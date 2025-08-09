# Use official PyTorch CPU image with Python 3.11
FROM pytorch/pytorch:2.1.1-cpu

# Install system dependencies needed for PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip (optional but recommended)
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir transformers pdfplumber requests flask

# Copy your app source code into the container
COPY . /app
WORKDIR /app

# Expose port if needed (optional)
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]





