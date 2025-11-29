import os
import threading
import time
from datetime import datetime

import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

app = FastAPI(title="Metrics Service API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# InfluxDB configuration
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "my-super-secret-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "food_delivery")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "metrics")

# Order service URL
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:5001")

# Polling interval in seconds
POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL", "5"))

# InfluxDB client
influx_client = None
write_api = None
query_api = None


def get_influx_client():
    """Get or create InfluxDB client."""
    global influx_client, write_api, query_api
    if influx_client is None:
        influx_client = InfluxDBClient(
            url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
        )
        write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        query_api = influx_client.query_api()
    return influx_client, write_api, query_api


def fetch_active_orders_count():
    """Fetch the count of active orders from the order service."""
    try:
        response = requests.get(f"{ORDER_SERVICE_URL}/orders/active", timeout=5)
        if response.status_code == 200:
            orders = response.json()
            return len(orders)
        else:
            print(f"Failed to fetch active orders: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching active orders: {e}")
        return None


def store_active_orders_count(count):
    """Store the active orders count in InfluxDB."""
    try:
        _, write_api, _ = get_influx_client()
        point = (
            Point("active_orders")
            .tag("service", "order-service")
            .field("count", count)
            .time(datetime.utcnow())
        )
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        print(f"Stored active orders count: {count}")
    except Exception as e:
        print(f"Error storing to InfluxDB: {e}")


def polling_task():
    """Background task to poll active orders and store in InfluxDB."""
    print(f"Starting polling task (interval: {POLLING_INTERVAL}s)")

    # Wait for services to be ready
    time.sleep(10)

    while True:
        try:
            count = fetch_active_orders_count()
            if count is not None:
                store_active_orders_count(count)
        except Exception as e:
            print(f"Polling task error: {e}")

        time.sleep(POLLING_INTERVAL)


# Start the polling thread when the app starts
polling_thread = None


@app.on_event("startup")
async def startup_event():
    """Start the background polling task."""
    global polling_thread
    polling_thread = threading.Thread(target=polling_task, daemon=True)
    polling_thread.start()
    print("Metrics service started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global influx_client
    if influx_client:
        influx_client.close()
    print("Metrics service stopped")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "Metrics service is running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/metrics/active-orders")
async def get_active_orders_metrics(
    range: str = Query(
        default="15m",
        description="Time range for metrics (e.g., 15m, 30m, 1h, 2h, 3h, 6h, 12h, 24h)",
    ),
):
    """
    Retrieve active orders metrics for the specified time range.

    Returns time-series data of active order counts.
    """
    # Validate and parse the range parameter
    valid_ranges = {
        "15m": "-15m",
        "30m": "-30m",
        "1h": "-1h",
        "2h": "-2h",
        "3h": "-3h",
        "6h": "-6h",
        "12h": "-12h",
        "24h": "-24h",
    }

    if range not in valid_ranges:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid range. Valid options: {list(valid_ranges.keys())}",
        )

    influx_range = valid_ranges[range]

    try:
        _, _, query_api = get_influx_client()

        # Query InfluxDB for the time series data
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: {influx_range})
            |> filter(fn: (r) => r._measurement == "active_orders")
            |> filter(fn: (r) => r._field == "count")
            |> sort(columns: ["_time"], desc: false)
        '''

        result = query_api.query(query, org=INFLUXDB_ORG)

        data_points = []
        for table in result:
            for record in table.records:
                data_points.append(
                    {
                        "timestamp": record.get_time().isoformat(),
                        "count": record.get_value(),
                    }
                )

        return {"range": range, "data": data_points}

    except Exception as e:
        print(f"Error querying InfluxDB: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve metrics: {str(e)}"
        )


@app.get("/metrics/active-orders/current")
async def get_current_active_orders():
    """Get the most recent active orders count."""
    try:
        _, _, query_api = get_influx_client()

        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -5m)
            |> filter(fn: (r) => r._measurement == "active_orders")
            |> filter(fn: (r) => r._field == "count")
            |> last()
        '''

        result = query_api.query(query, org=INFLUXDB_ORG)

        for table in result:
            for record in table.records:
                return {
                    "timestamp": record.get_time().isoformat(),
                    "count": record.get_value(),
                }

        return {"timestamp": None, "count": 0}

    except Exception as e:
        print(f"Error querying InfluxDB: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve current metrics: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5006)
