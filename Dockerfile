FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .

# Install runtime dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

EXPOSE 5000

# Production WSGI server
CMD ["gunicorn", "--workers", "4", "--timeout", "120", "--bind", "0.0.0.0:5000", "app:app"]
