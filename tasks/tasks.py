import os
import random
import time
from datetime import datetime

import requests
from celery import Celery

# Initialize Celery
celery = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

db_config = {
    "user": "root",
    "password": "password",
    "host": "db",
    "database": "food_delivery",
}
ORDER_SERVICE_URL = "http://order-service:5001"
DELIVERY_SERVICE_URL = "http://delivery-service:5002"
STOCK_SERVICE_URL = "http://stock-service:5003"


@celery.task(name="process_order")
def process_order(order_id: str, customer_distance: float, order_items: list):
    # Validate stock
    response = requests.post(
        f"{STOCK_SERVICE_URL}/validate_stock",
        json={"items": order_items},
    )
    # If stock is not available, cancel order
    # If stock is available, assign delivery
    if response.status_code != 200:
        response = requests.post(
            f"{ORDER_SERVICE_URL}/cancel_order",
            json={
                "order_id": order_id,
                "message": "Order cancelled due to server issues",
            },
        )
        return
    elif response.json()["status"] == False:
        response = requests.post(
            f"{ORDER_SERVICE_URL}/cancel_order",
            json={"order_id": order_id, "message": response.json()["message"]},
        )
        return
    elif response.json()["status"] == True:
        requests.post(
            f"{DELIVERY_SERVICE_URL}/assign_delivery",
            json={"order_id": order_id, "customer_distance": customer_distance},
        )
        requests.post(
            f"{STOCK_SERVICE_URL}/remove_stock",
            json={"items": order_items},
        )
        return
    else:
        response = requests.post(
            f"{ORDER_SERVICE_URL}/cancel_order",
            json={
                "order_id": order_id,
                "message": "Order cancelled due to server issues",
            },
        )
        return


@celery.task(name="simulate_delivery")
def simulate_delivery(order_id: str):
    # Find a list of delivery persons who are idle
    # If no delivery persion is idle, then check in a gap of 30 seconds repeatedly to find any idle delivery person
    # If no delivery person is idle for 1 hour, then cancel the order
    # If Idle delivery person is found, then assign the delivery person to the order randomly
    # Till no delivery person is idle, keep checking in a gap of 30 seconds call /update_msg for ORDER_SERVICE to update message "Finding delivery person ..."
    # Once delivery person is assigned, update the message to "Delivery person assigned"
    # Create a record in deliveries table with delivery_id, order_id, and delivery_person_id
    # Update the update_delivery_person_status status to "en_route"
    # Update the /update_msg for ORDER_SERVICE to update message "Delivery en route"
    time.sleep(random.randint(60, 180))
    # Call the /close_order for ORDER_SERVICE to close the order
    # Update the update_delivery_person_status status to "idle"
