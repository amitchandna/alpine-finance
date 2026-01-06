FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY django_project/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY django_project/ .

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "upper_lake.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
