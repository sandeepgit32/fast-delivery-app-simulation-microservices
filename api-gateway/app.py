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

ORDER_SERVICE_URL = "http://order-service:5001"
DELIVERY_SERVICE_URL = "http://delivery-service:5002"
STOCK_SERVICE_URL = "http://stock-service:5003"


@app.route("/")
def index():
    return "API Gateway is running"


# Order endpoints
@app.route("/orders", methods=["GET"])
def get_orders():
    response = requests.get(f"{ORDER_SERVICE_URL}/orders")
    return jsonify(response.json()), response.status_code


@app.route("/orders/active", methods=["GET"])
def get_active_orders():
    response = requests.get(f"{ORDER_SERVICE_URL}/orders/active")
    return jsonify(response.json()), response.status_code


@app.route("/orders/completed", methods=["GET"])
def get_completed_orders():
    response = requests.get(f"{ORDER_SERVICE_URL}/orders/completed")
    return jsonify(response.json()), response.status_code


@app.route("/order/<order_id>", methods=["GET"])
def get_order(order_id):
    response = requests.get(f"{ORDER_SERVICE_URL}/order/{order_id}")
    return jsonify(response.json()), response.status_code


@app.route("/create_order", methods=["POST"])
def create_order():
    response = requests.post(f"{ORDER_SERVICE_URL}/create_order", json=request.json)
    return jsonify(response.json()), response.status_code


@app.route("/close_order/<order_id>", methods=["POST"])
def close_order(order_id):
    response = requests.post(f"{ORDER_SERVICE_URL}/close_order/{order_id}")
    return jsonify(response.json()), response.status_code


@app.route("/cancel_order/<order_id>", methods=["POST"])
def cancel_order(order_id):
    message = request.json.get("message")
    response = requests.post(
        f"{ORDER_SERVICE_URL}/cancel_order/{order_id}", json={"message": message}
    )
    return jsonify(response.json()), response.status_code


@app.route("/update_msg/<order_id>", methods=["POST"])
def update_msg(order_id):
    message = request.json.get("message")
    response = requests.post(
        f"{ORDER_SERVICE_URL}/update_msg/{order_id}", json={"message": message}
    )
    return jsonify(response.json()), response.status_code


# Delivery endpoints
@app.route("/delivery_persons", methods=["GET"])
def get_delivery_persons():
    response = requests.get(f"{DELIVERY_SERVICE_URL}/delivery_persons")
    return jsonify(response.json()), response.status_code


@app.route("/delivery_persons/en_route", methods=["GET"])
def get_en_route_persons():
    response = requests.get(f"{DELIVERY_SERVICE_URL}/delivery_persons/en_route")
    return jsonify(response.json()), response.status_code


@app.route("/delivery_persons/idle", methods=["GET"])
def get_idle_persons():
    response = requests.get(f"{DELIVERY_SERVICE_URL}/delivery_persons/idle")
    return jsonify(response.json()), response.status_code


@app.route("/delivery_persons/<person_id>", methods=["GET"])
def get_delivery_person(person_id):
    response = requests.get(f"{DELIVERY_SERVICE_URL}/delivery_persons/{person_id}")
    return jsonify(response.json()), response.status_code


@app.route("/deliveries", methods=["GET"])
def get_deliveries():
    response = requests.get(f"{DELIVERY_SERVICE_URL}/deliveries")
    return jsonify(response.json()), response.status_code


@app.route("/deliveries/active", methods=["GET"])
def get_active_deliveries():
    response = requests.get(f"{DELIVERY_SERVICE_URL}/deliveries/active")
    return jsonify(response.json()), response.status_code


@app.route("/deliveries/completed", methods=["GET"])
def get_completed_deliveries():
    response = requests.get(f"{DELIVERY_SERVICE_URL}/deliveries/completed")
    return jsonify(response.json()), response.status_code


@app.route("/deliveries/<delivery_id>", methods=["GET"])
def get_delivery(delivery_id):
    response = requests.get(f"{DELIVERY_SERVICE_URL}/deliveries/{delivery_id}")
    return jsonify(response.json()), response.status_code


@app.route("/assign_delivery", methods=["POST"])
def assign_delivery():
    response = requests.post(
        f"{DELIVERY_SERVICE_URL}/assign_delivery", json=request.json
    )
    return jsonify(response.json()), response.status_code


@app.route("/update_delivery_person_status/<person_id>", methods=["POST"])
def update_delivery_person_status(person_id):
    # Transform the request to include person_id in the body
    request_data = request.json if request.json else {}
    request_data['person_id'] = int(person_id)
    response = requests.post(
        f"{DELIVERY_SERVICE_URL}/update_delivery_person_status",
        json=request_data,
    )
    return jsonify(response.json()), response.status_code


# Stock endpoints
@app.route("/current_stock", methods=["GET"])
def get_current_stock():
    response = requests.get(f"{STOCK_SERVICE_URL}/current_stock")
    return jsonify(response.json()), response.status_code


@app.route("/current_stock/<item_id>", methods=["GET"])
def get_item_stock(item_id):
    response = requests.get(f"{STOCK_SERVICE_URL}/current_stock/{item_id}")
    return jsonify(response.json()), response.status_code


@app.route("/add_stock", methods=["POST"])
def add_stock():
    response = requests.post(f"{STOCK_SERVICE_URL}/add_stock", json=request.json)
    return jsonify(response.json()), response.status_code


@app.route("/remove_stock", methods=["POST"])
def remove_stock():
    response = requests.post(f"{STOCK_SERVICE_URL}/remove_stock", json=request.json)
    return jsonify(response.json()), response.status_code


@app.route("/validate_stock", methods=["POST"])
def validate_stock():
    response = requests.post(f"{STOCK_SERVICE_URL}/validate_stock", json=request.json)
    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
