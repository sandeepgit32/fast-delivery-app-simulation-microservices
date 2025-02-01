from datetime import datetime
import random
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import mysql.connector
from mysql.connector.errors import Error as MySQLError
from contextlib import contextmanager


app = FastAPI(title="Delivery Service API")

# MySQL configuration
db_config = {
    "user": "root",
    "password": "password",
    "host": "db",
    "database": "food_delivery",
}


class DeliveryPerson(BaseModel):
    id: int
    name: str
    person_status: str
    current_location: Optional[str] = None


class Delivery(BaseModel):
    id: int
    order_id: str
    delivery_person_id: int
    delivery_status: str
    created_at: datetime
    completed_at: Optional[datetime] = None


class AssignDeliveryRequest(BaseModel):
    order_id: str
    customer_distance: float


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        yield conn
    except MySQLError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}",
        )
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_delivery_personnel(person_status="all"):
    """
    Fetch delivery personnel from database based on their status
    Args:
        person_status (str): Filter personnel by status ('idle', 'en_route', or 'all')
    Returns:
        list: List of delivery personnel matching the status criteria
    """
    if person_status == "idle":
        query = "SELECT * FROM delivery_persons WHERE person_status = 'idle';"
    elif person_status == "en_route":
        query = "SELECT * FROM delivery_persons WHERE person_status = 'en_route';"
    else:
        query = "SELECT * FROM delivery_persons;"

    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()


def get_list_of_deliveries(delivery_type="all"):
    """
    Retrieve deliveries from database based on their type
    Args:
        delivery_type (str): Filter deliveries by type ('active', 'completed', or 'all')
    Returns:
        list: List of deliveries matching the type criteria
    """
    if delivery_type == "active":
        query = "SELECT * FROM deliveries WHERE delivery_status = 'active';"
    elif delivery_type == "completed":
        query = "SELECT * FROM deliveries WHERE delivery_status = 'completed';"
    else:
        query = "SELECT * FROM deliveries;"

    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()


def fetch_delivery_person(person_id):
    """
    Retrieve specific delivery person by their ID
    Args:
        person_id: ID of the delivery person
    Returns:
        dict: Delivery person details or None if not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM delivery_persons WHERE id = %s", (person_id,))
            return cursor.fetchone()
        finally:
            cursor.close()


def update_delivery_person_status(person_id, status):
    """
    Update the status of a delivery person
    Args:
        person_id: ID of the delivery person
        person_status (str): New person_status to be set
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE delivery_persons SET person_status = %s WHERE id = %s",
                (status, person_id),
            )
            conn.commit()
        finally:
            cursor.close()


def fetch_delivery(delivery_id):
    """
    Retrieve specific delivery by its ID
    Args:
        delivery_id: ID of the delivery
    Returns:
        dict: Delivery details or None if not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM deliveries WHERE id = %s", (delivery_id,))
            return cursor.fetchone()
        finally:
            cursor.close()


def create_delivery_record(order_id, delivery_person_id):
    """
    Create a new delivery record in the database
    Args:
        order_id: ID of the order to be delivered
        delivery_person_id: ID of the assigned delivery person
    Returns:
        ID of the created delivery record
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO deliveries (order_id, delivery_person_id, delivery_status, created_at) VALUES (%s, %s, %s, %s)",
                (order_id, delivery_person_id, "active", datetime.now()),
            )
            delivery_id = cursor.lastrowid
            conn.commit()
            return delivery_id
        finally:
            cursor.close()


def close_delivery_record(delivery_id):
    """
    Mark a delivery as completed in the database
    Args:
        delivery_id: ID of the delivery to be completed
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE deliveries SET delivery_status = 'completed', completed_at = %s WHERE id = %s",
                (datetime.now(), delivery_id),
            )
            conn.commit()
        finally:
            cursor.close()


def process_delivery(delivery_id, delivery_person_id):
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
    import time

    print(f"Processing delivery {delivery_id}")
    update_delivery_person_status(delivery_person_id, "en_route")
    time.sleep(2 * 60)  # Simulating a 5-minute delivery
    print(f"Delivery {delivery_id} completed")
    close_delivery_record(delivery_id)
    update_delivery_person_status(delivery_person_id, "idle")


@app.get("/delivery_persons", response_model=List[DeliveryPerson])
async def get_delivery_personnel_list():
    """Get a list of all delivery personnel"""
    return get_delivery_personnel()


@app.get("/delivery_persons/en_route", response_model=List[DeliveryPerson])
async def get_delivery_personnel_list_en_route():
    """Get a list of delivery personnel who are currently delivering"""
    return get_delivery_personnel(person_status="en_route")


@app.get("/delivery_persons/idle", response_model=List[DeliveryPerson])
async def get_idle_delivery_personnel_list():
    """Get a list of available delivery personnel"""
    return get_delivery_personnel(person_status="idle")


@app.get("/delivery_persons/{person_id}", response_model=DeliveryPerson)
async def get_delivery_person(person_id: int):
    """Get details of a specific delivery person"""
    person = fetch_delivery_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Delivery person not found")
    return person


@app.get("/deliveries", response_model=List[Delivery])
async def get_all_deliveries():
    """Get a list of all deliveries"""
    return get_list_of_deliveries()


@app.get("/deliveries/active", response_model=List[Delivery])
async def get_active_deliveries():
    """Get a list of all ongoing deliveries"""
    return get_list_of_deliveries(delivery_type="active")


@app.get("/deliveries/completed", response_model=List[Delivery])
async def get_completed_deliveries():
    """Get a list of all completed deliveries"""
    return get_list_of_deliveries(delivery_type="completed")


@app.get("/deliveries/{delivery_id}", response_model=Delivery)
async def get_delivery(delivery_id: int):
    """Get details of a specific delivery"""
    delivery = fetch_delivery(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@app.post("/assign_delivery")
async def assign_delivery(request: AssignDeliveryRequest):
    """Assign a delivery to an available delivery person"""
    idle_persons = get_delivery_personnel(person_status="idle")
    if not idle_persons:
        raise HTTPException(status_code=400, detail="No delivery personnel available")

    delivery_person = random.choice(idle_persons)
    delivery_person_id = delivery_person["id"]
    delivery_id = create_delivery_record(request.order_id, delivery_person_id)
    process_delivery(delivery_id, request.customer_distance)
    return {"delivery_id": delivery_id, "delivery_person": delivery_person}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5002)
