import logging

from PIL import Image

from carpeta import Tracer, ImageHandler, Traceable


def logger_process_image(image: Image.Image):
    logger = logging.getLogger('logger_process_image')
    logger.info("", extra={'trace': image})
    bw_image = image.convert("L")
    logger.info("", extra={'trace': bw_image})
    return bw_image


# TUNE: This probably could be implemented as parametrization of test_trace.py::test_trace
def test_logging(random_image_file):
    tracer = Tracer()
    handler = ImageHandler(tracer, logging.INFO)
    logger = logging.getLogger('logger_process_image')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    image = Traceable(Image.open(random_image_file()), 'id1')
    processed_image = logger_process_image(image)

    assert tracer['id1'][0].object == image.value
    assert tracer['id1'][0].function_name == 'logger_process_image'
    assert tracer['id1'][0].line_number == 10
    assert tracer['id1'][1].object == processed_image.value
    assert tracer['id1'][1].function_name == 'logger_process_image'
    assert tracer['id1'][1].line_number == 12
    assert tracer['id1'][0].timestamp < tracer['id1'][1].timestamp
