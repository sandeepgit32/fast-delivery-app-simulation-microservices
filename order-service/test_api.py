"""
Steps to run the tests:

1. Create a new virtual environment in the order-service directory.
   `python3 -m venv venv`

2. Activate the virtual environment.
    - Windows: `venv\\Scripts\\activate`
    - macOS/Linux: `source venv/bin/activate`

3. Install the required packages.
    `pip install -r requirements.txt`

4. Run the tests.
    `pytest -v test_api.py`
"""

import json
import pytest
from app import app
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Configure test client for Flask application"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_db_connection():
    """Mock MySQL database connection"""
    with patch("mysql.connector.connect") as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        yield mock_cursor


def test_create_order(client, mock_db_connection):
    """Test create_order endpoint"""
    test_data = {
        "customer_name": "Alice",
        "customer_distance": 5.0,
        "items": json.dumps({"item1": 2, "item2": 1}),
    }

    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = {
            "message": "Delivery person assigned"
        }

        response = client.post("/create_order", query_string=test_data)

        # Assert database calls
        mock_db_connection.execute.assert_called()
        mock_db_connection.executemany.assert_called_once()

        assert response.status_code == 201
        data = json.loads(response.data)
        assert "id" in data
        assert data["order_status"] == "active"
        assert "order_time" in data


def test_get_orders(client, mock_db_connection):
    """Test get_orders endpoint"""
    mock_orders = [
        {"id": "1", "order_time": "2023-01-01T12:00:00", "order_status": "active"},
        {"id": "2", "order_time": "2023-01-01T14:00:00", "order_status": "completed"},
    ]
    mock_db_connection.fetchall.return_value = mock_orders

    response = client.get("/orders")

    # Assert database calls
    mock_db_connection.execute.assert_called_once_with("SELECT * FROM orders;")
    mock_db_connection.fetchall.assert_called_once()

    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]["id"] == "1"


def test_get_order_details(client, mock_db_connection):
    """Test get_order_details endpoint"""
    # Mock database responses
    mock_order = {
        "id": "1",
        "order_time": "2023-01-01T12:00:00",
        "customer_distance": 5.0,
        "order_status": "active",
    }
    mock_items = [
        {"item_id": "item1", "item_name": "Pizza", "quantity": 2},
        {"item_id": "item2", "item_name": "Burger", "quantity": 1},
    ]

    mock_db_connection.fetchone.return_value = mock_order
    mock_db_connection.fetchall.return_value = mock_items

    # Make request
    response = client.get("/order/1")

    # Assert response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == "1"
    assert len(data["items"]) == 2


def test_close_order(client, mock_db_connection):
    """Test close_order endpoint"""
    response = client.post("/close_order/1")

    # Assert database calls
    mock_db_connection.execute.assert_called_once_with(
        "UPDATE orders SET order_status = %s WHERE id = %s", ("closed", "1")
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["order_status"] == "Order completed"


def test_get_active_orders(client, mock_db_connection):
    """Test get_active_orders endpoint"""
    # Mock database response
    mock_active_orders = [
        {"id": "1", "order_time": "2023-01-01T12:00:00", "order_status": "active"},
        {"id": "2", "order_time": "2023-01-01T13:00:00", "order_status": "active"},
    ]
    mock_db_connection.fetchall.return_value = mock_active_orders

    # Make request
    response = client.get("/orders/active")

    # Assert response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert all(order["order_status"] == "active" for order in data)


def test_order_not_found(client, mock_db_connection):
    """Test get_order_details with non-existent order"""
    # Mock database response for non-existent order
    mock_db_connection.fetchone.return_value = None

    # Make request
    response = client.get("/order/999")

    # Assert response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["error"] == "Order not found"
