FROM python:3.11-slim

WORKDIR /app

# Install system deps needed by torch & pdfplumber
RUN apt-get update && apt-get install -y \
    build-essential libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy code and requirements
COPY . /app

# Upgrade pip first
RUN python -m pip install --upgrade pip

# Install PyTorch CPU wheels (match your torch version here)
RUN pip install torch==2.0.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Install the rest of your Python dependencies (do NOT include torch here)
RUN pip install -r requirements.txt

# Expose Flask default port (5000)
EXPOSE 5000

# Run your app
CMD ["python", "app.py"]



