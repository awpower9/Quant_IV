# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for C++ build and PostgreSQL
# We need build-essential, cmake, and libpqxx for the C++ engine
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    pkg-config \
    libpq-dev \
    libpqxx-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the package (This triggers CMake to build the C++ extension)
# After installation, we remove the source folders to prevent "package shadowing"
# where Python tries to import the local folder instead of the compiled version in site-packages.
RUN pip install --no-cache-dir . && \
    rm -rf quantiv engine bindings tests CMakeLists.txt setup.py

# Expose the port used by the Dash application
EXPOSE 8050

# Command to run the application via Gunicorn
# dashboard.app:server refers to the 'server' object in dashboard/app.py
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "--workers", "2", "--timeout", "120", "dashboard.app:server"]
