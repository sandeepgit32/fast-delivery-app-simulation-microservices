# Use the official MySQL image from the Docker Hub
FROM mysql:5.7

# Set environment variables for MySQL
ENV MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
ENV MYSQL_DATABASE=${MYSQL_DATABASE}

# Copy the initialization script into the container
COPY init.sql /docker-entrypoint-initdb.d/
