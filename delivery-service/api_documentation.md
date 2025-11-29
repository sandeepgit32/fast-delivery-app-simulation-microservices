# Delivery Service API Documentation

## Base URL
`http://localhost:5002`

## Endpoints

### Delivery Personnel

#### Get All Delivery Personnel
- **URL**: `/delivery_persons`
- **Method**: GET
- **Response**: 
  ```json
  [
    {
      "id": integer,
      "name": "string",
      "phone_number": "string",
      "person_status": "string"
    }
  ]
  ```

#### Get En-Route Delivery Personnel
- **URL**: `/delivery_persons/en_route`
- **Method**: GET
- **Response**: Same as Get All Delivery Personnel

#### Get Idle Delivery Personnel
- **URL**: `/delivery_persons/idle`
- **Method**: GET
- **Response**: Same as Get All Delivery Personnel

#### Get Specific Delivery Person
- **URL**: `/delivery_persons/{person_id}`
- **Method**: GET
- **Response**: 
  ```json
  {
    "id": integer,
    "name": "string",
    "phone_number": "string",
    "person_status": "string"
  }
  ```
- **Error Response** (404):
  ```json
  {
    "detail": "Delivery person not found"
  }
  ```

### Deliveries

#### Get All Deliveries
- **URL**: `/deliveries`
- **Method**: GET
- **Response**: 
  ```json
  [
    {
      "id": integer,
      "order_id": "string",
      "order_status": "string",
      "customer_name": "string",
      "customer_distance": float,
      "delivery_person_id": integer,
      "delivery_person_name": "string",
      "order_time": "datetime",
      "delivered_at": "datetime|null"
    }
  ]
  ```

#### Get Specific Delivery
- **URL**: `/deliveries/{delivery_id}`
- **Method**: GET
- **Response**: Same as single delivery object above
- **Error Response** (404):
  ```json
  {
    "detail": "Delivery not found"
  }
  ```

#### Get Delivery by Order ID
- **URL**: `/deliveries/by_order/{order_id}`
- **Method**: GET
- **Response**: Same as single delivery object above
- **Error Response** (404):
  ```json
  {
    "detail": "Delivery not found for this order"
  }
  ```

### Delivery Assignment

#### Assign Delivery
- **URL**: `/assign_delivery`
- **Method**: POST
- **Content-Type**: application/json
- **Request Body**:
  ```json
  {
    "order_id": "string"
  }
  ```
- **Success Response**:
  ```json
  {
    "order_id": "string",
    "task_id": "string"
  }
  ```
- **Error Response** (404):
  ```json
  {
    "detail": "Order not found"
  }
  ```

#### Update Delivery Person Status
- **URL**: `/update_delivery_person_status`
- **Method**: POST
- **Content-Type**: application/json
- **Request Body**:
  ```json
  {
    "person_id": integer,
    "person_status": "idle|en_route"
  }
  ```
- **Success Response**:
  ```json
  {
    "message": "Delivery person status updated"
  }
  ```
- **Error Response** (400):
  ```json
  {
    "detail": "Invalid status. Must be 'idle' or 'en_route'"
  }
  ```

#### Create Delivery Record
- **URL**: `/create_delivery_record`
- **Method**: POST
- **Content-Type**: application/json
- **Request Body**:
  ```json
  {
    "order_id": "string",
    "delivery_person_id": integer
  }
  ```
- **Success Response**:
  ```json
  {
    "message": "Delivery created",
    "delivery_id": integer
  }
  ```
  