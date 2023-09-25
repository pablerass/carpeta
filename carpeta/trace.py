from __future__ import annotations

import base64
import cv2 as cv
import io
import inspect
import numpy as np
import threading

from datetime import datetime
from pathlib import Path
from PIL import Image
from typing import Iterable, TypeVar

from .traceable import Traceable


T = TypeVar('T')


class Record:
    def __init__(self, obj: T, /, timestamp: datetime = None, previous: Record = None,
                 message: str = None, function_name: str = None, source_file: str | Path = None,
                 line_number: int = None, thread_id: int = None):
        # TODO: Allow register more conversions
        if isinstance(obj, np.ndarray):
            obj = Image.fromarray(cv.cvtColor(obj, cv.COLOR_BGR2RGB))
        self.__object = obj

        if timestamp is None:
            timestamp = datetime.now()
        self.__timestamp = timestamp

        self.__function_name = function_name
        self.__source_file = source_file
        self.__line_number = line_number
        self.__thread_id = thread_id
        self.__previous = previous
        self.__message = message

        self.__object_uri = None
        self.__code_lines = None

    @property
    def object(self) -> T:
        return self.__object

    @property
    def object_uri(self) -> str:
        if self.__object_uri is None:
            # TODO: Allow register more exporters
            if isinstance(self.__obj, Image):
                object_buffer = io.BytesIO()
                self.object.save(object_buffer, format="PNG")
                self.__object_uri = \
                    f"data:image/png;base64,{base64.b64encode(object_buffer.getvalue()).decode('UTF-8')}"

        return self.__object_uri

    @property
    def previous(self) -> Record | None:
        return self.__previous

    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    @property
    def message(self) -> str | None:
        return self.__message

    @property
    def function_name(self) -> str | None:
        return self.__function_name

    @property
    def source_file(self) -> str | None:
        return self.__source_file

    @property
    def line_number(self) -> int | None:
        return self.__line_number

    @property
    def thread_id(self) -> int | None:
        return self.__thread_id

    @property
    def code_lines(self) -> tuple[str]:
        if self.__code_lines is None:
            # TUNE: The code can change during execution, maybe this should not be lazy
            with Path(self.source_file).open('r') as file:
                file_code = file.readlines()

            last_line = self.line_number
            if self.previous is None or self.function_name != self.previous.function_name:
                first_line = last_line - 1
            else:
                first_line = self.previous.line_number
            trace_code_lines = file_code[first_line:last_line]

            # TODO: Remove all initial empty lines, not only the first
            if not trace_code_lines[0].strip():
                del trace_code_lines[0]

            self.__code_lines = tuple(t.rstrip() for t in trace_code_lines)

        return self.__code_lines

    @property
    def code(self) -> str:
        return '\n'.join(self.code_lines)

    def __getstate__(self) -> dict:
        record_dict = {
            'object': self.object_uri,
            # TODO: Review iso format and timezone management
            'timestamp': self.timestamp.isoformat(),
            'code_lines': self.code_lines
        }

        if self.message is not None:
            record_dict |= {'image_file': self.message}
        if self.image_file is not None:
            record_dict |= {'image_file': str(self.image_file)}
        if self.function_name is not None:
            record_dict |= {'function_name': self.function_name}
        if self.source_file is not None:
            record_dict |= {'source_file': self.source_file}
        if self.line_number is not None:
            record_dict |= {'line_number': self.line_number}
        if self.thread_id is not None:
            record_dict |= {'thread_id': self.thread_id}

        return record_dict


class Trace:
    def __init__(self, name: str):
        self.__name = name
        self.__records = []

    @property
    def name(self) -> str:
        return self.__name

    @property
    def thread_id(self) -> int:
        # TUNE: Not sure if this property should live here
        return self.__records[0].thread_id

    def add(self, record: Record):
        self.__records.append(record)

    def __len__(self):
        return len(self.__records)

    def __getitem__(self, key) -> Record:
        return self.__records[key]

    def __iter__(self) -> Iterable[Record]:
        return (record for record in self.__records)

    def items(self) -> tuple(Record):
        return tuple(self)

    def __getstate__(self) -> dict:
        return {
            'name': self.name,
            'records': self.__records,
        }


class Tracer:
    def __init__(self,):
        self.__traces = {}

    def record(self, traceable: Traceable, /, timestamp: datetime = None, message: str = None,
               function_name: str = None, source_file: str = None,
               line_number: int = None) -> None:
        # TUNE: I tried to use frame info but logging does not return it,
        # maybe there is a better way
        if function_name is None or source_file is None or line_number is None:
            calling_frame = inspect.currentframe().f_back
            calling_frame_info = inspect.getframeinfo(calling_frame)
            function_name = calling_frame_info.function
            source_file = calling_frame_info.filename
            line_number = calling_frame_info.lineno

        thread_id = threading.get_native_id()

        if traceable.trace_id in self.__traces:
            previous_trace = self.__traces[traceable.trace_id][-1]
        else:
            self.__traces[traceable.trace_id] = Trace(traceable.trace_id)
            previous_trace = None

        record = Record(
            traceable.value,
            timestamp=timestamp,
            previous=previous_trace,
            message=message,
            function_name=function_name,
            source_file=source_file,
            line_number=line_number,
            thread_id=thread_id
        )
        self.__traces[traceable.trace_id].add(record)

    def __len__(self):
        return len(self.__traces)

    def __getitem__(self, trace_id) -> Trace:
        return self.__traces[trace_id]

    def __iter__(self) -> Iterable[Trace]:
        return (trace for trace in self.__traces.values())
