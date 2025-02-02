from contextlib import contextmanager
from typing import List

import mysql.connector
from celery import Celery
from fastapi import FastAPI, HTTPException, status
from mysql.connector.errors import Error as MySQLError
from pydantic import BaseModel

app = FastAPI(title="Delivery Service API")
celery = Celery("tasks", broker="redis://redis:6379/0")

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
    phone_number: str
    person_status: str


class Delivery(BaseModel):
    id: int
    order_id: str
    delivery_person_id: int


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
        with conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute(query)
                return cursor.fetchall()
            except MySQLError as e:
                conn.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve delivery persons: {str(e)}",
                )


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
        with conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute(query)
                return cursor.fetchall()
            except MySQLError as e:
                conn.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve deliveries: {str(e)}",
                )


def fetch_delivery_person(person_id):
    """
    Retrieve specific delivery person by their ID
    Args:
        person_id: ID of the delivery person
    Returns:
        dict: Delivery person details or None if not found
    """
    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT * FROM delivery_persons WHERE id = %s", (person_id,)
                )
                return cursor.fetchone()
            except MySQLError as e:
                conn.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve delivery person details: {str(e)}",
                )


def update_delivery_person_status(person_id, person_status):
    """
    Update the status of a delivery person
    Args:
        person_id: ID of the delivery person
        person_status (str): New person_status to be set
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    "UPDATE delivery_persons SET person_status = %s WHERE id = %s",
                    (person_status, person_id),
                )
                conn.commit()
            except MySQLError as e:
                conn.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update delivery person status: {str(e)}",
                )


def fetch_delivery(delivery_id):
    """
    Retrieve specific delivery by its ID
    Args:
        delivery_id: ID of the delivery
    Returns:
        dict: Delivery details or None if not found
    """
    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM deliveries WHERE id = %s", (delivery_id,))
                return cursor.fetchone()
            except MySQLError as e:
                conn.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve delivery details: {str(e)}",
                )


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
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO deliveries (order_id, delivery_person_id) VALUES (%s, %s)",
                    (order_id, delivery_person_id),
                )
                delivery_id = cursor.lastrowid
                conn.commit()
                return delivery_id
            except MySQLError as e:
                conn.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create delivery record: {str(e)}",
                )


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


@app.get("/deliveries/{delivery_id}", response_model=Delivery)
async def get_delivery(delivery_id: int):
    """Get details of a specific delivery"""
    delivery = fetch_delivery(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@app.post("/assign_delivery")
async def assign_delivery(request: AssignDeliveryRequest):
    """Queue the delivery simulation task"""
    task = celery.send_task("simulate_delivery", args=[request.order_id])
    return {"order_id": request.order_id, "task_id": task.id}


@app.post("/update_delivery_person_status/{person_id}")
async def update_delivery_person(person_id: int, person_status: str):
    """Update the status of a delivery person"""
    if person_status not in ["idle", "en_route"]:
        raise HTTPException(
            status_code=400, detail="Invalid status. Must be 'idle' or 'en_route'"
        )
    update_delivery_person_status(person_id, person_status)
    return {"message": "Delivery person status updated"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5002)
