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
