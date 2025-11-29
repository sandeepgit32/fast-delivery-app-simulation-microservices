# Stock Service API Documentation

## Base URL
`http://localhost:5003`

## Endpoints

### Add Stock
Adds stock quantities for multiple items. Validates that new quantity does not exceed max_quantity.

- **URL**: `/add_stock`
- **Method**: POST
- **Content-Type**: application/json
- **Request Body**:
  ```json
  {
    "order_items": [
      {
        "item_id": integer,
        "quantity": integer
      }
    ]
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "message": "Stock updated"
    }
    ```
- **Error Response**:
  - **Code**: 400/404
  - **Content**:
    ```json
    {
      "detail": "Error message details"
    }
    ```

### Remove Stock
Removes stock quantities for multiple items after validating availability.

- **URL**: `/remove_stock`
- **Method**: POST
- **Content-Type**: application/json
- **Request Body**:
  ```json
  {
    "order_items": [
      {
        "item_id": integer,
        "quantity": integer
      }
    ]
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "message": "Stock updated"
    }
    ```
- **Error Response**:
  - **Code**: 400
  - **Content**:
    ```json
    {
      "detail": "Insufficient stock for item {item_name}"
    }
    ```

### Validate Stock
Validates if stock operations are possible for multiple items.

- **URL**: `/validate_stock`
- **Method**: POST
- **Content-Type**: application/json
- **Request Body**:
  ```json
  {
    "order_items": [
      {
        "item_id": integer,
        "quantity": integer
      }
    ]
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "status": true,
      "message": "Items currently in stock"
    }
    ```
  OR
    ```json
    {
      "status": false,
      "message": "Insufficient stock for item {item_name}"
    }
    ```

### Get All Stock Levels
Retrieves current stock levels for all items.

- **URL**: `/current_stock`
- **Method**: GET
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    [
      {
        "item_id": integer,
        "item_name": "string",
        "quantity": integer,
        "max_quantity": integer
      }
    ]
    ```

### Get Specific Item Stock
Retrieves stock level for a specific item.

- **URL**: `/current_stock/{item_id}`
- **Method**: GET
- **URL Parameters**: 
  - `item_id`: ID of the item to retrieve
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "item_id": integer,
      "item_name": "string",
      "quantity": integer,
      "max_quantity": integer
    }
    ```
- **Error Response**:
  - **Code**: 404
  - **Content**:
    ```json
    {
      "detail": "Item not found"
    }
    ```

## Example Usage

### Adding Stock
```bash
curl -X POST http://localhost:5003/add_stock \
  -H "Content-Type: application/json" \
  -d '{
    "order_items": [
      {"item_id": 1, "quantity": 10},
      {"item_id": 2, "quantity": 5}
    ]
  }'
```

### Removing Stock
```bash
curl -X POST http://localhost:5003/remove_stock \
  -H "Content-Type: application/json" \
  -d '{
    "order_items": [
      {"item_id": 1, "quantity": 2},
      {"item_id": 2, "quantity": 1}
    ]
  }'
```

### Getting Stock Levels
```bash
# Get all stock
curl http://localhost:5003/current_stock

# Get specific item stock
curl http://localhost:5003/current_stock/1
```
