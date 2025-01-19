import time
import random
import requests
import numpy as np
from datetime import datetime
import threading

class DeliverySimulation:
    def __init__(self):
        self.active_orders = {}
        self.active_deliveries = {}

    def generate_random_order(self):
        return {
            "id": int(time.time() * 1000),
            "timestamp": datetime.now().isoformat(),
            "items": random.sample(["item1", "item2"], random.randint(1, 2)),
            "location": {
                "lat": random.uniform(40.0, 41.0),
                "lon": random.uniform(-74.0, -73.0)
            },
            "status": "created"
        }

    def process_orders(self):
        while True:
            # Generate next event time using exponential distribution
            wait_time = np.random.exponential(1/300)  # Average 1 order per 5 minutes
            time.sleep(wait_time)
            
            # Generate and send order
            order = self.generate_random_order()
            try:
                response = requests.post("http://order-service:5001/orders", json=order)
                if response.status_code == 201:
                    print(f"Order created: {order['id']}")
                    self.active_orders[order['id']] = order
                    # Start delivery process for this order
                    threading.Thread(target=self.process_delivery, args=(order,)).start()
            except Exception as e:
                print(f"Error creating order: {str(e)}")

    def process_delivery(self, order):
        # Wait 10-30 seconds before assigning delivery
        time.sleep(random.uniform(10, 30))
        
        try:
            # Assign delivery
            delivery_response = requests.post(
                "http://delivery-service:5002/assign-delivery", 
                json=order
            )
            
            if delivery_response.status_code == 200:
                print(f"Delivery assigned for order: {order['id']}")
                # Wait 30-60 seconds before updating stock
                time.sleep(random.uniform(30, 60))
                
                # Update stock for each item in order
                self.process_stock_update(order)
        except Exception as e:
            print(f"Error processing delivery: {str(e)}")

    def process_stock_update(self, order):
        try:
            for item in order["items"]:
                stock_response = requests.post(
                    "http://stock-service:5003/update_stock",
                    json={"item_id": item, "quantity": -1}
                )
                if stock_response.status_code == 200:
                    print(f"Stock updated for item {item} in order {order['id']}")
        except Exception as e:
            print(f"Error updating stock: {str(e)}")

def run_simulation():
    simulation = DeliverySimulation()
    simulation.process_orders()

if __name__ == "__main__":
    run_simulation()
