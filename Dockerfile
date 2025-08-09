FROM python:3.11-slim-bullseye

# Install system dependencies for PDF processing and PyTorch
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install compatible PyTorch CPU packages and dependencies
RUN pip install --no-cache-dir \
    "numpy<2" \
    torch==2.1.1+cpu torchvision==0.16.2+cpu torchaudio==2.0.2+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Install other Python dependencies
RUN pip install --no-cache-dir transformers pdfplumber requests flask

# Copy app code
COPY . /app
WORKDIR /app

# Command to run the app
CMD ["python", "app.py"]





