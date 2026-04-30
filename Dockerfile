# Build stage
FROM python:3.13-slim-bookworm AS builder

# Install build essentials and Nuitka requirements
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    ccache \
    patchelf \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

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

# Install Nuitka via uv
RUN uv pip install nuitka

# Copy the application code
COPY . .

# Set environment variables for build
ENV PATH="/app/.venv/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE="config.settings.prod"
ENV SECRET_KEY="build-dummy-key"
ENV BIMS_PROFILE="production"

# Collect static files
RUN python manage.py collectstatic --noinput

# Compile with Nuitka
RUN python -m nuitka \
    --standalone \
    --assume-yes-for-downloads \
    --include-package=apps \
    --include-package=config \
    --include-package=django \
    --include-package=whitenoise \
    --include-package=psycopg \
    --include-package-data=django \
    --module-parameter=django-settings-module=config.settings.prod \
    --output-dir=nuitka_build \
    --output-filename=BIMS2_Server \
    waitress_server.py

# Final stage
FROM python:3.13-slim-bookworm

# Install WeasyPrint runtime dependencies
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN groupadd -r django && useradd -r -g django django

WORKDIR /app

# Copy the Nuitka compiled distribution folder contents
COPY --from=builder /app/nuitka_build/waitress_server.dist /app/dist

# Copy data files alongside the binary
COPY --from=builder /app/static /app/dist/static
COPY --from=builder /app/templates /app/dist/templates
COPY --from=builder /app/staticfiles /app/dist/staticfiles
COPY --from=builder /app/VERSION /app/dist/VERSION

# Set environment variables
ENV PATH="/app/dist:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.prod
ENV BIMS_PROFILE=production
ENV BIMS_DATA_ROOT=/app/data
ENV PROD_BIMS_DATA_ROOT=/app/data
ENV PROD_DEBUG=False
ENV BIMS_HOST=0.0.0.0

# Ensure the data directory exists and is owned by the non-root user
RUN mkdir -p /app/data && chown django:django /app/data
RUN chown -R django:django /app/dist

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Default command: run the compiled binary
CMD ["/app/dist/BIMS2_Server"]
