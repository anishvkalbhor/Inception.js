<<<<<<< HEAD
# Python FastAPI backend Dockerfile
=======
# Basic Python backend Dockerfile
>>>>>>> anish
FROM python:3.11-slim

# Set working directory
WORKDIR /app

<<<<<<< HEAD
# Install system dependencies for PDF processing and other libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
=======
# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
>>>>>>> anish
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

<<<<<<< HEAD
# Create necessary directories
RUN mkdir -p /app/data/local_storage/uploads \
    /app/data/local_storage/processed \
    /app/data/local_storage/schemes \
    /app/data/local_storage/scraped_moe_monthly_achivements
=======
# Create data directory
RUN mkdir -p /app/data/local_storage
>>>>>>> anish

# Expose port
EXPOSE 8000

<<<<<<< HEAD
# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
=======
# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "run_server.py"]
>>>>>>> anish
