FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed for pdfplumber and requests
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install numpy < 2 to avoid compatibility issues
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir "numpy<2"

# Install PyTorch 2.1.1+cpu and related libs explicitly from official wheel repo
RUN pip install --no-cache-dir \
    torch==2.1.1+cpu torchvision==0.15.2+cpu torchaudio==2.0.2+cpu \
    -f https://download.pytorch.org/whl/torch_stable.html

# Install transformers and other Python dependencies
RUN pip install --no-cache-dir transformers pdfplumber requests flask

# Copy app source code
COPY . /app

EXPOSE 5000

CMD ["python", "app.py"]





