import pytest

import os

from pathlib import Path


from carpeta.card import CardImage
from carpeta.measure import STANDARD


TEST_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_FILES_PATH = os.path.join(TEST_PATH, "files")


@pytest.fixture
def fixture_file():
    # TUNE: Move to pathlib
    def path(rel_path: Path | str):
        return os.path.join(TEST_FILES_PATH, rel_path)

    return path


@pytest.fixture
def random_image(fixture_file):
    return fixture_file('card.png')


@pytest.fixture
def card_image(random_image):
    return CardImage(random_image, size=STANDARD)