import logging
import os
import random
import time

import requests
from celery import Celery
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Celery
celery = Celery(
    os.getenv("TASK_QUEUE_NAME"),
    broker=os.getenv("TASK_QUEUE_BROKER_URL"),
    backend=os.getenv("TASK_QUEUE_RESULT_BACKEND_URL"),
)

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL")
DELIVERY_SERVICE_URL = os.getenv("DELIVERY_SERVICE_URL")
STOCK_SERVICE_URL = os.getenv("STOCK_SERVICE_URL")


# Retry decorator function
def create_retry_decorator(max_attempts=3):
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException)),
        before_sleep=lambda retry_state: logger.warning(
            f"Request failed, attempting retry {retry_state.attempt_number} of {max_attempts}"
        ),
    )


# Create a reusable retry decorator
retry_request = create_retry_decorator()


@retry_request
def make_request(method, url, **kwargs):
    if method == "GET":
        response = requests.get(url)
    elif method == "POST":
        response = requests.post(url, **kwargs)
    elif method == "PUT":
        response = requests.put(url, **kwargs)
    elif method == "DELETE":
        response = requests.delete(url, **kwargs)
    # Raise an exception for 4xx and 5xx status codes
    response.raise_for_status()
    return response


@celery.task(name="process_order")
def process_order(order_id: str, customer_distance: float, order_items: list):
    logger.info(f"Processing order {order_id}")
    try:
        # Validate stock
        response = make_request(
            "POST",
            f"{STOCK_SERVICE_URL}/validate_stock",
            json={"order_items": order_items},
        )

        if response.status_code != 200:
            logger.error(
                f"Stock service error for order {order_id}: {response.status_code}"
            )
            response = make_request(
                "POST",
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
            response = make_request(
                "POST",
                f"{ORDER_SERVICE_URL}/cancel_order",
                json={"order_id": order_id, "message": response.json()["message"]},
            )
            return

        elif response.json()["status"] == True:
            logger.info(f"Stock validated successfully for order {order_id}")
            # Update message "Order taken" in ORDER_SERVICE
            make_request(
                "POST",
                f"{ORDER_SERVICE_URL}/update_msg",
                json={
                    "order_id": order_id,
                    "message": "Order taken",
                },
            )
            make_request(
                "POST",
                f"{DELIVERY_SERVICE_URL}/assign_delivery",
                json={"order_id": order_id, "customer_distance": customer_distance},
            )
            make_request(
                "POST",
                f"{STOCK_SERVICE_URL}/remove_stock",
                json={"order_items": order_items},
            )
            logger.info(f"Order {order_id} processed successfully")
            return

        else:
            logger.error(f"Unexpected response for order {order_id}")
            response = make_request(
                "POST",
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
        response = make_request("GET", f"{DELIVERY_SERVICE_URL}/delivery_persons/idle")
        idle_delivery_persons = response.json()

        # If no delivery persion is idle, then check in a gap of 30 seconds repeatedly to find any idle delivery person
        count = 0
        while (len(idle_delivery_persons) == 0) and (count < 120):
            time.sleep(30)
            response = make_request("GET", f"{DELIVERY_SERVICE_URL}/idle")
            idle_delivery_persons = response.json()
            # Update message "Finding delivery person ..." in ORDER_SERVICE
            make_request(
                "POST",
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
            response = make_request(
                "POST",
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
        make_request(
            "POST",
            f"{DELIVERY_SERVICE_URL}/update_delivery_person_status",
            json={"person_id": delivery_person_id, "person_status": "en_route"},
        )

        # Create a record in deliveries table with delivery_id, order_id, and delivery_person_id
        response = make_request(
            "POST",
            f"{DELIVERY_SERVICE_URL}/create_delivery_record",
            json={"order_id": order_id, "delivery_person_id": delivery_person_id},
        )

        logger.info(
            f"Assigned delivery person {delivery_person_id} to order {order_id}"
        )

        # Once delivery person is assigned, update the message to "Delivery person assigned"
        make_request(
            "POST",
            f"{ORDER_SERVICE_URL}/update_msg",
            json={
                "order_id": order_id,
                "message": "Delivery person assigned",
            },
        )

        # Update the /update_msg for ORDER_SERVICE to update message "Delivery en route"
        make_request(
            "POST",
            f"{ORDER_SERVICE_URL}/update_msg",
            json={
                "order_id": order_id,
                "message": "Delivery on the road",
            },
        )

        # Simulate the delivery time of order based on customer distance
        delivery_time = random.randint(5, 10) + 5 * customer_distance
        logger.info(f"Delivery time for order {order_id}: {delivery_time} seconds")
        time.sleep(delivery_time)

        # Call the /close_order for ORDER_SERVICE to close the order
        make_request(
            "POST",
            f"{ORDER_SERVICE_URL}/close_order",
            json={
                "order_id": order_id,
                "message": "Order delivered",
            },
        )

        # Update the update_delivery_person_status status to "idle"
        make_request(
            "POST",
            f"{DELIVERY_SERVICE_URL}/update_delivery_person_status",
            json={"person_id": delivery_person_id, "person_status": "idle"},
        )

        logger.info(f"Delivery completed for order {order_id}")

    except Exception as e:
        logger.error(f"Error in delivery simulation for order {order_id}: {str(e)}")
        raise
