import os
import pytest

from file_mover import (
    DestinationValidationConfig,
    FileMoverHandler,
    get_mount_info,
    load_destination_validation_config,
    parse_mounts,
    validate_destination,
)
from file_mover.__main__ import _load_runtime_config


class DummyEvent:
    def __init__(self, src_path, is_directory=False):
        self.src_path = str(src_path)
        self.is_directory = is_directory


def test_process_moves_file(tmp_path):
    src = tmp_path / 'src'
    dest = tmp_path / 'dest'
    src.mkdir()
    dest.mkdir()

    # create a file in the source directory
    file_path = src / 'sample.txt'
    file_path.write_text('content')

    handler = FileMoverHandler(str(src), str(dest))
    event = DummyEvent(file_path)

    handler.process(event)

    assert not file_path.exists()
    moved_path = dest / 'sample.txt'
    assert moved_path.exists()
    assert moved_path.read_text() == 'content'


def test_process_renames_existing_file(tmp_path):
    src = tmp_path / 'src'
    dest = tmp_path / 'dest'
    src.mkdir()
    dest.mkdir()

    # existing file in destination
    existing = dest / 'duplicate.txt'
    existing.write_text('old')

    new_file = src / 'duplicate.txt'
    new_file.write_text('new')

    handler = FileMoverHandler(str(src), str(dest))
    event = DummyEvent(new_file)

    handler.process(event)

    assert not new_file.exists()
    original_path = dest / 'duplicate.txt'
    renamed_path = dest / 'duplicate_1.txt'

    assert original_path.exists()
    assert renamed_path.exists()
    assert renamed_path.read_text() == 'new'


def test_existing_files_moved_on_init(tmp_path):
    src = tmp_path / 'src'
    dest = tmp_path / 'dest'
    src.mkdir()
    dest.mkdir()

    existing = src / 'old.txt'
    existing.write_text('data')

    FileMoverHandler(str(src), str(dest))

    assert not existing.exists()
    moved = dest / 'old.txt'
    assert moved.exists()
    assert moved.read_text() == 'data'


def test_parse_mounts_unescapes_fields():
    mounts = parse_mounts('/dev/sda1 /media/My\\040Disk ext4 rw 0 0\n')

    assert mounts[0].mount_point == '/media/My Disk'
    assert mounts[0].source == '/dev/sda1'
    assert mounts[0].fstype == 'ext4'


def test_get_mount_info_uses_most_specific_match():
    mounts_text = '\n'.join([
        'overlay / overlay rw 0 0',
        '//media.lan/home-assistant /destination_folder cifs rw 0 0',
        '//media.lan/home-assistant /destination_folder/camera cifs rw 0 0',
    ])

    mount = get_mount_info('/destination_folder/camera/file.txt', lambda: mounts_text)

    assert mount is not None
    assert mount.mount_point == '/destination_folder/camera'


def test_load_destination_validation_config_defaults_disabled():
    config = load_destination_validation_config({})

    assert config.enabled is False
    assert config.require_mount is False
    assert config.expected_fstype is None
    assert config.expected_source is None


def test_load_destination_validation_config_reads_env():
    config = load_destination_validation_config({
        'DEST_REQUIRE_MOUNT': 'true',
        'DEST_EXPECTED_FSTYPE': 'cifs',
        'DEST_EXPECTED_SOURCE': '//media.lan/home-assistant',
    })

    assert config.require_mount is True
    assert config.expected_fstype == 'cifs'
    assert config.expected_source == '//media.lan/home-assistant'


def test_validate_destination_allows_local_usage_when_disabled():
    validate_destination(
        '/destination_folder',
        DestinationValidationConfig(),
        mount_reader=lambda: 'overlay / overlay rw 0 0\n',
    )


def test_validate_destination_requires_mountpoint():
    config = DestinationValidationConfig(require_mount=True)

    with pytest.raises(ValueError, match='DEST_MOUNT_INVALID'):
        validate_destination(
            '/destination_folder',
            config,
            mount_reader=lambda: 'overlay / overlay rw 0 0\n',
        )


def test_validate_destination_requires_expected_fstype():
    config = DestinationValidationConfig(expected_fstype='cifs')

    with pytest.raises(ValueError, match='DEST_FSTYPE_MISMATCH'):
        validate_destination(
            '/destination_folder',
            config,
            mount_reader=lambda: '/dev/sda1 /destination_folder ext4 rw 0 0\n',
        )


def test_validate_destination_requires_expected_source():
    config = DestinationValidationConfig(expected_source='//media.lan/home-assistant')

    with pytest.raises(ValueError, match='DEST_SOURCE_MISMATCH'):
        validate_destination(
            '/destination_folder',
            config,
            mount_reader=lambda: '//wrong/source /destination_folder cifs rw 0 0\n',
        )


def test_validate_destination_accepts_expected_mount():
    config = DestinationValidationConfig(
        require_mount=True,
        expected_fstype='cifs',
        expected_source='//media.lan/home-assistant',
    )

    validate_destination(
        '/destination_folder',
        config,
        mount_reader=lambda: (
            '//media.lan/home-assistant /destination_folder cifs rw 0 0\n'
        ),
    )


def test_load_runtime_config_defaults():
    config = _load_runtime_config(['file-mover'], {})

    assert config.source_folder == '/source_folder'
    assert config.destination_folder == '/destination_folder'
    assert config.validate_only is False


def test_load_runtime_config_reads_positionals():
    config = _load_runtime_config(
        ['file-mover', '/tmp/src', '/tmp/dest'],
        {},
    )

    assert config.source_folder == '/tmp/src'
    assert config.destination_folder == '/tmp/dest'
    assert config.validate_only is False


def test_load_runtime_config_honors_validation_flag():
    config = _load_runtime_config(
        ['file-mover', '--validate-destination', '/tmp/src', '/tmp/dest'],
        {},
    )

    assert config.source_folder == '/tmp/src'
    assert config.destination_folder == '/tmp/dest'
    assert config.validate_only is True


def test_load_runtime_config_prefers_env_vars():
    config = _load_runtime_config(
        ['file-mover', '--validate-destination', '/tmp/src', '/tmp/dest'],
        {
            'SOURCE_FOLDER': '/env/src',
            'DEST_FOLDER': '/env/dest',
        },
    )

    assert config.source_folder == '/env/src'
    assert config.destination_folder == '/env/dest'
    assert config.validate_only is True
