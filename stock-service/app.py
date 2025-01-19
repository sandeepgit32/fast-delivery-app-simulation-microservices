from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL configuration
db_config = {
    "user": "root",
    "password": "password",
    "host": "mysql",
    "database": "food_delivery",
}


# TODO Move it to the simulation-service
def init_stock():
    """
    Initialize the stock database with random item quantities.
    Generates 19 items with random quantities between 50 and 200.
    This is a temporary function that should be moved to simulation-service.
    """
    # Initialize some random stock data if table is empty
    import random

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


@app.route("/add_stock", methods=["POST"])
def add_stock():
    """
    API endpoint to add stock quantities for multiple items.

    Expected JSON payload:
        {
            "order_items": [
                {"item_id": "...", "quantity": int}
            ]
        }

    Returns:
        tuple: JSON response and HTTP status code
    """
    data = request.get_json()
    order_items = data.get("order_items")
    batch_update_stock(order_items, operation="add")
    return jsonify({"message": "Stock updated"}), 200


@app.route("/remove_stock", methods=["POST"])
def remove_stock():
    """
    API endpoint to remove stock quantities for multiple items.
    Validates stock availability before removal.

    Expected JSON payload:
        {
            "order_items": [
                {"item_id": "...", "quantity": int}
            ]
        }

    Returns:
        tuple: JSON response and HTTP status code
    """
    data = request.get_json()
    order_items = data.get("order_items")
    status, message = validate_stock(order_items)
    if not status:
        return jsonify({"error": message}), 400
    batch_update_stock(order_items, operation="remove")
    return jsonify({"message": "Stock updated"}), 200


@app.route("/current_stock", methods=["GET"])
def current_stock():
    """
    API endpoint to get current stock levels for all items.

    Returns:
        tuple: JSON response containing list of all items and their stock levels,
               and HTTP status code
    """
    stock = get_current_stock()
    print("------------------>", stock)
    return jsonify(stock), 200


@app.route("/current_stock/<item_id>", methods=["GET"])
def item_stock(item_id):
    """
    API endpoint to get current stock level for a specific item.

    Args:
        item_id (str): Unique identifier of the item

    Returns:
        tuple: JSON response containing item details and HTTP status code,
               or error message if item not found
    """
    stock = get_item_stock(item_id)
    if stock is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(stock), 200


if __name__ == "__main__":
    init_stock()
    app.run(debug=True, port=5003)
