import os
import shutil
import logging

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:  # pragma: no cover - fallback for environments without watchdog
    class FileSystemEventHandler:  # type: ignore
        pass

    class Observer:  # type: ignore
        def __init__(self):
            self._alive = False

        def schedule(self, *_, **__):
            pass

        def start(self):
            self._alive = True

        def stop(self):
            self._alive = False

        def is_alive(self):
            return self._alive

        def join(self):
            pass


class FileMoverHandler(FileSystemEventHandler):
    def __init__(self, source_folder: str, destination_folder: str) -> None:
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

    def move_file(self, src_path: str) -> None:
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
        except Exception as exc:  # pragma: no cover - safety net
            logging.error("Failed to move %s to %s: %s", src_path, dest_path, exc)

    def move_existing_files(self) -> None:
        for root, _, files in os.walk(self.source_folder):
            for name in list(files):
                self.move_file(os.path.join(root, name))

    def on_created(self, event) -> None:
        logging.info("Event detected: File created - %s", event.src_path)
        self.process(event)

    def process(self, event) -> None:
        if not getattr(event, "is_directory", False):
            self.move_file(event.src_path)
