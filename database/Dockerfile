# Use the official MySQL image from the Docker Hub
FROM mysql:5.7

# Set environment variables for MySQL
ENV MYSQL_ROOT_PASSWORD=password
ENV MYSQL_DATABASE=food_delivery

# Copy the initialization script into the container
COPY init.sql /docker-entrypoint-initdb.d/
