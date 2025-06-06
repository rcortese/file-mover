import os
from file_mover import FileMoverHandler

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
