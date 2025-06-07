# Use the official Python image from the Docker Hub
FROM python:3.12.5-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY file_mover ./file_mover

# Set the entry point for the container
ENTRYPOINT ["python", "-m", "file_mover"]

# Default command to run the script for source and destination folders
CMD ["/source_folder", "/destination_folder"]
