FROM python:3.13-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --locked --no-cache

# Create a volume for the database
VOLUME ["/app/data"]

# Set environment variable to use the volume for database
ENV DATABASE_URL=sqlite:////app/data/chat_conversations.db

# Copy and set up entrypoint script for migrations
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Run the application with migrations
ENTRYPOINT ["/app/docker-entrypoint.sh"]
