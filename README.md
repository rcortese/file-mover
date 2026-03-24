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

Replace `<source_folder>` and `<destination_folder>` in docker-compose.yml file with the paths you want to monitor and move files to. Run the Docker container using docker-compose:

```bash
docker-compose up -d
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
- Optional destination validation can be enabled with:
  - `DEST_REQUIRE_MOUNT=true` to require `/destination_folder` itself to be a mountpoint
  - `DEST_EXPECTED_FSTYPE=cifs` to require a specific filesystem type
  - `DEST_EXPECTED_SOURCE=//media.lan/home-assistant` to require a specific mount source

### SMB/CIFS Safety Mode

By default, `file-mover` keeps its current simple behavior and works with ordinary local folders.

If your destination is supposed to be an SMB/CIFS mount, enable destination validation so the container fails fast instead of silently writing to the wrong local path:

```bash
docker run -d \
  -e DEST_REQUIRE_MOUNT=true \
  -e DEST_EXPECTED_FSTYPE=cifs \
  -e DEST_EXPECTED_SOURCE=//media.lan/home-assistant \
  -v /data/incoming:/source_folder \
  -v /mnt/media_home_assistant:/destination_folder \
  rcortese/file-mover:latest
```

When validation is enabled, the container exits with a non-zero status and logs a stable error marker such as:

- `DEST_MOUNT_INVALID`
- `DEST_FSTYPE_MISMATCH`
- `DEST_SOURCE_MISMATCH`

The image also includes a Docker healthcheck that reuses the same validation logic. If you do not set any of the validation variables, the healthcheck remains effectively passive and local-folder setups keep working unchanged.

## Example

To monitor `/data/incoming` and move files to `/data/processed`, run:

```bash
docker run -d \
  -v /data/incoming:/source_folder \
  -v /data/processed:/destination_folder \
  rcortese/file-mover:latest
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
- **Files appear to move, but the destination SMB was down:** enable `DEST_REQUIRE_MOUNT` and `DEST_EXPECTED_FSTYPE=cifs` so the container fails fast instead of writing to an unintended local directory.
- **Errors during build:** Verify that Docker and Docker Compose are correctly installed and up to date.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Watchdog](https://pypi.org/project/watchdog/) for filesystem monitoring.
