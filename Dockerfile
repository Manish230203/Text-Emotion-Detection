# Dockerfile for text-emotion-detection
# Based on your uploaded app at /mnt/data/app.py
# Produces a minimal image; adjust python version and dependencies as needed

FROM python:3.11-slim

WORKDIR /app

# Copy application files; using uploaded path as source in CI, but in repo context these should be present
COPY . /app

# If using a requirements file in repo, this installs it
RUN pip install --no-cache-dir -r requirements.txt || true

# If model files are needed, ensure they're copied into the image in your repo
# Example: COPY model /app/model

EXPOSE 5000

# Run the Flask app directly (adjust if you use gunicorn / uvicorn etc.)
CMD ["python", "app.py"]
