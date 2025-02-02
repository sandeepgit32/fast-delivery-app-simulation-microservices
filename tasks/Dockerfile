FROM python:3.9-slim

WORKDIR /app

# Create a non-root user
RUN groupadd -r celery && useradd -r -g celery celery

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Change ownership of the working directory
RUN chown -R celery:celery /app

# Switch to non-root user
USER celery

CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
