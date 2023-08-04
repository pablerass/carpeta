import logging

from PIL import Image

from carpeta.processing import Tracer, ImageHandler


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

    assert len(tracer.traces) == 2
    assert tracer.traces[0].image == image
    assert tracer.traces[0].function_name == 'tracer_process_image'
    assert tracer.traces[0].line_number == 9
    assert tracer.traces[1].image == processed_image
    assert tracer.traces[1].function_name == 'tracer_process_image'
    assert tracer.traces[1].line_number == 11
    assert tracer.traces[0].timestamp < tracer.traces[1].timestamp

    assert len(tracer.streams) == 1
    tracer_process_image(random_image(), tracer)
    assert len(tracer.streams) == 2
    assert all(len(traces) == 2 for traces in tracer.streams.values())


def test_logging(random_image):
    tracer = Tracer()
    handler = ImageHandler(tracer, logging.INFO)
    logger = logging.getLogger('logger_process_image')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    image = random_image()
    processed_image = logger_process_image(image)

    assert len(tracer.traces) == 2
    assert tracer.traces[0].image == image
    assert tracer.traces[0].function_name == 'logger_process_image'
    assert tracer.traces[0].line_number == 17
    assert tracer.traces[1].image == processed_image
    assert tracer.traces[1].function_name == 'logger_process_image'
    assert tracer.traces[1].line_number == 19
    assert tracer.traces[0].timestamp < tracer.traces[1].timestamp

    assert len(tracer.streams) == 1
    logger_process_image(random_image())
    assert len(tracer.streams) == 2
    assert all(len(traces) == 2 for traces in tracer.streams.values())
