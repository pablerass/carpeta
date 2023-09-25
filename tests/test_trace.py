from PIL import Image, ImageOps

from carpeta import Tracer, Traceable


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

    image = Traceable(Image.open(random_image_file()), 'id1')
    processed_image = tracer_process_image(image, tracer)

    assert tracer['id1'][0].object == image.value
    assert tracer['id1'][0].function_name == 'tracer_process_image'
    assert tracer['id1'][0].line_number == 7
    assert tracer['id1'][1].object == processed_image.value
    assert tracer['id1'][1].function_name == 'tracer_process_image'
    assert tracer['id1'][1].line_number == 9
    assert tracer['id1'][0].timestamp < tracer['id1'][1].timestamp

    assert len(tracer) == 1
    image = Traceable(Image.open(random_image_file()), 'id2')
    processed_image = tracer_process_image(image, tracer)
    tracer_reprocess_image(processed_image, tracer)
    assert len(tracer) == 2
    assert len(tracer['id1']) == 2
    assert len(tracer['id2']) == 4
    assert tracer['id1'][0].previous is None
    assert tracer['id1'][1].previous == tracer['id1'][0]
    assert tracer['id2'][0].previous is None
    assert tracer['id2'][1].previous == tracer['id2'][0]
    assert tracer['id2'][2].previous == tracer['id2'][1]
    assert tracer['id2'][3].previous == tracer['id2'][2]
