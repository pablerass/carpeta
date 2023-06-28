import pytest

import os

from pathlib import Path


from carpeta.card import CardImage
from carpeta.measure import STANDARD


TEST_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_FILES_PATH = os.path.join(TEST_PATH, "files")


@pytest.fixture
def fixture_file():
    # TUNE: Move to path
    def path(rel_path: Path | str):
        return os.path.join(TEST_FILES_PATH, rel_path)

    return path


@pytest.fixture
def card_image(fixture_file):
    return CardImage(fixture_file('card.png'), size=STANDARD)