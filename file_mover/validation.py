import os
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class DestinationValidationConfig:
    require_mount: bool = False
    expected_fstype: str | None = None
    expected_source: str | None = None

    @property
    def enabled(self) -> bool:
        return self.require_mount or bool(self.expected_fstype) or bool(
            self.expected_source
        )


@dataclass(frozen=True)
class MountInfo:
    mount_point: str
    fstype: str
    source: str


def load_destination_validation_config(
    environ: dict[str, str] | None = None,
) -> DestinationValidationConfig:
    env = os.environ if environ is None else environ
    return DestinationValidationConfig(
        require_mount=_is_truthy(env.get("DEST_REQUIRE_MOUNT")),
        expected_fstype=_normalize_optional(env.get("DEST_EXPECTED_FSTYPE")),
        expected_source=_normalize_optional(env.get("DEST_EXPECTED_SOURCE")),
    )


def validate_destination(
    destination_folder: str,
    config: DestinationValidationConfig,
    mount_reader: Callable[[], str] | None = None,
) -> None:
    if not config.enabled:
        return

    destination = os.path.normpath(destination_folder)
    mount_info = get_mount_info(destination, mount_reader=mount_reader)

    if config.require_mount and (
        mount_info is None or os.path.normpath(mount_info.mount_point) != destination
    ):
        raise ValueError(
            "DEST_MOUNT_INVALID: destination is not mounted at the expected path"
        )

    if config.expected_fstype and (
        mount_info is None or mount_info.fstype != config.expected_fstype
    ):
        actual_fstype = mount_info.fstype if mount_info else "missing"
        raise ValueError(
            "DEST_FSTYPE_MISMATCH: expected "
            f"{config.expected_fstype}, got {actual_fstype}"
        )

    if config.expected_source and (
        mount_info is None or mount_info.source != config.expected_source
    ):
        actual_source = mount_info.source if mount_info else "missing"
        raise ValueError(
            "DEST_SOURCE_MISMATCH: expected "
            f"{config.expected_source}, got {actual_source}"
        )


def get_mount_info(
    path: str,
    mount_reader: Callable[[], str] | None = None,
) -> MountInfo | None:
    mounts = parse_mounts((mount_reader or _read_proc_mounts)())
    normalized_path = os.path.normpath(path)
    matches = []

    for mount in mounts:
        mount_point = os.path.normpath(mount.mount_point)
        if normalized_path == mount_point or normalized_path.startswith(
            f"{mount_point}{os.sep}"
        ):
            matches.append((len(mount_point), mount))

    if not matches:
        return None

    return max(matches, key=lambda item: item[0])[1]


def parse_mounts(mounts_text: str) -> list[MountInfo]:
    mounts = []

    for line in mounts_text.splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        mounts.append(
            MountInfo(
                mount_point=_unescape_mount_field(parts[1]),
                fstype=parts[2],
                source=_unescape_mount_field(parts[0]),
            )
        )

    return mounts


def _read_proc_mounts() -> str:
    with open("/proc/mounts", "r", encoding="utf-8") as mounts_file:
        return mounts_file.read()


def _is_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _unescape_mount_field(value: str) -> str:
    return value.replace("\\040", " ")
