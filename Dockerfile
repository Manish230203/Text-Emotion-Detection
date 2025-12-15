# ---- Test Stage ----
FROM python:3.11-slim AS test

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pytest pytest-cov

COPY . .

# Run tests
RUN pytest --maxfail=1 --disable-warnings --cov=. --cov-report=xml

# ----- Production Stage ----
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]
