import nbformat as nbf
import yaml

from pathlib import Path
from typing import Callable

from .trace import Trace


def trace_html_output(traces: list[Trace], output_file: Path):
    PRISM_VERSION = "1.29.0"
    PRISM_URL = f"https://cdnjs.cloudflare.com/ajax/libs/prism/{PRISM_VERSION}"

    BOOTSTRAP_VERSION = "5.2.3"
    BOOTSTRAP_URL = f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist"

    # TODO: Generate html vía template
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
                output_file.write(f"""
            <pre><code class="language-python line-numbers">{record.code}</code></pre>
            <img src="{record.data_uri_image}" />
            <br/>""")
            output_file.write("""
        </div>""")
        output_file.write("""
    </div>""")
        output_file.write("""
    </body>
</html>""")


def trace_yaml_output(traces: list[Trace], output_file: Path):
    with output_file.open('w') as o:
        yaml.dump(list(traces), o)


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
        case Path(suffix='.yml') | Path(suffix='.yaml'):
            trace_yaml_output(traces, output_path)
        case Path(suffix=''):
            trace_notebook_output(traces, output_path)
        case _:
            raise ValueError('Unable to identify output format in output_path')
