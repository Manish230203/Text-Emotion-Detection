# Dockerfile for text-emotion-detection
# Builds a minimal image that runs app.py (Flask app assumed)

FROM python:3.11-slim

WORKDIR /app

# Copy application files into image
COPY . /app

# Install dependencies if requirements.txt exists
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Ensure model folder exists (if you copy model into repo)
# COPY model /app/model

EXPOSE 5000

# Use a production WSGI server if desired (gunicorn recommended). Default: run app.py directly.
# For production, consider: CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
CMD ["python", "app.py"]
