import os
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import List

import mysql.connector
from celery import Celery
from fastapi import FastAPI, HTTPException, status
from mysql.connector.errors import Error as MySQLError
from pydantic import BaseModel

app = FastAPI(title="Order Service API")
celery = Celery(os.getenv("TASK_QUEUE_NAME"), broker=os.getenv("TASK_QUEUE_BROKER_URL"))

# MySQL configuration
db_config = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
}


class OrderItem(BaseModel):
    item_id: int
    quantity: int


class CreateOrderRequest(BaseModel):
    customer_name: str
    customer_distance: float
    items: List[OrderItem]


class UpdateOrderRequest(BaseModel):
    order_id: str
    message: str


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


def update_order_with_items(order, items):
    """Insert a new order and its items in a single transaction."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                # Insert order
                cursor.execute(
                    """INSERT INTO orders 
                    (id, order_time, customer_name, customer_distance, order_status, response_msg) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        order["id"],
                        order["order_time"],
                        order["customer_name"],
                        order["customer_distance"],
                        order["order_status"],
                        "Order created",
                    ),
                )

                # Insert order items
                values = [(order["id"], item.item_id, item.quantity) for item in items]
                cursor.executemany(
                    "INSERT INTO order_items (order_id, item_id, quantity) VALUES (%s, %s, %s)",
                    values,
                )

                conn.commit()
            except MySQLError as e:
                conn.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create order with items: {str(e)}",
                )


def update_order(order):
    """Insert a new order into the orders table."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    """INSERT INTO orders 
                    (id, order_time, customer_name, customer_distance, order_status) 
                    VALUES (%s, %s, %s, %s, %s)""",
                    (
                        order["id"],
                        order["order_time"],
                        order["customer_name"],
                        order["customer_distance"],
                        order["order_status"],
                    ),
                )
                conn.commit()
            except MySQLError as e:
                conn.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create order: {str(e)}",
                )


def update_order_items(order_id, items: List[OrderItem]):
    """
    Insert order items into the order_items table.

    Args:
        order_id (str): Unique identifier for the order
        items (List[OrderItem]): List of OrderItem objects
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                values = [(order_id, item.item_id, item.quantity) for item in items]
                cursor.executemany(
                    "INSERT INTO order_items (order_id, item_id, quantity) VALUES (%s, %s, %s)",
                    values,
                )
                conn.commit()
            except MySQLError as e:
                conn.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create order items: {str(e)}",
                )


def update_status_of_an_order(order_id, order_status, response_msg=None):
    """
    Update the order_status of an existing order.

    Args:
        order_id (str): Unique identifier for the order'
        order_status (str): 'completed' or 'cancelled'
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                if order_status == "completed":
                    delivered_at = datetime.now().isoformat()
                    if response_msg:
                        cursor.execute(
                            "UPDATE orders SET order_status = %s, delivered_at = %s, response_msg = %s WHERE id = %s",
                            (order_status, delivered_at, response_msg, order_id),
                        )
                    else:
                        cursor.execute(
                            "UPDATE orders SET order_status = %s, delivered_at = %s WHERE id = %s",
                            (order_status, delivered_at, order_id),
                        )
                else:
                    if response_msg:
                        cursor.execute(
                            "UPDATE orders SET order_status = %s, response_msg = %s WHERE id = %s",
                            (order_status, response_msg, order_id),
                        )
                    else:
                        cursor.execute(
                            "UPDATE orders SET order_status = %s WHERE id = %s",
                            (order_status, order_id),
                        )
                if cursor.rowcount == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
                    )
                conn.commit()
            except MySQLError as e:
                conn.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update order status: {str(e)}",
                )


def update_msg_of_an_order(order_id, response_msg):
    """
    Update the response message of an existing order.

    Args:
        order_id (str): Unique identifier for the order
        response_msg (str): Response message to be updated
    """
    if not response_msg or not isinstance(response_msg, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message must be a non-empty string",
        )

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    "UPDATE orders SET response_msg = %s WHERE id = %s",
                    (response_msg, order_id),
                )
                if cursor.rowcount == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
                    )
                conn.commit()
            except MySQLError as e:
                conn.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update order message: {str(e)}",
                )


def get_all_orders(order_type="All"):
    """
    Retrieve orders based on their type.

    Args:
        order_type (str): Filter for orders ('active', 'completed', or 'All')

    Returns:
        list: List of order dictionaries
    """
    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            try:
                cursor = conn.cursor(dictionary=True)
                if order_type == "active":
                    query = "SELECT * FROM orders WHERE order_status = 'active';"
                elif order_type == "completed":
                    query = "SELECT * FROM orders WHERE order_status = 'completed';"
                else:
                    query = "SELECT * FROM orders;"
                cursor.execute(query)
                return cursor.fetchall()
            except MySQLError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve orders: {str(e)}",
                )


def get_order_details(order_id):
    """
    Get detailed information about a specific order including its items.

    Args:
        order_id (str): Unique identifier for the order

    Returns:
        dict: Order details with items or None if not found
    """
    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
                order_details = cursor.fetchone()
                if not order_details:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
                    )

                get_items_query = """SELECT oi.item_id, s.item_name, oi.quantity 
                                    FROM order_items oi
                                    JOIN stock s ON oi.item_id = s.item_id
                                    WHERE order_id = %s"""
                cursor.execute(get_items_query, (order_id,))
                items = cursor.fetchall()
                order_details["items"] = items
                return order_details
            except MySQLError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve order details: {str(e)}",
                )


@app.post("/create_order", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_order(order_request: CreateOrderRequest):
    """Create a new order and assign delivery."""
    if not order_request.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item",
        )

    if order_request.customer_distance <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer distance must be greater than 0",
        )
    order_id = uuid.uuid4().hex
    order_id = order_id[-8:]
    order = {
        "id": order_id,
        "order_time": datetime.now().isoformat(),
        "customer_name": order_request.customer_name,
        "customer_distance": order_request.customer_distance,
        "order_status": "active",
        "items": order_request.items,
        "response_msg": "Order taken",
    }
    update_order_with_items(order, order_request.items)

    # Convert Pydantic models to dictionaries for Celery serialization
    serializable_items = [item.dict() for item in order_request.items]

    # Queue the process_order task
    task = celery.send_task(
        "process_order",
        args=[order["id"], order["customer_distance"], serializable_items],
    )
    return {"order_id": order["id"], "task_id": task.id}


@app.post("/close_order", response_model=dict)
async def close_order(request: UpdateOrderRequest):
    """Mark an order as closed."""
    update_status_of_an_order(request.order_id, "completed", request.message)
    return {"order_status": "Order delivered"}


@app.post("/cancel_order", response_model=dict)
async def cancel_order(request: UpdateOrderRequest):
    """Cancel an order."""
    update_status_of_an_order(request.order_id, "cancelled", request.message)
    return {"order_status": "Order cancelled"}


@app.post("/update_msg", response_model=dict)
async def update_msg(request: UpdateOrderRequest):
    """Update message for an order."""
    update_msg_of_an_order(request.order_id, request.message)
    return {"order_status": "Order message updated"}


@app.get("/orders")
async def get_orders():
    """Retrieve all orders."""
    return get_all_orders()


@app.get("/orders/active")
async def get_active_orders():
    """Retrieve all active orders."""
    return get_all_orders("active")


@app.get("/orders/completed")
async def get_completed_orders():
    """Retrieve all completed orders."""
    return get_all_orders("completed")


@app.get("/order/{order_id}")
async def get_order(order_id: str):
    """Retrieve details of a specific order."""
    return get_order_details(order_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5001)
