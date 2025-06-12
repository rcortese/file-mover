import logging
import pytest
from file_mover import smb_utils


class DummyThread:
    def __init__(self, target, args, daemon=False):
        self.target = target
        self.args = args
        self.daemon = daemon
        self.started = False

    def start(self):
        self.started = True

def test_ensure_mounted_calls_mount(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(smb_utils.os.path, "ismount", lambda p: False)
    monkeypatch.setattr(smb_utils.os, "makedirs", lambda p, exist_ok: calls.append("makedirs"))
    monkeypatch.setattr(smb_utils, "_mount", lambda *a, **k: calls.append((a, k)))

    smb_utils.ensure_mounted("//share", str(tmp_path))

    assert calls and calls[0] == "makedirs"
    assert calls[1][0][0] == "//share"


def test_monitor_remounts_when_lost(monkeypatch):
    events = {"mount_called": False, "sleep_called": 0}

    def fake_ismount(path):
        return False

    def fake_mount(*a, **k):
        events["mount_called"] = True

    def fake_sleep(i):
        events["sleep_called"] += 1
        raise StopIteration

    monkeypatch.setattr(smb_utils.os.path, "ismount", fake_ismount)
    monkeypatch.setattr(smb_utils, "_mount", fake_mount)
    monkeypatch.setattr(smb_utils.time, "sleep", fake_sleep)

    with pytest.raises(StopIteration):
        smb_utils._monitor("//share", "/mnt", interval=0)

    assert events["mount_called"]
    assert events["sleep_called"] == 1


def test_start_smb_monitor_starts_thread(monkeypatch, tmp_path):
    called = {}

    def fake_thread(target, args, daemon=False):
        called["target"] = target
        called["args"] = args
        return DummyThread(target, args, daemon)

    monkeypatch.setattr(smb_utils, "ensure_mounted", lambda *a, **k: called.setdefault("ensure", True))
    monkeypatch.setattr(smb_utils.threading, "Thread", fake_thread)

    smb_utils.start_smb_monitor("//share", str(tmp_path))

    assert called.get("ensure")
    assert called["target"] == smb_utils._monitor


def test_ensure_mounted_logs_error_on_failure(monkeypatch, caplog, tmp_path):
    monkeypatch.setattr(smb_utils.os.path, "ismount", lambda p: False)
    monkeypatch.setattr(smb_utils.os, "makedirs", lambda *a, **k: None)
    def fail_mount(*a, **k):
        raise RuntimeError("fail")

    monkeypatch.setattr(smb_utils, "_mount", fail_mount)

    with caplog.at_level(logging.ERROR):
        smb_utils.ensure_mounted("//share", str(tmp_path))

    assert "Failed to mount SMB share" in caplog.text


def test_monitor_logs_error_on_remount_failure(monkeypatch, caplog):
    monkeypatch.setattr(smb_utils.os.path, "ismount", lambda p: False)
    def fail_mount(*a, **k):
        raise RuntimeError("fail")

    monkeypatch.setattr(smb_utils, "_mount", fail_mount)
    def stop_sleep(_):
        raise StopIteration

    monkeypatch.setattr(smb_utils.time, "sleep", stop_sleep)

    with caplog.at_level(logging.ERROR), pytest.raises(StopIteration):
        smb_utils._monitor("//share", "/mnt", interval=0)

    assert "Remount failed" in caplog.text


def test_ensure_mounted_passes_credentials(monkeypatch, tmp_path):
    details = {}
    monkeypatch.setattr(smb_utils.os.path, "ismount", lambda p: False)
    monkeypatch.setattr(smb_utils.os, "makedirs", lambda *a, **k: None)

    def fake_mount(share, mount_point, username=None, password=None):
        details["user"] = username
        details["pass"] = password

    monkeypatch.setattr(smb_utils, "_mount", fake_mount)

    smb_utils.ensure_mounted("//share", str(tmp_path), "u", "p")

    assert details == {"user": "u", "pass": "p"}
