import logging
import os
import subprocess
import threading
import time


def _mount(share: str, mount_point: str, username: str | None = None, password: str | None = None) -> None:
    """Mount the SMB share using mount.cifs."""
    opts = []
    if username:
        opts.append(f"username={username}")
    if password:
        opts.append(f"password={password}")
    cmd = ["mount", "-t", "cifs", share, mount_point]
    if opts:
        cmd += ["-o", ",".join(opts)]
    logging.info("Running %s", " ".join(cmd))
    subprocess.run(cmd, check=True)


def ensure_mounted(share: str, mount_point: str, username: str | None = None, password: str | None = None) -> None:
    """Ensure the SMB share is mounted."""
    if not os.path.ismount(mount_point):
        try:
            os.makedirs(mount_point, exist_ok=True)
            _mount(share, mount_point, username, password)
            logging.info("Mounted SMB share %s at %s", share, mount_point)
        except Exception as exc:  # pragma: no cover - mount failures not tested
            logging.error("Failed to mount SMB share: %s", exc)


def _monitor(share: str, mount_point: str, username: str | None = None, password: str | None = None, interval: int = 30) -> None:
    """Periodically check if the mount is active and remount if needed."""
    while True:
        if not os.path.ismount(mount_point):
            logging.warning("SMB mount lost, attempting to remount...")
            try:
                _mount(share, mount_point, username, password)
                logging.info("Remounted SMB share %s", share)
            except Exception as exc:  # pragma: no cover - mount failures not tested
                logging.error("Remount failed: %s", exc)
        time.sleep(interval)


def start_smb_monitor(share: str, mount_point: str, username: str | None = None, password: str | None = None, interval: int = 30) -> None:
    """Start a background thread that ensures the SMB share stays mounted."""
    ensure_mounted(share, mount_point, username, password)
    thread = threading.Thread(target=_monitor, args=(share, mount_point, username, password, interval), daemon=True)
    thread.start()
