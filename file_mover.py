import os
import shutil
import time
import logging

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:  # pragma: no cover - fallback for environments without watchdog
    class FileSystemEventHandler:
        pass

    class Observer:
        def schedule(self, *_, **__):
            pass

        def start(self):
            pass

        def stop(self):
            pass

        def join(self):
            pass

class FileMoverHandler(FileSystemEventHandler):
    def __init__(self, source_folder, destination_folder):
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder, exist_ok=True)
        logging.info(
            "Initialized handler: %s -> %s",
            self.source_folder,
            self.destination_folder,
        )
        self.move_existing_files()

    def move_file(self, src_path):
        dest_path = os.path.join(
            self.destination_folder, os.path.relpath(src_path, self.source_folder)
        )
        dest_folder = os.path.dirname(dest_path)
        if not os.path.exists(dest_folder):
            logging.info("Creating destination folder: %s", dest_folder)
            os.makedirs(dest_folder, exist_ok=True)
        if os.path.exists(dest_path):
            file_name, file_extension = os.path.splitext(dest_path)
            i = 1
            while os.path.exists(f"{file_name}_{i}{file_extension}"):
                i += 1
            dest_path = f"{file_name}_{i}{file_extension}"
        try:
            shutil.move(src_path, dest_path)
            logging.info("Moved file from %s to %s", src_path, dest_path)
        except Exception as exc:
            logging.error("Failed to move %s to %s: %s", src_path, dest_path, exc)

    def move_existing_files(self):
        for root, _, files in os.walk(self.source_folder):
            for name in list(files):
                self.move_file(os.path.join(root, name))

    def on_created(self, event):
        logging.info("Event detected: File created - %s", event.src_path)
        self.process(event)

    def process(self, event):
        if not event.is_directory:
            self.move_file(event.src_path)

if __name__ == "__main__":
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if os.environ.get("SOURCE_FOLDER"):
        source_folder = os.environ["SOURCE_FOLDER"]
    elif len(sys.argv) > 1:
        source_folder = sys.argv[1]
    else:
        source_folder = "/source_folder"

    if os.environ.get("DEST_FOLDER"):
        destination_folder = os.environ["DEST_FOLDER"]
    elif len(sys.argv) > 2:
        destination_folder = sys.argv[2]
    else:
        destination_folder = "/destination_folder"

    event_handler = FileMoverHandler(source_folder, destination_folder)

    observer = Observer()
    observer.schedule(event_handler, path=source_folder, recursive=True)
    observer.start()
    logging.info("Monitoring %s for changes...", source_folder)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Stopping observer...")
    observer.join()
