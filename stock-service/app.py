from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List
import mysql.connector
from mysql.connector.errors import Error as MySQLError
import random
from contextlib import contextmanager

app = FastAPI(title="Stock Service API")

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


class OrderItems(BaseModel):
    order_items: List[OrderItem]


class StockResponse(BaseModel):
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


def get_current_stock():
    """Retrieve all items and their current stock quantities."""
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM stock")
            return cursor.fetchall()
        finally:
            cursor.close()


def get_item_stock(item_id):
    """Retrieve the current stock quantity for a specific item."""
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM stock WHERE item_id = %s", (item_id,))
            return cursor.fetchone()
        finally:
            cursor.close()


def batch_update_stock(items, operation="add"):
    """Update stock quantities for multiple items in a single transaction."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            query = """
                UPDATE stock 
                SET quantity = quantity {} %s 
                WHERE item_id = %s
            """.format(
                "+" if operation == "add" else "-"
            )

            cursor.executemany(query, [(item.quantity, item.item_id) for item in items])
            conn.commit()
            return {"message": "Stock updated successfully"}, 200
        except MySQLError as err:
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
            )
        finally:
            cursor.close()


def validate_stock(items):
    """Validate if requested stock operations are possible."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            for item in items:
                cursor.execute(
                    "SELECT quantity FROM stock WHERE item_id = %s", (item.item_id,)
                )
                result = cursor.fetchone()
                if not result:
                    return False, f"Item {item.item_id} not found"
                if result[0] - item.quantity < 0:
                    return False, f"Insufficient stock for item {item.item_id}"
            return True, None
        finally:
            cursor.close()


@app.post("/add_stock", response_model=StockResponse)
async def add_stock(items: OrderItems):
    """
    Add stock quantities for multiple items.
    """
    result, status_code = batch_update_stock(items.order_items, operation="add")
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=result["error"])
    return {"message": "Stock updated"}


@app.post("/remove_stock", response_model=StockResponse)
async def remove_stock(items: OrderItems):
    """
    Remove stock quantities for multiple items.
    """
    status, message = validate_stock(items.order_items)
    if not status:
        raise HTTPException(status_code=400, detail=message)
    result, status_code = batch_update_stock(items.order_items, operation="remove")
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=result["error"])
    return {"message": "Stock updated"}


@app.get("/current_stock")
async def current_stock():
    """
    Get current stock levels for all items.
    """
    stock = get_current_stock()
    return stock


@app.get("/current_stock/{item_id}")
async def item_stock(item_id: int):
    """
    Get current stock level for a specific item.
    """
    stock = get_item_stock(item_id)
    if stock is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return stock


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5003)
