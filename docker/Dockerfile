# ============================================
# Dockerfile for Production Environment
# ============================================
# This Dockerfile sets up a lightweight Python environment optimized for production.

# -------------------------------------------
# Base Image Configuration
# -------------------------------------------
# Use the official Python 3.13 slim image as the base image.
# The slim variant is minimal and avoids unnecessary components, reducing image size.
FROM python:3.14-slim

# -------------------------------------------
# Environment Variable Setup
# -------------------------------------------
# Define key environment variables to configure paths and Python behavior:
# - HOMEDIR: Specifies the directory where the application will reside within the container.
# - PYTHONPATH: Ensures /src is included in Python's module search path, simplifying imports.
ENV HOMEDIR=/cinebooker-dir/src \
    PYTHONPATH="/cinebooker-dir:/cinebooker-dir/src"

# Accept an argument for the environment (e.g., "prod" or "local").
ARG ENVIRONMENT

# -------------------------------------------
# Set Working Directory
# -------------------------------------------
# Define the working directory for subsequent commands to ensure all file paths are relative to it.
WORKDIR $HOMEDIR

# -------------------------------------------
# Copy Application Source Code
# -------------------------------------------
# Copy the application source code from the host machine's 'src' directory to the container's HOMEDIR.
COPY ../src $HOMEDIR

# -------------------------------------------
# Install System-Level Dependencies
# -------------------------------------------
# - gcc: GNU Compiler Collection for compiling dependencies.
# - libpq-dev: PostgreSQL library for database interactions.
# - git: For cloning repositories.
RUN apt-get update && apt-get install --assume-yes \
  gcc \
  libpq-dev \
  git \
  && rm -rf /var/lib/apt/lists/*

# -------------------------------------------
# Install Python Dependencies
# -------------------------------------------
RUN pip install --no-cache-dir --upgrade pip uv \
    && if [ "$ENVIRONMENT" = "local" ] ; then uv sync --dev ; else uv sync --no-dev; fi

# -------------------------------------------
# Initialize Git Repository (Optional)
# -------------------------------------------
# Create a Git repository within the container.
# This step is optional but useful if tools like pre-commit hooks or versioning rely on Git.
RUN git init

# -------------------------------------------
# Copy Custom Executable Scripts
# -------------------------------------------
# Copy additional custom executable scripts into the '/usr/local/bin' directory.
# This makes the scripts accessible system-wide.
COPY docker/bin/* /usr/local/bin/

# -------------------------------------------
# Default Command
# -------------------------------------------
# Define the command to run when the container starts.
# Use a production-ready server like Uvicorn.
CMD ["/usr/local/bin/uvicorn.sh"]
