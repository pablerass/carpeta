from functools import partial
from multiprocessing import Pool
from PIL import Image, ImageOps

from carpeta import Tracer


def tracer_process_image(image: Image.Image, tracer: Tracer):
    tracer.record(image)
    bw_image = image.convert("L")
    tracer.record(bw_image)
    return bw_image


def tracer_reprocess_image(image: Image.Image, tracer: Tracer):
    tracer.record(image)
    inverted_image = ImageOps.invert(image)
    tracer.record(inverted_image)
    return inverted_image


def test_tracer(random_image_file):
    tracer = Tracer()

    image = Image.open(random_image_file())
    processed_image = tracer_process_image(image, tracer)

    assert tracer[0][0].image == image
    assert tracer[0][0].function_name == 'tracer_process_image'
    assert tracer[0][0].line_number == 7
    assert tracer[0][1].image == processed_image
    assert tracer[0][1].function_name == 'tracer_process_image'
    assert tracer[0][1].line_number == 9
    assert tracer[0][0].timestamp < tracer[0][1].timestamp

    assert len(tracer) == 1
    image = Image.open(random_image_file())
    processed_image = tracer_process_image(image, tracer)
    tracer_reprocess_image(processed_image, tracer)
    assert len(tracer) == 2
    assert len(tracer[0]) == 2
    assert len(tracer[1]) == 4
    assert tracer[0][0].previous is None
    assert tracer[0][1].previous == tracer[0][0]
    assert tracer[1][0].previous is None
    assert tracer[1][1].previous == tracer[1][0]
    assert tracer[1][2].previous == tracer[1][1]
    assert tracer[1][3].previous == tracer[1][2]


def test_trace_image_file(random_image_file):
    tracer = Tracer()

    image_file_1 = random_image_file()
    image_1 = Image.open(image_file_1)
    tracer_process_image(image_1, tracer)

    image_file_2 = random_image_file()
    image_2 = Image.open(image_file_2)
    tracer_process_image(image_2, tracer)

    assert tracer[0][0].image_file == image_file_1
    assert tracer[0][1].image_file == image_file_1
    assert tracer[1][0].image_file == image_file_2
    assert tracer[1][1].image_file == image_file_2


def test_trace_multiprocessing(random_image_file):
    tracer = Tracer()
    process_image = partial(tracer_process_image, tracer=tracer)

    images = [Image.open(random_image_file()) for _ in range(1)]
    with Pool(processes=4) as pool:
        pool.map(process_image, images)

    assert len(tracer) == 4
