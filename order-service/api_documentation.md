# Order Service API Documentation

## Endpoints

### Create Order
- **URL**: `/create_order`
- **Method**: `POST`
- **Query Parameters**:
  - `customer_distance` (float, required): Distance to customer location
  - `items` (dict, required): Dictionary of items and their quantities
- **Success Response**:
  - Code: 201
  - Content: 
    ```json
    {
        "id": "string",
        "order_time": "string",
        "customer_distance": float,
        "status": "active",
        "items": {},
        "message": "Delivery person assigned"
    }
    ```
- **Error Response**:
  - Code: 400
  - Content: `{"error": "error message"}`

### Close Order
- **URL**: `/close_order/<order_id>`
- **Method**: `POST`
- **URL Parameters**:
  - `order_id` (string): Unique identifier of the order
- **Success Response**:
  - Code: 200
  - Content: `{"status": "Order completed"}`

### Get All Orders
- **URL**: `/orders`
- **Method**: `GET`
- **Success Response**:
  - Code: 200
  - Content: Array of order objects

### Get Active Orders
- **URL**: `/orders/active`
- **Method**: `GET`
- **Success Response**:
  - Code: 200
  - Content: Array of active order objects

### Get Completed Orders
- **URL**: `/orders/completed`
- **Method**: `GET`
- **Success Response**:
  - Code: 200
  - Content: Array of completed order objects

### Get Order Details
- **URL**: `/order/<order_id>`
- **Method**: `GET`
- **URL Parameters**:
  - `order_id` (string): Unique identifier of the order
- **Success Response**:
  - Code: 200
  - Content: Detailed order object including items
- **Error Response**:
  - Code: 404
  - Content: `{"error": "Order not found"}`

## Data Models

### Order Object
```json
{
    "customer_name": "string",
    "customer_distance": float,
    "status": "string",
    "items": {
        "item1": float,
        "item2": float,
        "item3": float
    }
}
```
