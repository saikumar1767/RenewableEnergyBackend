# Use the official Python image as base image
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Copy the backend application code into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port on which the Flask application will run
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "run.py"]
