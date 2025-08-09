FROM python:3.11

RUN apt-get update && apt-get install -y \
    build-essential \
    libpoppler-cpp-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir \
    torch==2.0.1+cpu torchvision==0.15.2+cpu torchaudio==2.0.2+cpu -f https://download.pytorch.org/whl/torch_stable.html

RUN pip install --no-cache-dir transformers pdfplumber flask requests

COPY app.py /app/app.py

WORKDIR /app

CMD ["python", "app.py"]





