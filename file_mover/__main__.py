import logging
import os
import sys
import time
from dataclasses import dataclass

from .handler import FileMoverHandler, Observer
from .validation import (
    DestinationValidationConfig,
    load_destination_validation_config,
    validate_destination,
)


@dataclass(frozen=True)
class RuntimeConfig:
    source_folder: str
    destination_folder: str
    validate_only: bool


def _validate_destination_or_exit(
    destination_folder: str,
    validation_config: DestinationValidationConfig,
) -> None:
    try:
        validate_destination(destination_folder, validation_config)
    except ValueError as exc:
        logging.error("%s", exc)
        sys.exit(1)

    if validation_config.enabled:
        logging.info(
            "DEST_VALIDATION_OK: destination checks passed for %s",
            destination_folder,
        )


def _load_runtime_config(argv: list[str], environ: dict[str, str]) -> RuntimeConfig:
    validate_only = False
    positional_args = []

    for arg in argv[1:]:
        if arg == "--validate-destination":
            validate_only = True
            continue
        positional_args.append(arg)

    if environ.get("SOURCE_FOLDER"):
        source_folder = environ["SOURCE_FOLDER"]
    elif positional_args:
        source_folder = positional_args[0]
    else:
        source_folder = "/source_folder"

    if environ.get("DEST_FOLDER"):
        destination_folder = environ["DEST_FOLDER"]
    elif len(positional_args) > 1:
        destination_folder = positional_args[1]
    else:
        destination_folder = "/destination_folder"

    return RuntimeConfig(
        source_folder=source_folder,
        destination_folder=destination_folder,
        validate_only=validate_only,
    )


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    runtime_config = _load_runtime_config(sys.argv, os.environ)
    validation_config = load_destination_validation_config()

    if runtime_config.validate_only:
        _validate_destination_or_exit(
            runtime_config.destination_folder,
            validation_config,
        )
        return

    _validate_destination_or_exit(
        runtime_config.destination_folder,
        validation_config,
    )

    event_handler = FileMoverHandler(
        runtime_config.source_folder,
        runtime_config.destination_folder,
    )

    observer = Observer()
    observer.schedule(
        event_handler,
        path=runtime_config.source_folder,
        recursive=True,
    )
    observer.start()
    logging.info("Monitoring %s for changes...", runtime_config.source_folder)
    try:
        while True:
            time.sleep(1)
            if not observer.is_alive():
                logging.error(
                    "Observer thread died unexpectedly, exiting for restart..."
                )
                observer.stop()
                sys.exit(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Stopping observer...")
    observer.join()


if __name__ == "__main__":
    main()
