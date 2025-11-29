# Dockerfile (fixed)
FROM python:3.11-slim

WORKDIR /app

# Copy code and requirements
COPY . /app

# Install runtime deps. Ensure you have requirements.txt committed.
# IMPORTANT: pin scikit-learn to the version used to pickle your model (example below).
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Install test tools used by CI (ok to include)
RUN pip install --no-cache-dir pytest pytest-cov

EXPOSE 5000

# Run the Flask/WSGI app via gunicorn. Ensure your Flask app object is "app" in app.py
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
