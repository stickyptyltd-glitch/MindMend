# MindMend Production Dockerfile
# ===============================

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Create mindmend user for security
RUN groupadd -r mindmend && useradd -r -g mindmend mindmend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    python3-dev \
    curl \
    git \
    nginx \
    supervisor \
    redis-server \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir gunicorn psycopg2-binary redis celery

# Install AI/ML specific packages
RUN pip install --no-cache-dir \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    transformers \
    sentence-transformers \
    accelerate

# Create necessary directories
RUN mkdir -p /var/log/mindmend /var/www/mindmend/uploads /app/logs && \
    chown -R mindmend:mindmend /var/log/mindmend /var/www/mindmend /app

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R mindmend:mindmend /app

# Create startup script
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

# Switch to mindmend user
USER mindmend

# Expose ports
EXPOSE 8000 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["/start.sh"]