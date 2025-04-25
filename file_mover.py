# file_mover.py
import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def move_file(source_path, source_folder, destination_folder):
    """Move a file from the source path to the destination folder."""
    relative_path = os.path.relpath(source_path, start=source_folder)
    destination_path = os.path.join(destination_folder, relative_path)

    destination_dir = os.path.dirname(destination_path)
    os.makedirs(destination_dir, exist_ok=True)

    print(f"Moving file from {source_path} to {destination_path}")
    shutil.move(source_path, destination_path)

class MoveHandler(FileSystemEventHandler):
    def __init__(self, source_folder, destination_folder):
        self.source_folder = source_folder
        self.destination_folder = destination_folder

    def on_created(self, event):
        if not event.is_directory:
            move_file(event.src_path, self.source_folder, self.destination_folder)

def move_existing_files(source_folder, destination_folder):
    """Move all existing files from the source folder to the destination folder."""
    for root, _, files in os.walk(source_folder):
        for file in files:
            source_path = os.path.join(root, file)
            move_file(source_path, source_folder, destination_folder)

def monitor_folder(source_folder, destination_folder):
    event_handler = MoveHandler(destination_folder)
    observer = Observer()
    observer.schedule(event_handler, path=source_folder, recursive=True)
    observer.start()
    
    print(f"Monitoring folder: {source_folder}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python file_mover.py <source_folder> <destination_folder>")
        sys.exit(1)

    source_folder = sys.argv[1]
    destination_folder = sys.argv[2]

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder, exist_ok=True)

    # Move existing files before starting the monitor
    move_existing_files(source_folder, destination_folder)

    # Start monitoring the folder
    monitor_folder(source_folder, destination_folder)
