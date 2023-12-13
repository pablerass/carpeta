from PIL import Image

import pickle

from carpeta import Traceable, register_id_extractor, extract_id


def test_traceable_function():
    value = "value"
    traceable_value = Traceable(value, 'id1')

    traceable_result = traceable_value.bind(sorted)
    assert traceable_result.trace_id == 'id1'
    assert traceable_result.value == sorted(value)
    assert len(traceable_result) == len(value)

    function = lambda x, y: x + y       # noqa: E731
    traceable_result = traceable_value.bind(function, 's')
    assert traceable_result.trace_id == 'id1'
    assert traceable_result.value == function(value, 's')


def test_traceable_method():
    value = "value"
    traceable_value = Traceable(value, 'id1')

    traceable_result = traceable_value.capitalize()
    assert traceable_result.trace_id == 'id1'
    assert traceable_result.value == value.capitalize()

    traceable_result = traceable_value.strip('v')
    assert traceable_result.trace_id == 'id1'
    assert traceable_result.value == value.strip('v')


def test_traceable_pickle():
    value = "value"
    traceable_value = Traceable(value, 'id1')

    pickled_traceable_value = pickle.loads(pickle.dumps(traceable_value))

    assert pickled_traceable_value.value == value
    assert pickled_traceable_value.trace_id == 'id1'


def test_traceable_image(random_image_file):
    value = Image.open(random_image_file())

    traceable_value = Traceable(value, value.filename)

    pickled_traceable_value = pickle.loads(pickle.dumps(traceable_value))

    assert pickled_traceable_value.value == value
    assert pickled_traceable_value.trace_id == value.filename


def test_extract_id_traceable(random_image_file):
    value = Image.open(random_image_file())

    traceable_value = Traceable(value, value.filename)

    assert extract_id(traceable_value) == value.filename


def test_extract_id_custom(random_image_file):
    register_id_extractor(Image.Image, lambda x: x.filename)

    value = Image.open(random_image_file())

    assert extract_id(value) == value.filename
