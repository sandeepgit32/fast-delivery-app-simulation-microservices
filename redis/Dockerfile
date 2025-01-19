# Use the official Redis image from the Docker Hub
FROM redis:6.2

# Copy the Redis configuration file into the container
COPY redis.conf /usr/local/etc/redis/redis.conf

# Run Redis with the specified configuration file
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]