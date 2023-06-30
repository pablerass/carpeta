import pytest

import os
import random
import tempfile

from pathlib import Path
from PIL import Image


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
def random_image():
    temp_dir = tempfile.mkdtemp()
    temp_file = Path(temp_dir) / f"{next(tempfile._get_candidate_names())}.png"

    aspect_ratio = random.choice([(3, 2), (4, 3)])
    width = random.randint(300, 1000)
    height = int(width * aspect_ratio[1] / aspect_ratio[0])

    image = Image.new('RGB', (width, height), color=(255, 0, 0))
    image.save(temp_file)

    yield temp_file

    temp_file.unlink()


@pytest.fixture
def random_card_image(random_image):
    return CardImage(random_image, size=STANDARD)