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

        # Register only the first found image
        if isinstance(record.msg, Image.Image) or isinstance(record.msg, np.ndarray):
            images.append(record.msg)
        for arg in record.args:
            if isinstance(arg, Image.Image) or isinstance(arg, np.ndarray):
                images.append(arg)

        for image in images:
            self.__tracer.record(
                image,
                timestamp=timestamp,
                function_name=record.funcName,
                source_file=record.pathname,
                line_number=record.lineno,
            )
