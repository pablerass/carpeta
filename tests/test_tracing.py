import logging

from PIL import Image

from carpeta.tracing import Tracer, ImageHandler


def tracer_process_image(image: Image.Image, tracer: Tracer):
    tracer.record(image)
    bw_image = image.convert("L")
    tracer.record(bw_image)
    return bw_image


def logger_process_image(image: Image.Image):
    logger = logging.getLogger('logger_process_image')
    logger.info(image)
    bw_image = image.convert("L")
    logger.info('Image %s', bw_image)
    return bw_image


def test_tracer(random_image):
    tracer = Tracer()

    image = random_image()
    processed_image = tracer_process_image(image, tracer)

    assert tracer[0][0].image == image
    assert tracer[0][0].function_name == 'tracer_process_image'
    assert tracer[0][0].line_number == 9
    assert tracer[0][1].image == processed_image
    assert tracer[0][1].function_name == 'tracer_process_image'
    assert tracer[0][1].line_number == 11
    assert tracer[0][0].timestamp < tracer[0][1].timestamp

    assert len(tracer) == 1
    tracer_process_image(random_image(), tracer)
    assert len(tracer) == 2
    assert all(len(trace) == 2 for trace in tracer)
    assert tracer[0][0].previous is None
    assert tracer[1][0].previous is None
    assert tracer[0][1].previous == tracer[0][0]
    assert tracer[1][1].previous == tracer[1][0]


# TUNE: This probably could be implemented as parametrization of the previous test
def test_logging(random_image):
    tracer = Tracer()
    handler = ImageHandler(tracer, logging.INFO)
    logger = logging.getLogger('logger_process_image')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    image = random_image()
    processed_image = logger_process_image(image)

    assert tracer[0][0].image == image
    assert tracer[0][0].function_name == 'logger_process_image'
    assert tracer[0][0].line_number == 17
    assert tracer[0][1].image == processed_image
    assert tracer[0][1].function_name == 'logger_process_image'
    assert tracer[0][1].line_number == 19
    assert tracer[0][0].timestamp < tracer[0][1].timestamp

    assert len(tracer) == 1
    logger_process_image(random_image())
    assert len(tracer) == 2
    assert all(len(trace) == 2 for trace in tracer)
    assert tracer[0][0].previous is None
    assert tracer[1][0].previous is None
    assert tracer[0][1].previous == tracer[0][0]
    assert tracer[1][1].previous == tracer[1][0]


def test_trace_image_file(random_image_file):
    pass
