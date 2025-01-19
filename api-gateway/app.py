from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests

app = Flask(__name__)
CORS(app)
limiter = Limiter(
    get_remote_address, app=app, default_limits=["200 per day", "50 per hour"]
)

BACKEND_URLS = {
    "order_service": "http://order-service:5001",
    "delivery_service": "http://delivery-service:5002",
    "stock_service": "http://stock-service:5003",
}


@app.route("/")
def index():
    return "API Gateway is running"


@app.route("/orders", methods=["POST", "GET"])
def orders():
    if request.method == "POST":
        response = requests.post(
            f"{BACKEND_URLS['order_service']}/orders", json=request.json
        )
    else:
        response = requests.get(f"{BACKEND_URLS['order_service']}/orders")
    return jsonify(response.json()), response.status_code


@app.route("/delivery-personnel", methods=["GET"])
def delivery_personnel():
    response = requests.get(f"{BACKEND_URLS['delivery_service']}/delivery-personnel")
    return jsonify(response.json()), response.status_code


@app.route("/assign-order", methods=["POST"])
def assign_order():
    response = requests.post(
        f"{BACKEND_URLS['delivery_service']}/assign-order", json=request.json
    )
    return jsonify(response.json()), response.status_code


@app.route("/stock", methods=["GET", "POST"])
def stock():
    if request.method == "POST":
        response = requests.post(
            f"{BACKEND_URLS['stock_service']}/update-stock", json=request.json
        )
    else:
        response = requests.get(f"{BACKEND_URLS['stock_service']}/stock")
    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    app.run(debug=True)
