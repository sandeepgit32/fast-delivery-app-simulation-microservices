import random
from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)


# MySQL configuration
db_config = {
    "user": "root",
    "password": "password",
    "host": "mysql",
    "database": "food_delivery",
}


def get_delivery_personnel(person_status="All"):
    if person_status == "idle":
        query = "SELECT * FROM delivery_persons WHERE status = 'idle';"
    elif person_status == "en_route":
        query = "SELECT * FROM delivery_persons WHERE status = 'en route';"
    else:
        query = "SELECT * FROM delivery_persons;"
    query = "SELECT * FROM delivery_persons;"
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    delivery_persons = cursor.fetchall()
    cursor.close()
    conn.close()
    result = []
    for id, name, phone_num, status in delivery_persons:
        result.append(
            {"id": id, "name": name, "phone_num": phone_num, "status": status}
        )
    return result


def get_list_of_deliveries(delivery_type="All"):
    if delivery_type == "active":
        query = "SELECT * FROM deliveries WHERE status = 'active';"
    elif delivery_type == "completed":
        query = "SELECT * FROM deliveries WHERE status = 'completed';"
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
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM delivery_persons WHERE id = %s", (person_id,))
    person = cursor.fetchone()
    cursor.close()
    conn.close()
    return person


def update_delivery_person_status(person_id, status):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE delivery_persons SET status = %s WHERE id = %s", (status, person_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def fetch_delivery(delivery_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM deliveries WHERE id = %s", (delivery_id,))
    delivery = cursor.fetchone()
    cursor.close()
    conn.close()
    return delivery


def create_delivery_record(order_id, delivery_person_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO deliveries (order_id, delivery_person_id, status, created_at) VALUES (%s, %s, %s, %s)",
        (order_id, delivery_person_id, "active", datetime.now()),
    )
    delivery_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return delivery_id


def close_delivery_record(delivery_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE deliveries SET status = 'completed', completed_at = %s WHERE id = %s",
        (datetime.now(), delivery_id),
    )
    conn.commit()


#TODO: Implement the process_delivery function in simulation service
def process_delivery(delivery_id):
    # It has to pass the delivery id to the message queue to simulate the delivery
    # Based on the delivery id it figures out the order id and the distance fo the customer
    # It then simulates the delivery by sleeping for the time it would take to deliver the order
    # Once the delivery is done, it updates the delivery status to completed in the database
    # and makes the delivery person `idle` again only after twice the time is taken to deliver the order
    # because the delivery person needs to get back to the restaurant
    # The stock is updated when the delivery person is assigned the order
    pass


@app.route("/delivery_persons", methods=["GET"])
def get_delivery_personnel_list():
    personnel = get_delivery_personnel()
    return jsonify(personnel), 200


@app.route("/delivery_persons/en_route", methods=["GET"])
def get_delivery_personnel_list_en_route():
    personnel = get_delivery_personnel(person_status="en_route")
    return jsonify(personnel), 200


@app.route("/delivery_persons/idle", methods=["GET"])
def get_idle_delivery_personnel_list():
    personnel = get_delivery_personnel(person_status="idle")
    return jsonify(personnel), 200


@app.route("/delivery_persons/<person_id>", methods=["GET"])
def get_delivery_person(person_id):
    person = fetch_delivery_person(person_id)
    if person:
        return jsonify(person), 200
    return jsonify({"error": "Delivery person not found"}), 404


@app.route("/deliveries", methods=["GET"])
def get_all_deliveries():
    deliveries = get_list_of_deliveries()
    return jsonify(deliveries), 200


@app.route("/deliveries/active", methods=["GET"])
def get_active_deliveries():
    deliveries = get_list_of_deliveries(delivery_type="active")
    return jsonify(deliveries), 200


@app.route("/deliveries/completed", methods=["GET"])
def get_completed_deliveries():
    deliveries = get_list_of_deliveries(delivery_type="completed")
    return jsonify(deliveries), 200


@app.route("/deliveries/<delivery_id>", methods=["GET"])
def get_delivery(delivery_id):
    delivery = fetch_delivery(delivery_id)
    if delivery:
        return jsonify(delivery), 200
    return jsonify({"error": "Delivery not found"}), 404


@app.route("/assign_delivery", methods=["POST"])
def assign_delivery():
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


if __name__ == "__main__":
    app.run(debug=True, port=5002)
