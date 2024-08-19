# file_mover.py
import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MoveHandler(FileSystemEventHandler):
    def __init__(self, destination_folder):
        self.destination_folder = destination_folder

    def on_created(self, event):
        if not event.is_directory:
            source_path = event.src_path
            relative_path = os.path.relpath(source_path, start=source_folder)
            destination_path = os.path.join(self.destination_folder, relative_path)

            destination_dir = os.path.dirname(destination_path)
            os.makedirs(destination_dir, exist_ok=True)

            print(f"Moving file from {source_path} to {destination_path}")
            shutil.move(source_path, destination_path)

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

    monitor_folder(source_folder, destination_folder)
