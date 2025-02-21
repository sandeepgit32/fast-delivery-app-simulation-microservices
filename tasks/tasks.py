import logging
import os
import random
import time

import requests
from celery import Celery

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Celery
celery = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

ORDER_SERVICE_URL = "http://order-service:5001"
DELIVERY_SERVICE_URL = "http://delivery-service:5002"
STOCK_SERVICE_URL = "http://stock-service:5003"


@celery.task(name="process_order")
def process_order(order_id: str, customer_distance: float, order_items: list):
    logger.info(f"Processing order {order_id}")
    try:
        # Validate stock
        logger.info(f"Validating stock for order {order_id}")
        response = requests.post(
            f"{STOCK_SERVICE_URL}/validate_stock",
            json={"items": order_items},
        )

        if response.status_code != 200:
            logger.error(
                f"Stock service error for order {order_id}: {response.status_code}"
            )
            response = requests.post(
                f"{ORDER_SERVICE_URL}/cancel_order",
                json={
                    "order_id": order_id,
                    "message": "Order cancelled due to server issues",
                },
            )
            return

        elif response.json()["status"] == False:
            logger.warning(
                f"Stock not available for order {order_id}: {response.json()['message']}"
            )
            response = requests.post(
                f"{ORDER_SERVICE_URL}/cancel_order",
                json={"order_id": order_id, "message": response.json()["message"]},
            )
            return

        elif response.json()["status"] == True:
            logger.info(f"Stock validated successfully for order {order_id}")
            # Update message "Order taken" in ORDER_SERVICE
            requests.post(
                f"{ORDER_SERVICE_URL}/update_msg",
                json={
                    "order_id": order_id,
                    "message": "Order taken",
                },
            )
            requests.post(
                f"{DELIVERY_SERVICE_URL}/assign_delivery",
                json={"order_id": order_id, "customer_distance": customer_distance},
            )
            requests.post(
                f"{STOCK_SERVICE_URL}/remove_stock",
                json={"items": order_items},
            )
            logger.info(f"Order {order_id} processed successfully")
            return

        else:
            logger.error(f"Unexpected response for order {order_id}")
            response = requests.post(
                f"{ORDER_SERVICE_URL}/cancel_order",
                json={
                    "order_id": order_id,
                    "message": "Order cancelled due to server issues",
                },
            )
            return

    except Exception as e:
        logger.error(f"Error processing order {order_id}: {str(e)}")
        raise


@celery.task(name="simulate_delivery")
def simulate_delivery(order_id: str, customer_distance: float):
    logger.info(f"Starting delivery simulation for order {order_id}")
    try:
        # Find a list of delivery persons who are idle
        logger.info("Searching for idle delivery persons")
        response = requests.get(f"{DELIVERY_SERVICE_URL}/idle")
        idle_delivery_persons = response.json()

        # If no delivery persion is idle, then check in a gap of 30 seconds repeatedly to find any idle delivery person
        count = 0
        while (len(idle_delivery_persons) == 0) and (count < 120):
            time.sleep(30)
            response = requests.get(f"{DELIVERY_SERVICE_URL}/idle")
            idle_delivery_persons = response.json()
            # Update message "Finding delivery person ..." in ORDER_SERVICE
            requests.post(
                f"{ORDER_SERVICE_URL}/update_msg",
                json={
                    "order_id": order_id,
                    "message": "Finding delivery person ...",
                },
            )
            count += 1

        # If no delivery person is idle for 1 hour, then cancel the order
        if (len(idle_delivery_persons) == 0) and (count == 120):
            logger.error(
                f"No delivery person available for order {order_id} after 1 hour"
            )
            response = requests.post(
                f"{ORDER_SERVICE_URL}/cancel_order",
                json={
                    "order_id": order_id,
                    "message": "No delivery person available",
                },
            )
            return

        # If Idle delivery person is found, then assign the delivery person to the order randomly
        delivery_person = random.choice(idle_delivery_persons)
        delivery_person_id = delivery_person["id"]

        # Update the update_delivery_person_status status to "en_route"
        requests.post(
            f"{DELIVERY_SERVICE_URL}/update_delivery_person_status/{delivery_person_id}",
            json={"person_status": "en_route"},
        )

        # Create a record in deliveries table with delivery_id, order_id, and delivery_person_id
        response = requests.post(
            f"{DELIVERY_SERVICE_URL}/create_delivery_record",
            json={"order_id": order_id, "delivery_person_id": delivery_person_id},
        )

        logger.info(
            f"Assigned delivery person {delivery_person_id} to order {order_id}"
        )

        # Once delivery person is assigned, update the message to "Delivery person assigned"
        requests.post(
            f"{ORDER_SERVICE_URL}/update_msg",
            json={
                "order_id": order_id,
                "message": "Delivery person assigned",
            },
        )

        # Update the /update_msg for ORDER_SERVICE to update message "Delivery en route"
        requests.post(
            f"{ORDER_SERVICE_URL}/update_msg",
            json={
                "order_id": order_id,
                "message": "Delivery on the road",
            },
        )

        # Simulate the delivery time of order based on customer distance
        time.sleep(random.randint(20, 40) + 20 * customer_distance)

        # Call the /close_order for ORDER_SERVICE to close the order
        requests.post(f"{ORDER_SERVICE_URL}/close_order", json={"order_id": order_id})

        # Update the update_delivery_person_status status to "idle"
        requests.post(
            f"{DELIVERY_SERVICE_URL}/update_delivery_person_status/{delivery_person_id}",
            json={"person_status": "idle"},
        )

        logger.info(f"Delivery completed for order {order_id}")

    except Exception as e:
        logger.error(f"Error in delivery simulation for order {order_id}: {str(e)}")
        raise
