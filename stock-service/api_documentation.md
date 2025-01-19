# Stock Service API Documentation

## Base URL
`http://localhost:5003`

## Endpoints

### Add Stock
Adds stock quantities for multiple items.

- **URL**: `/add_stock`
- **Method**: POST
- **Content-Type**: application/json
- **Request Body**:
  ```json
  {
    "order_items": [
      {
        "item_id": "string",
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
      "error": "Error message details"
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
        "item_id": "string",
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
      "error": "Insufficient stock for item {item_id}"
    }
    ```
  OR
    ```json
    {
      "error": "Item {item_id} not found"
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
        "item_id": "string",
        "item_name": "string",
        "quantity": integer
      }
    ]
    ```

### Get Specific Item Stock
Retrieves stock level for a specific item.

- **URL**: `/current_stock/<item_id>`
- **Method**: GET
- **URL Parameters**: 
  - `item_id`: ID of the item to retrieve
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "item_id": "string",
      "item_name": "string",
      "quantity": integer
    }
    ```
- **Error Response**:
  - **Code**: 404
  - **Content**:
    ```json
    {
      "error": "Item not found"
    }
    ```

## Example Usage

### Adding Stock
```bash
curl -X POST http://localhost:5003/add_stock \
  -H "Content-Type: application/json" \
  -d '{
    "order_items": [
      {"item_id": "item1", "quantity": 10},
      {"item_id": "item2", "quantity": 5}
    ]
  }'
```

### Removing Stock
```bash
curl -X POST http://localhost:5003/remove_stock \
  -H "Content-Type: application/json" \
  -d '{
    "order_items": [
      {"item_id": "item1", "quantity": 2},
      {"item_id": "item2", "quantity": 1}
    ]
  }'
```

### Getting Stock Levels
```bash
# Get all stock
curl http://localhost:5003/current_stock

# Get specific item stock
curl http://localhost:5003/current_stock/item1
```
