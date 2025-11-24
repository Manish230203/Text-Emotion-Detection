# Base Python image
FROM python:3.10-slim-bullseye

# Set working directory
WORKDIR /app

# Environment variables to make Python behave nicely in containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# (Optional) System dependencies - extend if you use numpy/pandas/etc
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY requirements.txt /app/

# Install Python dependencies + test libs
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install pytest pytest-cov

# Copy project files
COPY . /app/

# Expose app port (change if your app uses another)
EXPOSE 5000

# Run the app
# If you're using Flask with "app.py", this usually works.
# Change this if you use a different entrypoint, e.g. "gunicorn main:app"
CMD ["python", "app.py"]
