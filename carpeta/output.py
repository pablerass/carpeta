import base64
import cv2 as cv
import io
import nbformat as nbf
import numpy as np

from pathlib import Path
from PIL import Image
from typing import TypeVar, Callable, Any

from .trace import Trace


T = TypeVar('T')


def _image_html_tag_creator(image: Image.Image) -> str:
    image_buffer = io.BytesIO()
    image.save(image_buffer, format="PNG")
    image_uri = f"data:image/png;base64,{base64.b64encode(image_buffer.getvalue()).decode('UTF-8')}"
    return f'<img src="{image_uri}" />'


def _ndarray_image_html_tag_creator(image: np.ndarray) -> str:
    return _image_html_tag_creator(Image.fromarray(cv.cvtColor(image, cv.COLOR_BGR2RGB)))


def _default_html_tag_creator(value: Any) -> str:
    return repr(value)


# TUNE: Make this testable
_HTML_TAG_CREATORS = {
    Image.Image: _image_html_tag_creator,
    np.ndarray: _ndarray_image_html_tag_creator
}


def _create_html_tag(value: Any) -> str:
    if type(value) in _HTML_TAG_CREATORS:
        return _HTML_TAG_CREATORS[type(value)](value)

    for _type, function in _HTML_TAG_CREATORS.items():
        if isinstance(value, _type):
            return function(value)

    return _default_html_tag_creator(value)


def register_html_tag_creator(_type: type[T], html_tag_creator: Callable[T, str]):
    _HTML_TAG_CREATORS.update({
        _type: html_tag_creator
    })


def trace_html_output(traces: list[Trace], output_file: Path):
    PRISM_VERSION = "1.29.0"
    PRISM_URL = f"https://cdnjs.cloudflare.com/ajax/libs/prism/{PRISM_VERSION}"

    BOOTSTRAP_VERSION = "5.2.3"
    BOOTSTRAP_URL = f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist"

    # TODO: Generate html vía template
    # TODO: Properly format margins
    with output_file.open('w') as output_file:
        output_file.write(f"""<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="{BOOTSTRAP_URL}/css/bootstrap.min.css" />
        <link rel="stylesheet" href="{PRISM_URL}/themes/prism.min.css" />
        <script src="{BOOTSTRAP_URL}/js/bootstrap.min.js"></script>
        <script src="{BOOTSTRAP_URL}/js/bootstrap.bundle.min.js"></script>
        <script src="{PRISM_URL}/prism.min.js"></script>
        <script src="{PRISM_URL}/components/prism-python.min.js"></script>
    </head>
    <body>""")
        output_file.write(f"""
    <ul class="nav nav-tabs mb-{len(traces)}" id="trace" role="tablist">""")
        for n, trace in enumerate(traces):
            output_file.write(f"""
        <li class="nav-item" role="presentation">
            <a class="nav-link{ " active" if not n else ""}"
               id="trace-tab-{n+1}"
               data-bs-toggle="tab"
               data-bs-target="#trace-tabs-{n+1}"
               role="tab"
               aria-controls="trace-tabs-{n+1}"
               aria-selected="{"true" if not n else "false"}">{trace.name}
            </a>
        </li>""")
        output_file.write("""
    </ul>
    <div class="tab-content" id="trace-content">""")
        for n, trace in enumerate(traces):
            output_file.write(f"""
        <div class="tab-pane fade{ " show active" if not n else ""}"
             id="trace-tabs-{n+1}"
             role="tabpanel"
             aria-labelledby="trace-tab-{n+1}">""")
            for record in trace:
                # TODO: Add line numbers in code, this approach does not work
                if record.message:
                    output_file.write(f"""
            <h5>{record.message}</h5>""")
                output_file.write(f"""
            <pre><code class="language-python line-numbers">{record.code}</code></pre>
            { _create_html_tag(record.value) }
            <br/>""")
            output_file.write("""
        </div>""")
        output_file.write("""
    </div>""")
        output_file.write("""
    </body>
</html>""")


# TODO: Implement this in the right way
# def trace_yaml_output(traces: list[Trace], output_file: Path):
#     with output_file.open('w') as o:
#         yaml.dump(list(traces), o)


def trace_notebook_output(traces: list[Trace], output_dir: Path):
    # TODO: Include required imports
    # TODO: Load image in the first cell
    # TODO: Comment logging lines
    # TODO: Propagate image value between cells
    # TODO: Reindent code
    output_dir.mkdir(parents=True, exist_ok=True)

    for trace in traces:
        output_file = output_dir / f"{trace.name}.ipynb"

        nb = nbf.v4.new_notebook()
        for record in trace:
            code_cell = nbf.v4.new_code_cell()
            code_cell.source = record.code
            nb['cells'].append(code_cell)

        nbf.write(nb, output_file)


def trace_output(traces: list[Trace], output_path: Path | str):
    if isinstance(output_path, str):
        output_path = Path(output_path)

    output_path = output_path.expanduser()

    if not output_path.is_absolute():
        output_path = Path.cwd() / output_path

    match output_path:
        case Path(suffix='.html'):
            trace_html_output(traces, output_path)
        # case Path(suffix='.yml') | Path(suffix='.yaml'):
        #     trace_yaml_output(traces, output_path)
        case Path(suffix=''):
            trace_notebook_output(traces, output_path)
        case _:
            raise ValueError('Unable to identify output format in output_path')
