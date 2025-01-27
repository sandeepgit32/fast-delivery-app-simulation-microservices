from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests

app = Flask(__name__)
CORS(app)
limiter = Limiter(
    get_remote_address, app=app, default_limits=["1000 per day", "60 per hour"]
)

BACKEND_URLS = {
    "order_service": "http://order-service:5001",
    "delivery_service": "http://delivery-service:5002",
    "stock_service": "http://stock-service:5003",
}


@app.route("/")
def index():
    return "API Gateway is running"


# Order endpoints
@app.route("/orders", methods=["GET"])
def get_orders():
    response = requests.get(f"{BACKEND_URLS['order_service']}/orders")
    return jsonify(response.json()), response.status_code


@app.route("/orders/active", methods=["GET"])
def get_active_orders():
    response = requests.get(f"{BACKEND_URLS['order_service']}/orders/active")
    return jsonify(response.json()), response.status_code


@app.route("/orders/completed", methods=["GET"])
def get_completed_orders():
    response = requests.get(f"{BACKEND_URLS['order_service']}/orders/completed")
    return jsonify(response.json()), response.status_code


@app.route("/order/<order_id>", methods=["GET"])
def get_order(order_id):
    response = requests.get(f"{BACKEND_URLS['order_service']}/order/{order_id}")
    return jsonify(response.json()), response.status_code


@app.route("/create_order", methods=["POST"])
def create_order():
    response = requests.post(
        f"{BACKEND_URLS['order_service']}/create_order", json=request.json
    )
    return jsonify(response.json()), response.status_code


@app.route("/close_order/<order_id>", methods=["POST"])
def close_order(order_id):
    response = requests.post(f"{BACKEND_URLS['order_service']}/close_order/{order_id}")
    return jsonify(response.json()), response.status_code


# Delivery endpoints
@app.route("/delivery_persons", methods=["GET"])
def get_delivery_persons():
    response = requests.get(f"{BACKEND_URLS['delivery_service']}/delivery_persons")
    return jsonify(response.json()), response.status_code


@app.route("/delivery_persons/en_route", methods=["GET"])
def get_en_route_persons():
    response = requests.get(
        f"{BACKEND_URLS['delivery_service']}/delivery_persons/en_route"
    )
    return jsonify(response.json()), response.status_code


@app.route("/delivery_persons/idle", methods=["GET"])
def get_idle_persons():
    response = requests.get(f"{BACKEND_URLS['delivery_service']}/delivery_persons/idle")
    return jsonify(response.json()), response.status_code


@app.route("/delivery_persons/<person_id>", methods=["GET"])
def get_delivery_person(person_id):
    response = requests.get(
        f"{BACKEND_URLS['delivery_service']}/delivery_persons/{person_id}"
    )
    return jsonify(response.json()), response.status_code


@app.route("/deliveries", methods=["GET"])
def get_deliveries():
    response = requests.get(f"{BACKEND_URLS['delivery_service']}/deliveries")
    return jsonify(response.json()), response.status_code


@app.route("/deliveries/active", methods=["GET"])
def get_active_deliveries():
    response = requests.get(f"{BACKEND_URLS['delivery_service']}/deliveries/active")
    return jsonify(response.json()), response.status_code


@app.route("/deliveries/completed", methods=["GET"])
def get_completed_deliveries():
    response = requests.get(f"{BACKEND_URLS['delivery_service']}/deliveries/completed")
    return jsonify(response.json()), response.status_code


@app.route("/deliveries/<delivery_id>", methods=["GET"])
def get_delivery(delivery_id):
    response = requests.get(
        f"{BACKEND_URLS['delivery_service']}/deliveries/{delivery_id}"
    )
    return jsonify(response.json()), response.status_code


@app.route("/assign_delivery", methods=["POST"])
def assign_delivery():
    response = requests.post(
        f"{BACKEND_URLS['delivery_service']}/assign_delivery", json=request.json
    )
    return jsonify(response.json()), response.status_code


# Stock endpoints
@app.route("/current_stock", methods=["GET"])
def get_current_stock():
    response = requests.get(f"{BACKEND_URLS['stock_service']}/current_stock")
    return jsonify(response.json()), response.status_code


@app.route("/current_stock/<item_id>", methods=["GET"])
def get_item_stock(item_id):
    response = requests.get(f"{BACKEND_URLS['stock_service']}/current_stock/{item_id}")
    return jsonify(response.json()), response.status_code


@app.route("/add_stock", methods=["POST"])
def add_stock():
    response = requests.post(
        f"{BACKEND_URLS['stock_service']}/add_stock", json=request.json
    )
    return jsonify(response.json()), response.status_code


@app.route("/remove_stock", methods=["POST"])
def remove_stock():
    response = requests.post(
        f"{BACKEND_URLS['stock_service']}/remove_stock", json=request.json
    )
    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
