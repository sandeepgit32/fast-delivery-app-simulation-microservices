import time
import requests
import json
from datetime import datetime
import os

LOG_DIR = "logs"

def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def log_data(endpoint, data):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{LOG_DIR}/{endpoint}-{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def collect_logs():
    endpoints = {
        "stock": "http://stock-service:5003/current_stock",
        "orders": "http://order-service:5001/orders",
        "active_orders": "http://order-service:5001/orders/active",
        "completed_orders": "http://order-service:5001/orders/completed"
    }

    while True:
        for name, url in endpoints.items():
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    log_data(name, response.json())
            except Exception as e:
                print(f"Error collecting logs for {name}: {str(e)}")
        
        time.sleep(5)  # Wait 5 seconds before next collection

if __name__ == "__main__":
    ensure_log_dir()
    collect_logs()
