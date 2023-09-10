from datetime import datetime
from logging import Handler, LogRecord, NOTSET

from .trace import Tracer


class ImageHandler(Handler):
    def __init__(self, tracer: Tracer, level=NOTSET):
        self.__tracer = tracer
        super().__init__(level)

    def emit(self, record: LogRecord) -> None:
        timestamp = datetime.fromtimestamp(record.created)

        if hasattr(record, 'trace'):
            self.__tracer.record(
                record.trace,
                timestamp=timestamp,
                message=record.msg,
                function_name=record.funcName,
                source_file=record.pathname,
                line_number=record.lineno,
            )
