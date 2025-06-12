# File Mover

This project is a containerized Python script that monitors a specified folder and its subfolders for files. Existing files are moved when the program starts, and any new files detected afterward are moved to a destination folder while preserving the original directory structure.

## Features

- Monitors a folder and its subfolders for new files.
- Moves newly created files to a destination folder.
- Moves existing files on startup.
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

The repository includes a minimal `examples/docker-compose.yml` file which can
be used as a template. Replace `<source_folder>` and `<destination_folder>` in
that file with the paths you want to monitor and move files to, then run:

```bash
docker-compose -f examples/docker-compose.yml up -d
```

Alternatively, to run without docker-compose, replace `<source_folder>` and `<destination_folder>` with the paths you want to monitor and move files to and run:

```bash
docker run -d \
  -v <source_folder>:/source_folder \
  -v <destination_folder>:/destination_folder \
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
- The script also respects the `SOURCE_FOLDER` and `DEST_FOLDER` environment variables. If set, these values override command-line arguments and defaults.
- To use an SMB share directly, set `DEST_SMB` to the share path (for example
  `//server/share`). Optional `SMB_USERNAME` and `SMB_PASSWORD` variables can be
  supplied for authentication. The application mounts the share inside the
  container at `/destination_folder` and will automatically attempt to
  reconnect if the mount is lost.

## Example

To monitor `/data/incoming` and move files to `/data/processed`, run:

```bash
docker run -d \
  -v /data/incoming:/source_folder \
  -v /data/processed:/destination_folder \
  rcortese/file-mover:latest
```

### Example using an SMB share

The `examples/docker-compose-smb.yml` file demonstrates how to configure the
container when the destination is an SMB share. It sets the required
environment variables so the share is mounted at `/destination_folder` inside
the container. Start it with:

```bash
docker compose -f examples/docker-compose-smb.yml up -d
```

## Troubleshooting

- Ensure Docker is installed and running.
- Verify that the source and destination folders are correctly mounted and accessible.
- Check container logs for any errors:

  ```bash
  docker logs <container-id-or-name>
  ```
- The application uses Python logging to report actions and errors.

- **No files are being moved:** Ensure the `source_folder` and `destination_folder` paths are correctly set and that the container has appropriate permissions to access these directories.
- **Errors during build:** Verify that Docker and Docker Compose are correctly installed and up to date.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Watchdog](https://pypi.org/project/watchdog/) for filesystem monitoring.
