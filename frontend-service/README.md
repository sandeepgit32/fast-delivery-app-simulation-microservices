# Food Delivery Frontend Service

A professional Vue.js dashboard for managing the food delivery simulation system.

## Features

- **Dashboard Overview**: Real-time statistics and monitoring
- **Orders Management**: View, create, cancel, and close orders
- **Deliveries Tracking**: Monitor all deliveries and their status
- **Personnel Management**: Track delivery personnel and their availability
- **Stock Management**: Add and remove stock items

## Technology Stack

- Vue.js 3
- Vue Router
- Axios for API calls
- Modern CSS with custom properties
- Responsive design

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run serve

# Build for production
npm run build
```

## Docker

The service runs on port 8080 and connects to the API Gateway at port 5000.

```bash
docker build -t frontend-service .
docker run -p 8080:8080 frontend-service
```

## Environment Variables

- `VUE_APP_API_URL`: API Gateway URL (default: http://localhost:5000)
