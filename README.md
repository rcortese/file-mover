# File Mover

This project is a containerized Python script that monitors a specified folder and its subfolders for new files. When new files are detected, they are moved to a destination folder while preserving the original directory structure.

## Features

- Monitors a folder and its subfolders for new files.
- Moves newly created files to a destination folder.
- Preserves the directory structure during the move.
- Dockerized application only has access to mapped folders.

## Requirements

- Docker (v20.10 or higher recommended)
- Docker Compose (optional, for easier management)

## Getting Started

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone <repository-url>
cd file_mover
```

### 2. Build the Docker Image

Build the Docker image using the provided Dockerfile:

```bash
docker build -t file-mover .
```

### 3. Run the Docker Container

Run the Docker container, replacing `<source_folder>` and `<destination_folder>` with the paths you want to monitor and move files to. Note that these paths need to be accessible from within the container.

```bash
docker run -v /path/on/host/source:/source_folder -v /path/on/host/destination:/destination_folder file-mover /source_folder /destination_folder
```

- `/path/on/host/source` is the path on your host machine that you want to monitor.
- `/path/on/host/destination` is the path on your host machine where you want the files to be moved.

### 4. Verify Operation

Once the container is running, it will monitor the source folder for new files and move them to the destination folder as they appear.

### 5. Stopping the Container

To stop the container, use:

```bash
docker ps  # Get the container ID or name
docker stop <container-id-or-name>
```

## Configuration

- **Source Folder**: The directory to be monitored for new files.
- **Destination Folder**: The directory where files will be moved, preserving the directory structure.

## Example

To monitor `/data/incoming` and move files to `/data/processed`, run:

```bash
docker run -v /data/incoming:/source_folder -v /data/processed:/destination_folder file-mover /source_folder /destination_folder
```

## Troubleshooting

- Ensure Docker is installed and running.
- Verify that the source and destination folders are correctly mounted and accessible.
- Check container logs for any errors:

  ```bash
  docker logs <container-id-or-name>
  ```

- **No files are being moved:** Ensure the `source_folder` and `destination_folder` paths are correctly set and that the container has appropriate permissions to access these directories.
- **Errors during build:** Verify that Docker and Docker Compose are correctly installed and up to date.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Watchdog](https://pypi.org/project/watchdog/) for filesystem monitoring.
