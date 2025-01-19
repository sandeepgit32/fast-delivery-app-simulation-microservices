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
      "id": "integer",
      "name": "string",
      "phone_num": "string",
      "status": "string"
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
- **URL**: `/delivery_persons/<person_id>`
- **Method**: GET
- **Response**: 
  ```json
  {
    "id": "integer",
    "name": "string",
    "phone_num": "string",
    "status": "string"
  }
  ```
- **Error Response** (404):
  ```json
  {
    "error": "Delivery person not found"
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
      "id": "integer",
      "order_id": "integer",
      "delivery_person_id": "integer",
      "status": "string",
      "created_at": "datetime",
      "completed_at": "datetime"
    }
  ]
  ```

#### Get Active Deliveries
- **URL**: `/deliveries/active`
- **Method**: GET
- **Response**: Same as Get All Deliveries

#### Get Completed Deliveries
- **URL**: `/deliveries/completed`
- **Method**: GET
- **Response**: Same as Get All Deliveries

#### Get Specific Delivery
- **URL**: `/deliveries/<delivery_id>`
- **Method**: GET
- **Response**: 
  ```json
  {
    "id": "integer",
    "order_id": "integer",
    "delivery_person_id": "integer",
    "status": "string",
    "created_at": "datetime",
    "completed_at": "datetime"
  }
  ```
- **Error Response** (404):
  ```json
  {
    "error": "Delivery not found"
  }
  ```

### Delivery Assignment

#### Assign Delivery
- **URL**: `/assign_delivery`
- **Method**: POST
- **Query Parameters**:
  - `order_id`: ID of the order to be delivered
  - `customer_distance`: Distance to customer location
- **Success Response**:
  ```json
  {
    "delivery_id": "integer",
    "delivery_person": {
      "id": "integer",
      "name": "string",
      "phone_num": "string",
      "status": "string"
    }
  }
  ```
- **Error Response** (400):
  ```json
  {
    "error": "No delivery personnel available"
  }
  ```