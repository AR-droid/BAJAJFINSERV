FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install required packages
COPY requirements.txt .
RUN pip install --upgrade pip

# Install tensorflow (CPU-only)
RUN pip install tensorflow-cpu==2.13.0

# Install other python dependencies
RUN pip install -r requirements.txt

COPY . /app

CMD ["python", "app.py"]




