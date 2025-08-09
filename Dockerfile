FROM python:3.11-slim-bullseye

# Install system dependencies for PyTorch & PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

RUN pip install --no-cache-dir "numpy<2"
RUN pip install --no-cache-dir torch==2.1.1+cpu torchvision==0.15.2+cpu torchaudio==2.0.2+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install --no-cache-dir transformers pdfplumber requests flask

COPY . /app
WORKDIR /app

CMD ["python", "app.py"]





