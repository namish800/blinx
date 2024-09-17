# Use an official Python base image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project files
COPY . .

# Expose the port your FastAPI app listens on (default is 8000)
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--reload"]