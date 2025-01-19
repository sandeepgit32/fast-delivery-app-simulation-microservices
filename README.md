# Food Delivery Simulation App

## Overview

This project simulates a food delivery system using a microservices architecture. The simulation includes a Google Map over any city, where orders arrive at random times from random locations with a specified arrival rate. The system features a central food kitchen, a finite number of delivery personnel, and limited stock for a list of food items. Orders are rejected when the food stock is depleted. The frontend displays a live map (dummy) that updates every 5 seconds, showing the locations of delivery personnel and the order pattern. Additionally, a graph shows order fulfillment statistics.

## Architecture

### Microservices

1. **API Gateway**
   - Central entry point for all requests.
   - Routes requests to the appropriate backend services.
   - Implements rate limiting, request logging, and error handling.

2. **Order Service**
   - Manages order lifecycle: creation, status updates, and tracking.
   - Generates random orders with a predefined rate using Simpy.
   - Validates stock availability via the Stock Service.
   - Sends accepted orders to the Delivery Service for fulfillment.
   - Logs order data in the MySQL database.

3. **Delivery Service**
   - Tracks delivery personnel and their current states (idle, en route, delivering).
   - Assigns orders to available personnel using geospatial proximity calculations (e.g., Haversine formula).
   - Simulates delivery personnel movement using Simpy.
   - Updates delivery status and logs completion in the database.

4. **Stock Service**
   - Manages stock levels for the menu.
   - Decrements stock when an order is accepted.
   - Periodically restocks based on predefined rules or admin inputs.

5. **Frontend Service**
   - Displays the live map with delivery personnel and order locations.
   - Shows real-time graphs of order fulfillment and stock levels.
   - Allows users to configure simulation parameters (e.g., order rate, stock limits).

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
  - `POST /orders`: Generate a new order.
  - `GET /orders`: Fetch current or historical order data.
  - `GET /delivery-personnel`: Fetch real-time locations and statuses.
  - `POST /assign-order`: Assign an order to a delivery person.
  - `GET /stock`: Fetch current stock levels.
  - `POST /update-stock`: Adjust stock levels (e.g., restock items).

#### Order Service

- **Port**: 5001
- **Endpoints**:
  - `POST /orders`: Create a new order.
  - `GET /orders`: Fetch current or historical order data.

#### Delivery Service

- **Port**: 5002
- **Endpoints**:
  - `GET /delivery-personnel`: Fetch real-time locations and statuses.
  - `POST /assign-order`: Assign an order to a delivery person.

#### Stock Service

- **Port**: 5003
- **Endpoints**:
  - `GET /stock`: Fetch current stock levels.
  - `POST /update-stock`: Adjust stock levels (e.g., restock items).

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

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.
