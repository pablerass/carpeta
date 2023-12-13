from datetime import datetime
from logging import Handler, LogRecord, NOTSET

from .tracer import Tracer


class ImageHandler(Handler):
    def __init__(self, tracer: Tracer, level=NOTSET):
        self.__tracer = tracer
        super().__init__(level)

    def emit(self, record: LogRecord) -> None:
        timestamp = datetime.fromtimestamp(record.created)

        trace_id = None
        if hasattr(record, 'trace_id'):
            trace_id = record.trace_id

        if hasattr(record, 'trace'):
            self.__tracer.record(
                record.trace,
                trace_id=trace_id,
                timestamp=timestamp,
                message=record.msg,
                function_name=record.funcName,
                source_file=record.pathname,
                line_number=record.lineno,
            )
