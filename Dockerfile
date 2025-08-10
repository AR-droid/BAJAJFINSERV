# Use lightweight Python image
FROM python:3.10-slim

# Avoid Python buffering
ENV PYTHONUNBUFFERED=1

# Install system deps for spaCy
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download small spaCy model
RUN python -m spacy download en_core_web_sm

COPY . .

# Run app.py when container starts
CMD ["python", "app.py"]




