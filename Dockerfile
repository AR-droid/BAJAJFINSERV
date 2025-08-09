FROM python:3.11-slim-bullseye

# System dependencies for PyTorch, PDF, and general
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 libsm6 libxext6 libxrender-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Install PyTorch CPU and torchvision (without fixed minor versions, to avoid conflicts)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install transformers and other deps
RUN pip install --no-cache-dir transformers pdfplumber requests flask

# Copy app and set workdir
COPY . /app
WORKDIR /app

# Expose port if needed
EXPOSE 5000

# Run your app
CMD ["python", "app.py"]



