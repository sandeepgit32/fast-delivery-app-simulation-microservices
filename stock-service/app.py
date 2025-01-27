from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import mysql.connector
import random

app = FastAPI(title="Stock Service API")

# MySQL configuration
db_config = {
    "user": "root",
    "password": "password",
    "host": "mysql",
    "database": "food_delivery",
}


class OrderItem(BaseModel):
    item_id: int
    quantity: int


class OrderItems(BaseModel):
    order_items: List[OrderItem]


class StockResponse(BaseModel):
    message: str


@app.on_event("startup")
def init_stock():
    """Initialize the stock database with random item quantities."""
    random_items = []
    for i in range(1, 20):
        random_items.append((f"item{i}", random.randint(50, 200)))
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO stock (item_name, quantity) VALUES (%s, %s)",
        random_items,
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_current_stock():
    """
    Retrieve all items and their current stock quantities from the database.

    Returns:
        list: List of dictionaries containing item details:
            - item_id (int): Unique identifier for the item
            - item_name (str): Name of the item
            - quantity (int): Current stock quantity
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock;")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def get_item_stock(item_id):
    """
    Retrieve the current stock quantity for a specific item.

    Args:
        item_id (str): Unique identifier of the item

    Returns:
        tuple: Item details (item_id, item_name, quantity) or None if item not found
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock WHERE item_id = %s", (item_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def batch_update_stock(items, operation="add"):
    """
    Update stock quantities for multiple items in a single transaction.

    Args:
        items (list): List of dictionaries containing:
            - item_id: Unique identifier of the item
            - quantity: Amount to add or remove
        operation (str): Either "add" or "remove" to increase or decrease stock

    Returns:
        tuple: (dict, int) containing response message and HTTP status code

    Raises:
        mysql.connector.Error: If database operation fails
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        # Prepare batch update query
        if operation == "add":
            query = """
                UPDATE stock 
                SET quantity = quantity + %s 
                WHERE item_id = %s
            """
        else:
            query = """
                UPDATE stock 
                SET quantity = quantity - %s 
                WHERE item_id = %s
            """
        # Execute batch update
        cursor.executemany(
            query, [(item["quantity"], item["item_id"]) for item in items]
        )
        conn.commit()
        return {"message": "Stock updated successfully"}, 200

    except mysql.connector.Error as err:
        return {"error": str(err)}, 400
    finally:
        cursor.close()
        conn.close()


def validate_stock(items):
    """
    Validate if requested stock operations are possible.

    Args:
        items (list): List of dictionaries containing:
            - item_id: Unique identifier of the item
            - quantity: Amount to validate

    Returns:
        tuple: (bool, str) containing:
            - bool: True if operation is valid, False otherwise
            - str: Error message if operation is invalid, None otherwise
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    for item in items:
        cursor.execute(
            "SELECT quantity FROM stock WHERE item_id = %s", (item["item_id"],)
        )
        result = cursor.fetchone()
        if not result:
            return False, f"Item {item['item_id']} not found"
        if result[0] - item["quantity"] < 0:
            return False, f"Insufficient stock for item {item['item_id']}"
    return True, None


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
