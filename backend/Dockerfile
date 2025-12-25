FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2 and curl for healthcheck
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY . .

# Expose port
EXPOSE 8000

# Run the application with auto-reload disabled for production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
