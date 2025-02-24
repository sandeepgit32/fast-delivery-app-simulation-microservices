import logging
import os
import random
import sys
import time

import requests
from faker import Faker

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL")
ORDER_INTERVAL = (
    int(os.getenv("ORDER_MIN_INTERVAL")),
    int(os.getenv("ORDER_MAX_INTERVAL")),
)

# Initialize Faker
fake = Faker()

# Generate a pool of random customer names
CUSTOMERS = [fake.name() for _ in range(30)]
CUSTOMER_DISTANCE_MAP = {x: random.randint(1, 12) for x in CUSTOMERS}
ITEMS = list(range(1, 11))  # 10 items


class OrderGenerator:
    def __init__(self, order_service_url):
        self.order_service_url = order_service_url

    def generate_order_payload(self):
        num_items = random.randint(1, 3)  # Each order contains 1-3 items
        items = [
            {"item_id": random.choice(ITEMS), "quantity": random.randint(1, 5)}
            for _ in range(num_items)
        ]
        customer = random.choice(CUSTOMERS)
        return {
            "customer_name": customer,
            "customer_distance": CUSTOMER_DISTANCE_MAP[customer],
            "items": items,
        }

    def send_order_request(self, payload):
        try:
            response = requests.post(
                f"{self.order_service_url}/create_order", json=payload
            )
            if response.status_code == 201:
                logger.info(f"Order created: {payload}")
            else:
                logger.info(f"Order failed: {response.status_code} {response.text}")
        except requests.RequestException as e:
            logger.info(f"Error sending order: {e}")

    def generate_orders(self):
        while True:
            time.sleep(random.randint(*ORDER_INTERVAL))
            order_payload = self.generate_order_payload()
            self.send_order_request(order_payload)


if __name__ == "__main__":
    try:
        logger.info("Starting order generation simulation...")
        order_generator = OrderGenerator(ORDER_SERVICE_URL)
        order_generator.generate_orders()
    except Exception as e:
        logger.error(f"Error running simulation: {e}")
        sys.exit(1)
