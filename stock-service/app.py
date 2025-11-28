import os
from contextlib import contextmanager
from typing import List

import mysql.connector
from fastapi import FastAPI, HTTPException, status
from mysql.connector.errors import Error as MySQLError
from pydantic import BaseModel

app = FastAPI(title="Stock Service API")

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


class OrderItems(BaseModel):
    order_items: List[OrderItem]


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
        with conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM stock")
                return cursor.fetchall()
            except MySQLError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get current stock: {str(e)}",
                )


def get_item_stock(item_id):
    """Retrieve the current stock quantity for a specific item."""
    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM stock WHERE item_id = %s", (item_id,))
                return cursor.fetchone()
            except MySQLError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get stock for item {item_id}: {str(e)}",
                )


def batch_update_stock(items, operation="add"):
    """Update stock quantities for multiple items in a single transaction. operation can be 'add' or 'remove'."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                # If adding stock, validate against max_quantity
                if operation == "add":
                    for item in items:
                        cursor.execute(
                            "SELECT quantity, max_quantity, item_name FROM stock WHERE item_id = %s",
                            (item.item_id,),
                        )
                        result = cursor.fetchone()
                        if not result:
                            conn.rollback()
                            return {
                                "error": f"Item with ID={item.item_id} not found"
                            }, status.HTTP_404_NOT_FOUND
                        current_qty, max_qty, item_name = result
                        new_qty = current_qty + item.quantity
                        if new_qty > max_qty:
                            conn.rollback()
                            return {
                                "error": f"Adding {item.quantity} units to {item_name} would exceed maximum capacity ({max_qty}). Current: {current_qty}"
                            }, status.HTTP_400_BAD_REQUEST

                query = """
                    UPDATE stock 
                    SET quantity = quantity {} %s 
                    WHERE item_id = %s
                """.format("+" if operation == "add" else "-")

                cursor.executemany(
                    query, [(item.quantity, item.item_id) for item in items]
                )
                conn.commit()
                return {"message": "Stock updated successfully"}, status.HTTP_200_OK
            except MySQLError as err:
                conn.rollback()
                return {"error": str(err)}, status.HTTP_500_INTERNAL_SERVER_ERROR


def validate_stock(items):
    """Validate if requested stock operations are possible."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:  # Use cursor context manager
            try:
                for item in items:
                    cursor.execute(
                        "SELECT quantity, item_name, max_quantity FROM stock WHERE item_id = %s",
                        (item.item_id,),
                    )
                    result = cursor.fetchone()
                    if not result:
                        return False, f"Item with ID={item.item_id} not found"
                    elif result[0] - item.quantity < 0:
                        return False, f"Insufficient stock for item {result[1]}"
                    else:
                        return True, "Items currently in stock"
            except MySQLError as err:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
                )


@app.post("/add_stock", response_model=dict)
async def add_stock(items: OrderItems):
    """
    Add stock quantities for multiple items.
    Validates that new quantity does not exceed max_quantity.
    """
    result, status_code = batch_update_stock(items.order_items, operation="add")
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=result["error"])
    return {"message": "Stock updated"}


@app.post("/remove_stock", response_model=dict)
async def remove_stock(request: OrderItems):
    """
    Remove stock quantities for multiple items.
    """
    validation_status, message = validate_stock(request.order_items)
    if not validation_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    result, status_code = batch_update_stock(request.order_items, operation="remove")
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=result["error"])
    return {"message": "Stock updated"}


@app.post("/validate_stock", response_model=dict)
async def validate_stock_operation(request: OrderItems):
    """
    Validate if stock operations are possible for multiple items.
    """
    validation_status, message = validate_stock(request.order_items)
    return {"status": validation_status, "message": message}


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return stock


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5003)
