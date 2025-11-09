import logging
import os
import random
import sys
import threading
import time

import requests
from faker import Faker
from fastapi import FastAPI
from pydantic import BaseModel
from requests.adapters import HTTPAdapter
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

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL")
STOCK_SERVICE_URL = os.getenv("STOCK_SERVICE_URL")
ORDER_INTERVAL_MIN = int(os.getenv("ORDER_INTERVAL_MIN"))
ORDER_INTERVAL_MAX = int(os.getenv("ORDER_INTERVAL_MAX"))

# Create a session with connection pooling
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=100,  # Number of connection objects to keep in pool
    pool_maxsize=100,  # Maximum number of connections to keep in pool
    max_retries=0,  # Let tenacity handle retries
    pool_block=False,  # Don't block when pool is full (raise error)
)
session.mount("http://", adapter)
session.mount("https://", adapter)


# Initialize Faker
fake = Faker()

# Generate a pool of random customer names
CUSTOMERS = [fake.name() for _ in range(30)]
CUSTOMER_DISTANCE_MAP = {x: random.randint(1, 12) for x in CUSTOMERS}
ORDER_GENERATION = False

app = FastAPI(title="Order Auto Generation Simulation")


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
    # Add timeout if not provided
    if "timeout" not in kwargs:
        kwargs["timeout"] = (5, 30)  # (connect timeout, read timeout)

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


response = make_request("GET", f"{STOCK_SERVICE_URL}/current_stock")
ITEMS = [x["item_id"] for x in response.json()]
print(">>> ITEMS:", ITEMS)


class OrderInterval(BaseModel):
    order_interval_min: int
    order_interval_max: int


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
            response = make_request(
                "POST", f"{self.order_service_url}/create_order", json=payload
            )
            if response.status_code == 201:
                logger.info(f"Order created: {payload}")
            else:
                logger.info(f"Order failed: {response.status_code} {response.text}")
        except requests.RequestException as e:
            logger.info(f"Error sending order: {e}")

    def generate_orders(self):
        while True:
            time.sleep(random.randint(ORDER_INTERVAL_MIN, ORDER_INTERVAL_MAX))
            order_payload = self.generate_order_payload()
            if ORDER_GENERATION:
                self.send_order_request(order_payload)


def run_simulation():
    try:
        logger.info("Starting order generation simulation...")
        order_generator = OrderGenerator(ORDER_SERVICE_URL)
        order_generator.generate_orders()
    except Exception as e:
        logger.error(f"Error running simulation: {e}")
        sys.exit(1)


@app.get("/order_start")
async def order_auto_generation_start():
    """Start the order generation."""
    global ORDER_GENERATION
    ORDER_GENERATION = True
    return {"message": "Order generation started"}


@app.get("/order_stop")
async def order_auto_generation_stop():
    """Stop the order generation."""
    global ORDER_GENERATION
    ORDER_GENERATION = False
    return {"message": "Order generation stopped"}


@app.get("/get_order_interval", response_model=dict)
async def order_auto_generation_get_interval():
    """Get the order generation rate."""
    return {
        "message": f"Current order interval is set to {ORDER_INTERVAL_MIN}-{ORDER_INTERVAL_MAX} seconds"
    }


@app.post("/set_order_interval", response_model=dict)
async def order_auto_generation_set_interval(request: OrderInterval):
    """Set the order generation rate."""
    global ORDER_INTERVAL_MIN, ORDER_INTERVAL_MAX
    ORDER_INTERVAL_MIN = request.order_interval_min
    ORDER_INTERVAL_MAX = request.order_interval_max
    return {
        "message": f"Order interval set to {ORDER_INTERVAL_MIN}-{ORDER_INTERVAL_MAX} seconds"
    }


if __name__ == "__main__":
    threading.Thread(target=run_simulation, daemon=True).start()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5005)
