"""
Steps to run the tests:

1. Create a new virtual environment in the delivery-service directory.
   `python3 -m venv venv`

2. Activate the virtual environment.
    - Windows: `venv\\Scripts\\activate`
    - macOS/Linux: `source venv/bin/activate`

3. Install the required packages.
    `pip install -r requirements.txt`

4. Run the tests.
    `pytest -v test_api.py`
"""

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


def test_get_delivery_personnel(client, mock_db_connection):
    """Test get_delivery_personnel endpoint"""
    mock_personnel = [
        {
            "id": 1,
            "name": "John Doe",
            "phone_num": "1234567890",
            "person_status": "idle",
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "phone_num": "0987654321",
            "person_status": "en route",
        },
    ]
    mock_db_connection.fetchall.return_value = mock_personnel

    response = client.get("/delivery_persons")

    mock_db_connection.execute.assert_called_once()
    assert response.status_code == 200
    assert len(response.json) == 2


def test_get_idle_personnel(client, mock_db_connection):
    """Test get_idle_delivery_personnel endpoint"""
    mock_idle_personnel = [
        {
            "id": 1,
            "name": "John Doe",
            "phone_num": "1234567890",
            "person_status": "idle",
        },
    ]
    mock_db_connection.fetchall.return_value = mock_idle_personnel

    response = client.get("/delivery_persons/idle")

    assert response.status_code == 200
    assert all(person["person_status"] == "idle" for person in response.json)


def test_get_delivery_person_details(client, mock_db_connection):
    """Test get_delivery_person endpoint"""
    mock_person = {
        "id": 1,
        "name": "John Doe",
        "phone_num": "1234567890",
        "person_status": "idle",
    }
    mock_db_connection.fetchone.return_value = mock_person

    response = client.get("/delivery_persons/1")

    mock_db_connection.execute.assert_called_once_with(
        "SELECT * FROM delivery_persons WHERE id = %s", ("1",)
    )
    assert response.status_code == 200
    assert response.json["name"] == "John Doe"


def test_get_deliveries(client, mock_db_connection):
    """Test get_all_deliveries endpoint"""
    mock_deliveries = [
        {
            "id": 1,
            "order_id": 100,
            "delivery_status": "active",
            "created_at": "2023-01-01",
        },
        {
            "id": 2,
            "order_id": 101,
            "delivery_status": "completed",
            "created_at": "2023-01-02",
        },
    ]
    mock_db_connection.fetchall.return_value = mock_deliveries

    response = client.get("/deliveries")

    assert response.status_code == 200
    assert len(response.json) == 2


def test_get_active_deliveries(client, mock_db_connection):
    """Test get_active_deliveries endpoint"""
    mock_active_deliveries = [
        {
            "id": 1,
            "order_id": 100,
            "delivery_status": "active",
            "created_at": "2023-01-01",
        },
    ]
    mock_db_connection.fetchall.return_value = mock_active_deliveries

    response = client.get("/deliveries/active")

    assert response.status_code == 200
    assert all(delivery["delivery_status"] == "active" for delivery in response.json)


def test_assign_delivery(client, mock_db_connection):
    """Test assign_delivery endpoint"""
    mock_idle_person = {
        "id": 1,
        "name": "John Doe",
        "phone_num": "1234567890",
        "person_status": "idle",
    }
    mock_db_connection.fetchall.return_value = [mock_idle_person]
    mock_db_connection.lastrowid = 1

    test_data = {"order_id": "100", "customer_distance": "5.0"}

    with patch("app.process_delivery") as mock_process:
        response = client.post("/assign_delivery", query_string=test_data)

        assert response.status_code == 200
        assert "delivery_id" in response.json
        print(response.json)
        assert response.json["delivery_person"]["id"] == 1
        mock_process.assert_called_once()


def test_delivery_not_found(client, mock_db_connection):
    """Test get_delivery with non-existent delivery"""
    mock_db_connection.fetchone.return_value = None

    response = client.get("/deliveries/999")

    assert response.status_code == 404
    assert response.json["error"] == "Delivery not found"


def test_no_idle_personnel(client, mock_db_connection):
    """Test assign_delivery with no available personnel"""
    mock_db_connection.fetchall.return_value = []

    test_data = {"order_id": "100", "customer_distance": "5.0"}

    response = client.post("/assign_delivery", query_string=test_data)

    assert response.status_code == 400
    assert response.json["error"] == "No delivery personnel available"
