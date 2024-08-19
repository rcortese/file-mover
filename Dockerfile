# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY file_mover.py ./

# Set the entry point for the container
ENTRYPOINT ["python", "file_mover.py"]

# Default command to run the script for source and destination folders
CMD ["/source_folder", "/destination_folder"]
