import logging
import os
import sys
import time

from .handler import FileMoverHandler, Observer

def main() -> None:
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


if __name__ == "__main__":
    main()
