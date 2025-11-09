# Food Delivery Simulation App

## Overview

This project simulates a fast delivery system that operates using a microservices architecture. The system autonomously generates orders at random intervals and assigns them to available delivery personnel. The entire process, from order creation to delivery completion, is handled in an asynchronous and event-driven manner. The complete workflow is described below:

1. **Order Generation** - The system automatically generates new orders at random intervals. These orders consist of one or more items chosen from the available stock. Each order is recorded in the system.

2. **Stock Validation and Order Confirmation** - Once an order is generated, the Stock Service verifies whether the requested items are available. If sufficient stock exists, the order is confirmed and the stock quantities are updated accordingly. If an item is out of stock or the order quantity is more than the available quantity, the order is cancelled.

3. **Delivery Person Assignment** - After an order is confirmed, the system checks if any delivery personnel are idle. If an idle delivery person is available, the system assigns them to the order. The Delivery Service updates the delivery person's status to `en route` and creates an entry in the deliveries table, mapping the order to the assigned delivery person. If no delivery person is available, the order remains in a waiting state until someone becomes free.

4. **Order Delivery Process** - The assigned delivery person picks up the order and begins the delivery process. Once the delivery is completed, the order status is updated to `completed`.
    
5. **Resetting the Delivery Person’s Status** - After completing the delivery, the delivery person's status is updated back to `idle`. They are now available to be assigned to a new order.

## Architecture

### Microservices

1. **API Gateway**
   - Serves as the central entry point for all incoming requests.
   - Routes requests to the appropriate backend services.
   - Implements features such as rate limiting, request logging, and error handling.

2. **Order Service**
   - Manages customer orders, allowing users to view, create, cancel, or close orders.
   - Stores order details in the orders database table.
   - Tracks individual order items and their quantities in the order_items table.
   - Processes new order requests asynchronously by sending tasks to a queue, where they are handled by the Task Service.

3. **Delivery Service**
   - Manages delivery personnel and their statuses (idle, en-route) using the delivery_persons table.
   - Maintains order-to-delivery-person mappings in the deliveries table.
   - Allows users to view available delivery personnel and active deliveries.
   - Assigning a delivery person is handled asynchronously via the Task Service.

4. **Stock Service**
   - Tracks stock levels for available menu items using the stock database table.
   - Allows users to view current stock levels.
   - Automatically decrements item quantities when an order is accepted.

5. **Task Service**
   - Handles short-term asynchronous tasks via a task queue.
   - Processes new order requests asynchronously.
   - Assigns delivery personnel asynchronously.
   - Does not interact with the database directly; instead, it communicates with other services (Order Service, Stock Service, and Delivery Service) via REST API calls to retrieve and update data.

### Database

- **MySQL**: Persistent storage for order details, delivery data, and stock levels.
- **Redis**: Real-time cache for delivery personnel locations and in-progress orders.

### Deployment

- **Docker**: Each service runs in its own Docker container.
- **Docker Compose**: Used to orchestrate the services and manage dependencies.

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/food-delivery-simulation-app.git
   cd food-delivery-simulation-app
   ```

2. Build and start the services using Docker Compose:

   ```bash
   docker-compose up --build
   ```

3. Access the frontend service at `http://localhost:8080`.

### Services

#### API Gateway

- **Port**: 5000
- **Endpoints**:
  - `GET /orders`: Get all orders
  - `GET /orders/active`: Get active orders
  - `GET /orders/completed`: Get completed orders
  - `GET /order/{order_id}`: Get specific order details with items availability
  - `GET /delivery_persons`: Get all delivery personnel
  - `GET /delivery_persons/en_route`: Get personnel currently delivering
  - `GET /delivery_persons/idle`: Get available personnel
  - `GET /delivery_persons/{person_id}`: Get specific delivery person details
  - `GET /deliveries`: Get all deliveries
  - `GET /deliveries/{delivery_id}`: Get specific delivery details
  - `GET /current_stock`: Get all stock levels
  - `GET /current_stock/{item_id}`: Get specific item stock level
  - `POST /create_order`: Create a new order with customer details and items
  - `POST /close_order/{order_id}`: Mark an order as delivered
  - `POST /cancel_order/{order_id}`: Cancel an order with a message
  - `POST /update_msg/{order_id}`: Update message for an order
  - `POST /assign_delivery`: Queue a delivery simulation task
  - `POST /update_delivery_person_status/{person_id}`: Update delivery person status
  - `POST /add_stock`: Add stock quantities for multiple items
  - `POST /remove_stock`: Remove stock quantities after validation
  - `POST /validate_stock`: Validate if stock operations are possible

#### Order Service

- **Port**: 5001
- **Endpoints**:
  - `POST /create_order`: Create a new order with customer details and items
  - `POST /close_order/{order_id}`: Mark an order as delivered
  - `POST /cancel_order/{order_id}`: Cancel an order with a message
  - `POST /update_msg/{order_id}`: Update message for an order
  - `GET /orders`: Get all orders
  - `GET /orders/active`: Get active orders
  - `GET /orders/completed`: Get completed orders
  - `GET /order/{order_id}`: Get specific order details with items

#### Delivery Service

- **Port**: 5002
- **Endpoints**:
  - `GET /delivery_persons`: Get all delivery personnel
  - `GET /delivery_persons/en_route`: Get personnel currently delivering
  - `GET /delivery_persons/idle`: Get available personnel
  - `GET /delivery_persons/{person_id}`: Get specific delivery person details
  - `GET /deliveries`: Get all deliveries
  - `GET /deliveries/{delivery_id}`: Get specific delivery details
  - `POST /assign_delivery`: Queue a delivery simulation task
  - `POST /update_delivery_person_status/{person_id}`: Update delivery person status

#### Stock Service

- **Port**: 5003
- **Endpoints**:
  - `POST /add_stock`: Add stock quantities for multiple items
  - `POST /remove_stock`: Remove stock quantities after validation
  - `POST /validate_stock`: Validate if stock operations are possible
  - `GET /current_stock`: Get all stock levels
  - `GET /current_stock/{item_id}`: Get specific item stock level

#### Frontend Service

- **Port**: 8080
- **Features**:
  - Displays live map with delivery personnel and order locations.
  - Shows real-time graphs of order fulfillment and stock levels.
  - Allows users to configure simulation parameters.

### Configuration

#### MySQL

- **User**: root
- **Password**: password
- **Database**: food_delivery

#### Redis

- **Port**: 6379

### File Structure

```
food-delivery-simulation-app/
├── api-gateway/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── config/
│       └── config.yaml
├── order-service/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── config/
│       └── config.yaml
├── delivery-service/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── config/
│       └── config.yaml
├── stock-service/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── config/
│       └── config.yaml
├── frontend-service/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   └── components/
│   │       └── PlotlyGraph.vue
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   ├── Dockerfile
│   └── vue.config.js
├── database/
│   ├── init.sql
│   ├── Dockerfile
│   └── config/
│       └── my.cnf
├── redis/
│   ├── Dockerfile
│   └── config/
│       └── redis.conf
├── docker-compose.yml
└── README.md
```

### Microservices Architecture

![Architecture](architecture.drawio.png)


### Database Schema

![Database Schema](database_schema.png)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.
