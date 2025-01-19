"""
Steps to run the tests:

1. Create a new virtual environment in the stock-service directory.
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


def test_get_current_stock(client, mock_db_connection):
    """Test get_current_stock endpoint"""
    mock_stock = [
        {"item_id": "id1", "item_name": "item1", "quantity": 100},
        {"item_id": "id2", "item_name": "item2", "quantity": 150},
    ]
    mock_db_connection.fetchall.return_value = mock_stock

    response = client.get("/current_stock")

    mock_db_connection.execute.assert_called_once_with("SELECT * FROM stock;")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert "item_id" in data[0]
    assert "quantity" in data[0]


def test_get_item_stock(client, mock_db_connection):
    """Test get_item_stock endpoint"""
    mock_item = ("id1", "item1", 100)
    mock_db_connection.fetchone.return_value = mock_item

    response = client.get("/current_stock/id1")

    mock_db_connection.execute.assert_called_once_with(
        "SELECT * FROM stock WHERE item_id = %s", ("id1",)
    )
    assert response.status_code == 200


def test_item_not_found(client, mock_db_connection):
    """Test get_item_stock with non-existent item"""
    mock_db_connection.fetchone.return_value = None

    response = client.get("/current_stock/999")

    assert response.status_code == 404
    assert json.loads(response.data)["error"] == "Item not found"


def test_add_stock(client, mock_db_connection):
    """Test add_stock endpoint"""
    test_data = {
        "order_items": [
            {"item_id": "1", "quantity": 10},
            {"item_id": "2", "quantity": 5},
        ]
    }

    response = client.post(
        "/add_stock", json=test_data, content_type="application/json"
    )

    assert response.status_code == 200
    assert json.loads(response.data)["message"] == "Stock updated"


def test_remove_stock_success(client, mock_db_connection):
    """Test remove_stock endpoint with sufficient stock"""
    test_data = {
        "order_items": [
            {"item_id": "1", "quantity": 5},
            {"item_id": "2", "quantity": 3},
        ]
    }
    # Mock sufficient stock
    mock_db_connection.fetchone.return_value = (100,)

    response = client.post(
        "/remove_stock", json=test_data, content_type="application/json"
    )

    assert response.status_code == 200
    assert json.loads(response.data)["message"] == "Stock updated"


def test_remove_stock_insufficient(client, mock_db_connection):
    """Test remove_stock endpoint with insufficient stock"""
    test_data = {
        "order_items": [
            {"item_id": "1", "quantity": 1000},
        ]
    }
    # Mock insufficient stock
    mock_db_connection.fetchone.return_value = (10,)

    response = client.post(
        "/remove_stock", json=test_data, content_type="application/json"
    )

    assert response.status_code == 400
    assert "Insufficient stock" in json.loads(response.data)["error"]


def test_remove_stock_item_not_found(client, mock_db_connection):
    """Test remove_stock endpoint with non-existent item"""
    test_data = {
        "order_items": [
            {"item_id": "999", "quantity": 5},
        ]
    }
    # Mock item not found
    mock_db_connection.fetchone.return_value = None

    response = client.post(
        "/remove_stock", json=test_data, content_type="application/json"
    )

    assert response.status_code == 400
    assert "not found" in json.loads(response.data)["error"]

