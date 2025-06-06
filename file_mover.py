import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileMoverHandler(FileSystemEventHandler):
    def __init__(self, source_folder, destination_folder):
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder, exist_ok=True)

    def on_created(self, event):
        print(f"Event detected: File created - {event.src_path}")
        self.process(event)

    def process(self, event):
        if not event.is_directory:
            dest_path = os.path.join(self.destination_folder, os.path.relpath(event.src_path, self.source_folder))
            dest_folder = os.path.dirname(dest_path)
            if not os.path.exists(dest_folder):
                print(f"Creating destination folder: {dest_folder}")
                os.makedirs(dest_folder, exist_ok=True)
            if os.path.exists(dest_path):
                file_name, file_extension = os.path.splitext(dest_path)
                i = 1
                while os.path.exists('{}_{}{}'.format(file_name, i, file_extension)):
                    i += 1
                dest_path = '{}_{}{}'.format(file_name, i, file_extension)
            print(f"Moving file from {event.src_path} to {dest_path}")
            shutil.move(event.src_path, dest_path)

if __name__ == "__main__":
    import sys
    # source_folder and destination_folder are set to /source_folder and /destination_folder
    # when no arguments are provided
    if len(sys.argv) > 2:
        source_folder = sys.argv[1]
        destination_folder = sys.argv[2]
    else:
        source_folder = '/source_folder'
        destination_folder = '/destination_folder'

    event_handler = FileMoverHandler(source_folder, destination_folder)

    observer = Observer()
    observer.schedule(event_handler, path=source_folder, recursive=True)
    observer.start()
    print(f"Monitoring {source_folder} for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Stopping observer...")
    observer.join()
