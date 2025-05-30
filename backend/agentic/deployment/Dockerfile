FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV AGENTIC_DEBUG=off
ENV PORT=8086
ENV AGENT_PATH="agents/basic_agent."

# Set working directory
WORKDIR /app

# Copy project files
COPY ./agents /app/agents
COPY ./tools /app/tools

# Copy .env file if it exists, otherwise create an empty one
COPY ./.env* /app/.env

# Install Python dependencies
RUN pip install --no-cache-dir "agentic-framework[all]" --extra-index-url https://download.pytorch.org/whl/cpu

# Expose the port the app runs on
EXPOSE 8086

# Set the entrypoint that handles environment variables
COPY ./deployment/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Set the entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]
