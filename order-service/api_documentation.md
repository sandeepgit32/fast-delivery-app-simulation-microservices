# Order Service API Documentation

## Endpoints

### Create Order
- **URL**: `/create_order`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "customer_name": "string",
    "customer_distance": float,
    "items": [
      {"item_id": integer, "quantity": integer}
    ]
  }
  ```
- **Success Response**:
  - Code: 201
  - Content: 
    ```json
    {
        "order_id": "string",
        "task_id": "string"
    }
    ```
- **Error Response**:
  - Code: 400
  - Content: `{"detail": "error message"}`

### Cancel Order
- **URL**: `/cancel_order`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "order_id": "string",
    "message": "string"
  }
  ```
- **Success Response**:
  - Code: 200
  - Content: `{"order_status": "Order cancelled"}`

### Update Message
- **URL**: `/update_msg`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "order_id": "string",
    "message": "string"
  }
  ```
- **Success Response**:
  - Code: 200
  - Content: `{"order_status": "Order message updated"}`

### Close Order
- **URL**: `/close_order`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "order_id": "string",
    "message": "string"
  }
  ```
- **Success Response**:
  - Code: 200
  - Content: `{"order_status": "Order delivered"}`

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
- **URL**: `/order/{order_id}`
- **Method**: `GET`
- **URL Parameters**:
  - `order_id` (string): Unique identifier of the order
- **Success Response**:
  - Code: 200
  - Content: Detailed order object including items
- **Error Response**:
  - Code: 404
  - Content: `{"detail": "Order not found"}`

## Data Models

### Order Object
```json
{
    "id": "string",
    "order_time": "string",
    "customer_name": "string",
    "customer_distance": float,
    "order_status": "string",
    "response_msg": "string",
    "delivered_at": "string|null",
    "items": [
      {"item_id": integer, "item_name": "string", "quantity": integer}
    ]
}
```
