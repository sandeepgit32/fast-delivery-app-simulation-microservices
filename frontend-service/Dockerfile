FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Build the app
RUN npm run build

# Install a simple HTTP server for serving static content
RUN npm install -g http-server

# Expose port
EXPOSE 8080

# Serve the built app
CMD ["http-server", "dist", "-p", "8080", "--proxy", "http://localhost:8080?"]
