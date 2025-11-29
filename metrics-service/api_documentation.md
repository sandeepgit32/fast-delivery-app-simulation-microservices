# Metrics Service API Documentation

## Overview

The Metrics Service collects and stores time-series metrics data using InfluxDB. It automatically polls the Order Service every 5 seconds to track active order counts over time, enabling historical analysis and visualization.

## Endpoints

### Health Check
- **URL**: `/`
- **Method**: `GET`
- **Success Response**:
  - Code: 200
  - Content: 
    ```json
    {
        "status": "Metrics service is running"
    }
    ```

### Health Status
- **URL**: `/health`
- **Method**: `GET`
- **Success Response**:
  - Code: 200
  - Content: 
    ```json
    {
        "status": "healthy"
    }
    ```

### Get Active Orders Metrics
- **URL**: `/metrics/active-orders`
- **Method**: `GET`
- **Query Parameters**:
  - `range` (string, optional): Time range for metrics. Default: `15m`
    - Valid values: `15m`, `30m`, `1h`, `2h`, `3h`, `6h`, `12h`, `24h`
- **Success Response**:
  - Code: 200
  - Content: 
    ```json
    {
        "range": "15m",
        "data": [
            {
                "timestamp": "2025-11-29T10:30:00.000000+00:00",
                "count": 5
            },
            {
                "timestamp": "2025-11-29T10:30:05.000000+00:00",
                "count": 7
            }
        ]
    }
    ```
- **Error Response**:
  - Code: 400
  - Content: 
    ```json
    {
        "detail": "Invalid range. Valid options: ['15m', '30m', '1h', '2h', '3h', '6h', '12h', '24h']"
    }
    ```
  - Code: 500
  - Content: 
    ```json
    {
        "detail": "Failed to retrieve metrics: <error message>"
    }
    ```

### Get Current Active Orders Count
- **URL**: `/metrics/active-orders/current`
- **Method**: `GET`
- **Success Response**:
  - Code: 200
  - Content: 
    ```json
    {
        "timestamp": "2025-11-29T10:30:05.000000+00:00",
        "count": 7
    }
    ```
  - If no data available:
    ```json
    {
        "timestamp": null,
        "count": 0
    }
    ```
- **Error Response**:
  - Code: 500
  - Content: 
    ```json
    {
        "detail": "Failed to retrieve current metrics: <error message>"
    }
    ```

## Data Models

### Metric Data Point
```json
{
    "timestamp": "string (ISO 8601 format)",
    "count": integer
}
```

### Metrics Response
```json
{
    "range": "string",
    "data": [
        {
            "timestamp": "string",
            "count": integer
        }
    ]
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `INFLUXDB_URL` | InfluxDB connection URL | `http://influxdb:8086` |
| `INFLUXDB_TOKEN` | InfluxDB authentication token | `my-super-secret-token` |
| `INFLUXDB_ORG` | InfluxDB organization name | `food_delivery` |
| `INFLUXDB_BUCKET` | InfluxDB bucket for storing metrics | `metrics` |
| `ORDER_SERVICE_URL` | URL of the Order Service | `http://order-service:5001` |
| `POLLING_INTERVAL` | Interval (in seconds) for polling active orders | `5` |

## Background Process

The service runs a background thread that:
1. Polls the Order Service `/orders/active` endpoint every 5 seconds
2. Counts the number of active orders
3. Stores the count as a time-series data point in InfluxDB

This ensures metrics are collected continuously, even when no clients are actively viewing the dashboard.

## InfluxDB Schema

### Measurement: `active_orders`

| Field | Type | Description |
|-------|------|-------------|
| `count` | Integer | Number of active orders at the timestamp |

### Tags

| Tag | Description |
|-----|-------------|
| `service` | Source service identifier (`order-service`) |
