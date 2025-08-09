# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt (make sure you create this with needed packages)
COPY requirements.txt .

# Install system dependencies for pdfplumber and others
RUN apt-get update && apt-get install -y \
    build-essential \
    libpoppler-cpp-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Expose port (optional, default Flask port)
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]



