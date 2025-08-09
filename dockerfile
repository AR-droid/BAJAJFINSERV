FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN python3 -m pip install --upgrade pip

RUN pip install torch==2.0.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python3", "app.py"]




