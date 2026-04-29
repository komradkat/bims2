# Build stage
FROM python:3.13-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy the application code for collectstatic
COPY . .

# Set environment variables for build
ENV PATH="/app/.venv/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE="config.settings.prod"
ENV SECRET_KEY="build-dummy-key"
ENV BIMS_PROFILE="production"

# Collect static files
RUN python manage.py collectstatic --noinput

# Final stage
FROM python:3.13-slim-bookworm

# Create a non-root user
RUN groupadd -r django && useradd -r -g django django

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv
# Copy static files from the builder stage
COPY --from=builder /app/staticfiles /app/staticfiles

# Copy the application code
COPY . .

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.prod
ENV BIMS_PROFILE=production
ENV BIMS_DATA_ROOT=/app/data
ENV PROD_BIMS_DATA_ROOT=/app/data
ENV PROD_DEBUG=False

# Ensure the data directory exists and is owned by the non-root user
RUN mkdir -p /app/data && chown django:django /app/data

# Change ownership of the app directory
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Default command: perform migrations and start server using waitress
CMD ["sh", "-c", "python manage.py migrate --noinput && python waitress_server.py"]
