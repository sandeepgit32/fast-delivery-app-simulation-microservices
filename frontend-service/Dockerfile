# Use the official Node.js image from the Docker Hub
FROM node:14

# Set the working directory
WORKDIR /app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install the dependencies
RUN npm install

# Copy the rest of the application code into the container
COPY . .

# Build the Vue application
RUN npm run build

# Expose the port the app runs on
EXPOSE 8080

# Run the application
CMD ["npm", "run", "serve"]