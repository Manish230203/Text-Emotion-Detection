# Dockerfile for text-emotion-detection
FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Add this line 👇
RUN pip install --no-cache-dir pytest pytest-cov

EXPOSE 5000

CMD ["python", "app.py"]
