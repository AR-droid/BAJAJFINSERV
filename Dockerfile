# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed by torch & pdfplumber
RUN apt-get update && apt-get install -y \
    build-essential libglib2.0-0 curl && \
    rm -rf /var/lib/apt/lists/*

# Copy your application code
COPY . /app

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install PyTorch 2.1 CPU version (use --pre for latest pre-release if needed)
RUN pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu

# Install other Python dependencies from requirements.txt
RUN pip install -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]





