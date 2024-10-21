# Use an official Python runtime as a parent image, specific for ARM architecture (Mac M1)
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for Flask to use main.py
ENV FLASK_APP=main.py

# Run the application
CMD ["flask", "run", "--host=0.0.0.0",  "--port=5000"]
