# Use an official Python runtime as a parent image
FROM python:3.10-slim AS builder

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY /src /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV UVICORN_CMD "uvicorn main:app --host=0.0.0.0 --port=8000 --reload"

# Run app.py when the container launches
CMD ["sh", "-c", "$UVICORN_CMD"]
