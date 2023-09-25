from functools import partial
from multiprocessing import Pool
from PIL import Image

from carpeta import Tracer, Traceable


def tracer_process_image(image: Image.Image, tracer: Tracer):
    tracer.record(image)
    bw_image = image.convert("L")
    tracer.record(bw_image)
    return bw_image


def test_trace_multiprocessing(random_image_file):
    tracer = Tracer()
    process_image = partial(tracer_process_image, tracer=tracer)

    images = [Traceable(Image.open(random_image_file()), f"id{i}") for i in range(4)]
    with Pool(processes=4) as pool:
        pool.map(process_image, images)

    assert len(tracer) == 4
