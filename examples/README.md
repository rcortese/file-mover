# Examples

This directory contains sample configuration files for running **file-mover**.

## SMB share

`docker-compose-smb.yml` shows how to start the container with an SMB share
as the destination. Adjust the `DEST_SMB`, `SMB_USERNAME`, and `SMB_PASSWORD`
values to match your environment and map a local folder to `/source_folder`.
