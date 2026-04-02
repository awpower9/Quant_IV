# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies for C++ build and PostgreSQL
# We need build-essential, cmake, and libpqxx for the C++ engine
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libpq-dev \
    libpqxx-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the package (This triggers CMake to build the C++ extension)
RUN pip install --no-cache-dir .

# Expose the port used by the Dash application
EXPOSE 8050

# Command to run the application via Gunicorn
# dashboard.app:server refers to the 'server' object in dashboard/app.py
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "--workers", "2", "--timeout", "120", "dashboard.app:server"]
