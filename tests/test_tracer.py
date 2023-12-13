import pytest

from functools import partial
from multiprocessing import Pool
from PIL import Image, ImageOps

from carpeta import Tracer, Traceable, TraceId, ProcessTracer


def tracer_process_image(image: Traceable[Image.Image], tracer: Tracer):
    tracer.record(image)
    bw_image = image.convert("L")
    tracer.record(bw_image)
    return bw_image


def tracer_reprocess_image(image: Traceable[Image.Image], tracer: Tracer):
    tracer.record(image)
    inverted_image = ImageOps.invert(image)
    tracer.record(inverted_image)
    return inverted_image


def test_tracer_implicit_id(random_image_file):

    tracer = Tracer()

    image = Traceable(Image.open(random_image_file()), 'id1')
    processed_image = tracer_process_image(image, tracer)

    assert tracer['id1'][0].value == image.value
    assert tracer['id1'][0].function_name == 'tracer_process_image'
    assert tracer['id1'][0].line_number == 11
    assert tracer['id1'][1].value == processed_image.value
    assert tracer['id1'][1].function_name == 'tracer_process_image'
    assert tracer['id1'][1].line_number == 13
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


def test_tracer_explicit_id(random_image_file):
    def tracer_process_image(image: Traceable[Image.Image], tracer: Tracer, trace_id: TraceId):
        tracer.record(image, trace_id=trace_id)
        bw_image = image.convert("L")
        tracer.record(bw_image, trace_id=trace_id)
        return bw_image

    def tracer_reprocess_image(image: Traceable[Image.Image], tracer: Tracer, trace_id: TraceId):
        tracer.record(image, trace_id=trace_id)
        inverted_image = ImageOps.invert(image)
        tracer.record(inverted_image, trace_id=trace_id)
        return inverted_image

    tracer = Tracer()

    image = Traceable(Image.open(random_image_file()), 'id1')
    processed_image = tracer_process_image(image, tracer, trace_id='ed2')

    assert tracer['ed2'][0].value == image.value
    assert tracer['ed2'][0].function_name == 'tracer_process_image'
    assert tracer['ed2'][0].line_number == 56
    assert tracer['ed2'][1].value == processed_image.value
    assert tracer['ed2'][1].function_name == 'tracer_process_image'
    assert tracer['ed2'][1].line_number == 58
    assert tracer['ed2'][0].timestamp < tracer['ed2'][1].timestamp

    assert len(tracer) == 1
    image = Traceable(Image.open(random_image_file()), 'id2')
    processed_image = tracer_process_image(image, tracer, trace_id='ed3')
    tracer_reprocess_image(processed_image, tracer, trace_id='ed3')
    assert len(tracer) == 2
    assert len(tracer['ed2']) == 2
    assert len(tracer['ed3']) == 4
    assert tracer['ed2'][0].previous is None
    assert tracer['ed2'][1].previous == tracer['ed2'][0]
    assert tracer['ed3'][0].previous is None
    assert tracer['ed3'][1].previous == tracer['ed3'][0]
    assert tracer['ed3'][2].previous == tracer['ed3'][1]
    assert tracer['ed3'][3].previous == tracer['ed3'][2]


# There are race conditions that can make this test work if queue read thread is sutdonw properly by chance
@pytest.mark.repeat(5)
def test_trace_multiprocessing(random_image_file):
    tracer = ProcessTracer()
    process_image = partial(tracer_process_image, tracer=tracer.remote_tracer)

    images = [Traceable(Image.open(random_image_file()), f"id{i}") for i in range(4)]
    with Pool(processes=4) as pool:
        pool.map(process_image, images)

    tracer.wait_and_stop()

    assert len(tracer) == 4
    for i in range(len(tracer)):
        assert tracer[f'id{i}'][0].function_name == 'tracer_process_image'
        assert tracer[f'id{i}'][0].line_number == 11
        assert tracer[f'id{i}'][1].function_name == 'tracer_process_image'
        assert tracer[f'id{i}'][1].line_number == 13
        assert tracer[f'id{i}'][0].timestamp < tracer[f'id{i}'][1].timestamp
