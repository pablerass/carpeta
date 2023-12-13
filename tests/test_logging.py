import logging

from PIL import Image

from carpeta import Tracer, ImageHandler, Traceable, TraceId


def logger_process_image(image: Image.Image):
    logger = logging.getLogger('logger_process_image')
    logger.info("", extra={'trace': image})
    bw_image = image.convert("L")
    logger.info("", extra={'trace': bw_image})
    return bw_image


def test_logging_implicit_id(random_image_file):
    tracer = Tracer()
    handler = ImageHandler(tracer, logging.INFO)
    logger = logging.getLogger('logger_process_image')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    image = Traceable(Image.open(random_image_file()), 'id1')
    processed_image = logger_process_image(image)

    assert tracer['id1'][0].value == image.value
    assert tracer['id1'][0].function_name == 'logger_process_image'
    assert tracer['id1'][0].line_number == 10
    assert tracer['id1'][1].value == processed_image.value
    assert tracer['id1'][1].function_name == 'logger_process_image'
    assert tracer['id1'][1].line_number == 12
    assert tracer['id1'][0].timestamp < tracer['id1'][1].timestamp


def test_logging_explicit_id(random_image_file):
    def logger_process_image(image: Image.Image, trace_id: TraceId):
        logger = logging.getLogger('logger_process_image')
        logger.info("", extra={'trace': image, 'trace_id': trace_id})
        bw_image = image.convert("L")
        logger.info("", extra={'trace': bw_image, 'trace_id': trace_id})
        return bw_image

    tracer = Tracer()
    handler = ImageHandler(tracer, logging.INFO)
    logger = logging.getLogger('logger_process_image')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    image = Traceable(Image.open(random_image_file()), 'id1')
    processed_image = logger_process_image(image, trace_id='ed2')

    assert tracer['ed2'][0].value == image.value
    assert tracer['ed2'][0].function_name == 'logger_process_image'
    assert tracer['ed2'][0].line_number == 38
    assert tracer['ed2'][1].value == processed_image.value
    assert tracer['ed2'][1].function_name == 'logger_process_image'
    assert tracer['ed2'][1].line_number == 40
    assert tracer['ed2'][0].timestamp < tracer['ed2'][1].timestamp
