import numpy as np

from datetime import datetime
from logging import Handler, LogRecord, NOTSET
from PIL import Image

from .trace import Tracer


class ImageHandler(Handler):
    def __init__(self, tracer: Tracer, level=NOTSET):
        self.__tracer = tracer
        super().__init__(level)

    def emit(self, record: LogRecord) -> None:
        images = []
        timestamp = datetime.fromtimestamp(record.created)

        if hasattr(record, 'trace'):
            self.__tracer.record(
                record.trace,
                timestamp=timestamp,
                function_name=record.funcName,
                source_file=record.pathname,
                line_number=record.lineno,
            )
