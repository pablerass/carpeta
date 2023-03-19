import pytest

import os
from pathlib import Path


TEST_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_FILES_PATH = os.path.join(TEST_PATH, "files")


@pytest.fixture
def fixture_file():
    def path(rel_path: Path | str):
        return os.path.join(TEST_FILES_PATH, rel_path)

    return path