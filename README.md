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

### 1. Pull the Docker Container

Pull the latest version of the container to your local machine:

```bash
docker pull rcortese/file-mover:latest
```

### 2. Run the Docker Container

Replace `<source_folder>` and `<destination_folder>` in docker-compose.yml file with the paths you want to monitor and move files to. Run the Docker container using docker-compose:

```bash
docker-compose up -d
```

Alternatively, to run without docker-compose, replace `<source_folder>` and `<destination_folder>` with the paths you want to monitor and move files to and run:

```bash
docker run -d
  -v <source_folder>:/source_folder
  -v <destination_folder>:/destination_folder
  rcortese/file-mover:latest
```

### 3. Verify Operation

Once the container is running, it will monitor the source folder for new files and move them to the destination folder as they appear.

### 4. Stopping the Container

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
docker run -d
  -v /data/incoming:/source_folder
  -v /data/processed:/destination_folder
  rcortese/file-mover:latest
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
