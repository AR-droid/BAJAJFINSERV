FROM python:3.11-slim-bullseye

# Install system dependencies for PDF processing and PyTorch
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install PyTorch CPU packages without version pins
RUN pip install --no-cache-dir torch torchvision torchaudio -f https://download.pytorch.org/whl/torch_stable.html

# Install other Python dependencies without versions
RUN pip install --no-cache-dir transformers pdfplumber requests flask

# Copy app code
COPY . /app
WORKDIR /app

# Command to run the app
CMD ["python", "app.py"]




