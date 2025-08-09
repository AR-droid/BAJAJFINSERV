FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip

# Install both torch CPU and tensorflow CPU:
RUN pip install torch==2.1.1+cpu torchvision==0.15.2+cpu torchaudio==2.0.2+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install tensorflow-cpu==2.13.0

# Then install other deps
RUN pip install -r requirements.txt

COPY . /app

CMD ["python", "app.py"]




