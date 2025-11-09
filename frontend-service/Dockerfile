FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Set build argument and environment variable for Vue
ARG VUE_APP_API_URL=http://localhost:5000
ENV VUE_APP_API_URL=$VUE_APP_API_URL

# Build the app
RUN npm run build

# Install a simple HTTP server for serving static content
RUN npm install -g http-server

# Expose port
EXPOSE 8080

# Serve the built app
CMD ["http-server", "dist", "-p", "8080", "--proxy", "http://localhost:8080?"]
