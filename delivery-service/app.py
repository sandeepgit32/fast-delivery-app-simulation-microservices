import random
from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime

# Initialize Flask application
app = Flask(__name__)


# MySQL configuration
db_config = {
    "user": "root",
    "password": "password",
    "host": "mysql",
    "database": "food_delivery",
}


def get_delivery_personnel(person_status="All"):
    """
    Fetch delivery personnel from database based on their status
    Args:
        person_status (str): Filter personnel by status ('idle', 'en_route', or 'All')
    Returns:
        list: List of delivery personnel matching the status criteria
    """
    if person_status == "idle":
        query = "SELECT * FROM delivery_persons WHERE person_status = 'idle';"
    elif person_status == "en_route":
        query = "SELECT * FROM delivery_persons WHERE person_status = 'en route';"
    else:
        query = "SELECT * FROM delivery_persons;"
    query = "SELECT * FROM delivery_persons;"
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    delivery_persons = cursor.fetchall()
    cursor.close()
    conn.close()
    return delivery_persons


def get_list_of_deliveries(delivery_type="All"):
    """
    Retrieve deliveries from database based on their type
    Args:
        delivery_type (str): Filter deliveries by type ('active', 'completed', or 'All')
    Returns:
        list: List of deliveries matching the type criteria
    """
    if delivery_type == "active":
        query = "SELECT * FROM deliveries WHERE delivery_status = 'active';"
    elif delivery_type == "completed":
        query = "SELECT * FROM deliveries WHERE delivery_status = 'completed';"
    else:
        query = "SELECT * FROM deliveries;"
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    deliveries = cursor.fetchall()
    cursor.close()
    conn.close()
    return deliveries


def fetch_delivery_person(person_id):
    """
    Retrieve specific delivery person by their ID
    Args:
        person_id: ID of the delivery person
    Returns:
        dict: Delivery person details or None if not found
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM delivery_persons WHERE id = %s", (person_id,))
    person = cursor.fetchone()
    cursor.close()
    conn.close()
    return person


def update_delivery_person_status(person_id, status):
    """
    Update the status of a delivery person
    Args:
        person_id: ID of the delivery person
        person_status (str): New person_status to be set
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE delivery_persons SET person_status = %s WHERE id = %s",
        (status, person_id),
    )
    conn.commit()
    cursor.close()
    conn.close()


def fetch_delivery(delivery_id):
    """
    Retrieve specific delivery by its ID
    Args:
        delivery_id: ID of the delivery
    Returns:
        dict: Delivery details or None if not found
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM deliveries WHERE id = %s", (delivery_id,))
    delivery = cursor.fetchone()
    cursor.close()
    conn.close()
    return delivery


def create_delivery_record(order_id, delivery_person_id):
    """
    Create a new delivery record in the database
    Args:
        order_id: ID of the order to be delivered
        delivery_person_id: ID of the assigned delivery person
    Returns:
        ID of the created delivery record
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO deliveries (order_id, delivery_person_id, delivery_status, created_at) VALUES (%s, %s, %s, %s)",
        (order_id, delivery_person_id, "active", datetime.now()),
    )
    delivery_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return delivery_id


def close_delivery_record(delivery_id):
    """
    Mark a delivery as completed in the database
    Args:
        delivery_id: ID of the delivery to be completed
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE deliveries SET delivery_status = 'completed', completed_at = %s WHERE id = %s",
        (datetime.now(), delivery_id),
    )
    conn.commit()


def process_delivery(delivery_id):
    """
    Process the delivery simulation
    Args:
        delivery_id: ID of the delivery to be processed
    TODO: Implement this function in simulation service
    """
    # It has to pass the delivery id to the message queue to simulate the delivery
    # Based on the delivery id it figures out the order id and the distance fo the customer
    # It then simulates the delivery by sleeping for the time it would take to deliver the order
    # Once the delivery is done, it updates the delivery status to completed in the database
    # and makes the delivery person `idle` again only after twice the time is taken to deliver the order
    # because the delivery person needs to get back to the restaurant
    # The stock is updated when the delivery person is assigned the order
    print(f"Processing delivery {delivery_id}")
    pass


# API Routes


@app.route("/delivery_persons", methods=["GET"])
def get_delivery_personnel_list():
    """Get a list of all delivery personnel"""
    personnel = get_delivery_personnel()
    return jsonify(personnel), 200


@app.route("/delivery_persons/en_route", methods=["GET"])
def get_delivery_personnel_list_en_route():
    """Get a list of delivery personnel who are currently delivering"""
    personnel = get_delivery_personnel(person_status="en_route")
    return jsonify(personnel), 200


@app.route("/delivery_persons/idle", methods=["GET"])
def get_idle_delivery_personnel_list():
    """Get a list of available delivery personnel"""
    personnel = get_delivery_personnel(person_status="idle")
    return jsonify(personnel), 200


@app.route("/delivery_persons/<person_id>", methods=["GET"])
def get_delivery_person(person_id):
    """Get details of a specific delivery person by ID"""
    person = fetch_delivery_person(person_id)
    if person:
        return jsonify(person), 200
    return jsonify({"error": "Delivery person not found"}), 404


@app.route("/deliveries", methods=["GET"])
def get_all_deliveries():
    """Get a list of all deliveries in the system"""
    deliveries = get_list_of_deliveries()
    return jsonify(deliveries), 200


@app.route("/deliveries/active", methods=["GET"])
def get_active_deliveries():
    """Get a list of all ongoing deliveries"""
    deliveries = get_list_of_deliveries(delivery_type="active")
    return jsonify(deliveries), 200


@app.route("/deliveries/completed", methods=["GET"])
def get_completed_deliveries():
    """Get a list of all completed deliveries"""
    deliveries = get_list_of_deliveries(delivery_type="completed")
    return jsonify(deliveries), 200


@app.route("/deliveries/<delivery_id>", methods=["GET"])
def get_delivery(delivery_id):
    """Get details of a specific delivery by ID"""
    delivery = fetch_delivery(delivery_id)
    if delivery:
        return jsonify(delivery), 200
    return jsonify({"error": "Delivery not found"}), 404


@app.route("/assign_delivery", methods=["POST"])
def assign_delivery():
    """
    Assign a delivery to an available delivery person
    """
    order_id = request.args.get("order_id")
    customer_distance = request.args.get("customer_distance")
    idle_persons = get_delivery_personnel(person_status="idle")
    if not idle_persons:
        return jsonify({"error": "No delivery personnel available"}), 400
    else:
        # select one idle person in random
        delivery_person = random.choice(idle_persons)
        delivery_person_id = delivery_person["id"]
        delivery_id = create_delivery_record(order_id, delivery_person_id)
        process_delivery(delivery_id, customer_distance)
        update_delivery_person_status(delivery_person_id, "en route")
        return (
            jsonify({"delivery_id": delivery_id, "delivery_person": delivery_person}),
            200,
        )


# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True, port=5002)
