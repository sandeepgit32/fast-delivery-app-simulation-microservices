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


def get_current_stocks():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock;")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    stocks = []
    for item_id, item_name, quantity in result:
        stocks.append(
            {"item_id": item_id, "item_name": item_name, "quantity": quantity}
        )
    return stocks


def get_item_stock(item_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock WHERE item_id = %s", (item_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def batch_update_stock(items, operation="add"):
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
    data = request.get_json()
    order_items = data.get("order_items")
    batch_update_stock(order_items, operation="add")
    return jsonify({"message": "Stock updated"}), 200


@app.route("/remove_stock", methods=["POST"])
def remove_stock():
    data = request.get_json()
    order_items = data.get("order_items")
    status, message = validate_stock(order_items)
    if not status:
        return jsonify({"error": message}), 400
    batch_update_stock(order_items, operation="remove")
    return jsonify({"message": "Stock updated"}), 200


@app.route("/current_stocks", methods=["GET"])
def get_current_stocks():
    stocks = get_current_stocks()
    return jsonify(stocks), 200


@app.route("/current_stocks/<item_id>", methods=["GET"])
def get_item_stock(item_id):
    stock = get_item_stock(item_id)
    if stock is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(stock), 200


if __name__ == "__main__":
    init_stock()
    app.run(debug=True, port=5003)
