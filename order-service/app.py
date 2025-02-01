import uuid
from datetime import datetime
from typing import List, Optional

import httpx
import mysql.connector
from mysql.connector.errors import Error as MySQLError
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from contextlib import contextmanager

app = FastAPI(title="Order Service API")

# MySQL configuration
db_config = {
    "user": "root",
    "password": "password",
    "host": "db",
    "database": "food_delivery",
}


class OrderItem(BaseModel):
    item_id: int
    quantity: int


class CreateOrderRequest(BaseModel):
    customer_name: str
    customer_distance: float
    items: List[OrderItem]


class OrderResponse(BaseModel):
    id: str
    order_time: str
    customer_name: str
    customer_distance: float
    order_status: str
    items: List[OrderItem]
    message: Optional[str] = None


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


def update_order(order):
    """Insert a new order into the orders table."""
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()
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
        finally:
            cursor.close()


def update_order_items(order_id, items: List[OrderItem]):
    """
    Insert order items into the order_items table.

    Args:
        order_id (str): Unique identifier for the order
        items (List[OrderItem]): List of OrderItem objects
    """
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()
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
        finally:
            cursor.close()


def update_status_of_an_order(order_id, order_status):
    """
    Update the order_status of an existing order.

    Args:
        order_id (str): Unique identifier for the order
        order_status (str): New order_status to be set
    """
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()
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
        finally:
            cursor.close()


def get_all_orders(order_type="All"):
    """
    Retrieve orders based on their type.

    Args:
        order_type (str): Filter for orders ('active', 'completed', or 'All')

    Returns:
        list: List of order dictionaries
    """
    with get_db_connection() as conn:
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
        finally:
            cursor.close()


def get_order_details(order_id):
    """
    Get detailed information about a specific order including its items.

    Args:
        order_id (str): Unique identifier for the order

    Returns:
        dict: Order details with items or None if not found
    """
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor(dictionary=True)
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
        finally:
            cursor.close()


async def process_order(order_id, customer_distance):
    """Process an order by requesting delivery assignment."""
    try:
        async with httpx.AsyncClient(timeout=900.0) as client:
            response = await client.post(
                "http://delivery-service:5002/assign_delivery",
                json={"order_id": order_id, "customer_distance": customer_distance},
            )
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                await update_status_of_an_order(order_id, "failed")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=data["error"]
                )
            return "Delivery person assigned"

    except httpx.TimeoutException:
        await update_status_of_an_order(order_id, "failed")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Delivery service timeout",
        )

    except httpx.RequestError as e:
        await update_status_of_an_order(order_id, "failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Delivery service error: {str(e)}",
        )


@app.post(
    "/create_order", response_model=OrderResponse, status_code=status.HTTP_201_CREATED
)
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

    order = {
        "id": uuid.uuid4().hex,
        "order_time": datetime.now().isoformat(),
        "customer_name": order_request.customer_name,
        "customer_distance": order_request.customer_distance,
        "order_status": "active",
        "items": order_request.items,
    }

    update_order(order)
    update_order_items(order["id"], order_request.items)
    message = await process_order(order["id"], order_request.customer_distance)

    if message != "Delivery person assigned":
        raise HTTPException(status_code=400, detail=message)

    order["message"] = message
    return order


@app.post("/close_order/{order_id}", response_model=dict)
async def close_order(order_id: str):
    """Mark an order as closed."""
    update_status_of_an_order(order_id, "closed")
    return {"order_status": "Order completed"}


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
    order_details = get_order_details(order_id)
    if not order_details:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_details


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5001)
