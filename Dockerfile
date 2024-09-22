# Use the official Python 3.10 Slim image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the dependencies listed in requirements.txt without caching
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory to the working directory
COPY . .

# Define the command to run when the container starts
# This command runs the Uvicorn server with the specified settings
CMD ["uvicorn", "backend.backend:app", "--host", "0.0.0.0", "--port", "8000"]