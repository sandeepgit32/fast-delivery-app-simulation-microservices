from datetime import datetime
import json
import uuid

import requests
import mysql.connector
from flask import Flask, jsonify, request

app = Flask(__name__)

# MySQL database configuration for food delivery system
db_config = {
    "user": "root",
    "password": "password",
    "host": "mysql",
    "database": "food_delivery",
}


def update_order(order):
    """
    Insert a new order into the orders table.

    Args:
        order (dict): Order details including id, order_time, customer_name, customer_distance, and order_status
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (id, order_time, customer_name,  customer_distance, order_status) VALUES (%s, %s, %s, %s, %s, %s)",
        (
            order["id"],
            order["order_time"],
            order["customer_name"],
            order["customer_distance"],
            order["order_status"],
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()


def update_order_items(order_id, items):
    """
    Insert order items into the order_items table.

    Args:
        order_id (str): Unique identifier for the order
        items (dict): Dictionary of item_id and quantity pairs
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    values = [(order_id, item_id, quantity) for item_id, quantity in items.items()]
    cursor.executemany(
        "INSERT INTO order_items (order_id, item_id, quantity) VALUES (%s, %s, %s)",
        values,
    )
    conn.commit()
    cursor.close()
    conn.close()


def update_status_of_an_order(order_id, order_status):
    """
    Update the order_status of an existing order.

    Args:
        order_id (str): Unique identifier for the order
        order_status (str): New order_status to be set
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE orders SET order_status = %s WHERE id = %s", (order_status, order_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_all_orders(order_type="All"):
    """
    Retrieve orders based on their type.

    Args:
        order_type (str): Filter for orders ('active', 'completed', or 'All')

    Returns:
        list: List of order dictionaries
    """
    if order_type == "active":
        query = "SELECT * FROM orders WHERE order_status = 'active';"
    elif order_type == "completed":
        query = "SELECT * FROM orders WHERE order_status = 'completed';"
    else:
        query = "SELECT * FROM orders;"
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return orders


def get_order_details(order_id):
    """
    Get detailed information about a specific order including its items.

    Args:
        order_id (str): Unique identifier for the order

    Returns:
        dict: Order details with items or None if not found
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order_details = cursor.fetchone()
    if not order_details:
        return None
    get_items_query = """SELECT oi.item_id, s.item_name, oi.quantity FROM order_items oi
    JOIN stock s ON oi.item_id = s.item_id
    WHERE order_id = %s"""
    cursor.execute(get_items_query, (order_id,))
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    order_details["items"] = items
    return order_details


def process_order(order_id, customer_distance):
    """
    Process an order by requesting delivery assignment.

    Args:
        order_id (str): Unique identifier for the order
        customer_distance (float): Distance to customer location

    Returns:
        str: Status message indicating success or failure
    """
    print("Order ID: ", order_id)
    print("Customer Distance: ", customer_distance)
    return "Delivery person assigned"
    # request_data = {
    #     "order_id": order_id,
    #     "customer_distance": customer_distance
    # }
    # response = requests.post("http://delivery-service:5002/assign_delivery", json=request_data)
    # if "error" in response.json():
    #     update_status_of_an_order(order_id, "failed")
    #     return response.json()["error"]
    # else:
    #     return "Delivery person assigned"


# API Endpoints


@app.route("/create_order", methods=["POST"])
def create_order():
    """
    API endpoint to create a new order and assign delivery.

    Query Parameters:
        customer_name (str): Name of the customer
        customer_distance (float): Distance to customer location
        items (dict): Dictionary of items and quantities
    """
    customer_name = request.args.get("customer_name")
    customer_distance = request.args.get("customer_distance", type=float)
    order_items = request.args.get("items")
    order_items = json.loads(order_items)
    order = {
        "id": uuid.uuid4().hex,
        "order_time": datetime.now().isoformat(),
        "customer_name": customer_name,
        "customer_distance": customer_distance,
        "order_status": "active",
        "items": order_items,
    }
    update_order(order)
    update_order_items(order["id"], order_items)
    message = process_order(order["id"], customer_distance)
    order["message"] = message
    if message == "Delivery person assigned":
        return jsonify(order), 201
    else:
        return jsonify({"error": message}), 400


@app.route("/close_order/<order_id>", methods=["POST"])
def close_order(order_id):
    """
    API endpoint to mark an order as closed.

    Parameters:
        order_id (str): Unique identifier for the order
    """
    update_status_of_an_order(order_id, "closed")
    return jsonify({"order_status": "Order completed"}), 200


@app.route("/orders", methods=["GET"])
def get_orders():
    """API endpoint to retrieve all orders."""
    orders = get_all_orders()
    return jsonify(orders), 200


@app.route("/orders/active", methods=["GET"])
def get_active_orders():
    """API endpoint to retrieve all active orders."""
    active_orders = get_all_orders("active")
    return jsonify(active_orders), 200


@app.route("/orders/completed", methods=["GET"])
def get_completed_orders():
    """API endpoint to retrieve all completed orders."""
    completed_orders = get_all_orders("completed")
    return jsonify(completed_orders), 200


@app.route("/order/<order_id>", methods=["GET"])
def get_order(order_id):
    """
    API endpoint to retrieve details of a specific order.

    Parameters:
        order_id (str): Unique identifier for the order
    """
    order_details = get_order_details(order_id)
    if order_details:
        return jsonify(order_details), 200
    return jsonify({"error": "Order not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5001)
