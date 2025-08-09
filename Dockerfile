FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for PyTorch and torchvision
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libglib2.0-0 \
    libjpeg-dev \
    zlib1g-dev \
    libpoppler-cpp-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install numpy < 2 for compatibility
RUN pip install "numpy<2"

# Install PyTorch 2.1.1 CPU version along with torchvision and torchaudio
RUN pip install torch==2.1.1+cpu torchvision==0.15.2+cpu torchaudio==2.0.2+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Copy your application code
COPY . /app

# Install other Python dependencies
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python3", "app.py"]



