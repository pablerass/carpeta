from __future__ import annotations

import cv2 as cv
import inspect
import numpy as np
import threading

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from PIL import Image
from typing import Iterable


class Record:
    # TUNE: This could be applied to any type of object
    def __init__(self, image: Image.Image | np.ndarray, timestamp: datetime = None, previous: Record = None, /,
                 function_name: str = None, source_file: str | Path = None, line_number: int = None,
                 thread_id: int = None):
        if isinstance(image, np.ndarray):
            image = Image.fromarray(cv.cvtColor(image, cv.COLOR_BGR2RGB))
        self.__image = image.copy()

        if timestamp is None:
            timestamp = datetime.now()
        self.__timestamp = timestamp

        self.__function_name = function_name
        self.__source_file = source_file
        self.__line_number = line_number
        if thread_id is None:
            thread_id = threading.get_native_id()
        self.__thread_id = thread_id
        self.__previous = previous

        try:
            self.__image_file = Path(image.filename)
        except AttributeError:
            if previous is not None:
                self.__image_file = previous.image_file
            else:
                self.__image_file = None

        self.__code = None

    @property
    def image(self) -> Image.Image:
        return self.__image

    @property
    def image_file(self) -> Path | None:
        return self.__image_file

    @property
    def previous(self) -> Record:
        return self.__previous

    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

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
    def code(self) -> str:
        if self.__code is None:
            # TUNE: The code can change during execution
            with Path(self.source_file).open('r') as file:
                file_code = file.readlines()

            last_line = self.line_number
            if self.previous is None or self.function_name != self.previous.function_name:
                # TODO: Add calling function definition
                first_line = last_line - 1
            else:
                first_line = self.previous.line_number
            trace_code_lines = file_code[first_line:last_line]

            # Code formatting or adjustments
            if not trace_code_lines[0].strip():
                del trace_code_lines[0]
            # FIXME: This does not comment lines propery, it should keep align
            # trace_code_lines[-1] = f"# {trace_code_lines[-1]}"

            self.__code = ''.join(trace_code_lines)

        return self.__code


class Trace:
    def __init__(self):
        self.__traces = []

    @property
    def image_file(self) -> Path:
        return self.__traces[0].image_file

    @property
    def thread_id(self) -> int:
        # TUNE: Not sure if this property should live here
        return self.__traces[0].thread_id

    def add(self, trace: Record):
        self.__traces.append(trace)

    def __len__(self):
        return len(self.__traces)

    def __getitem__(self, key) -> Record:
        return self.__traces[key]

    def __iter__(self) -> Iterable[Record]:
        return (trace for trace in self.__traces)


class Tracer:
    def __init__(self):
        self.__last_trace = defaultdict(int)
        self.__traces = defaultdict(Trace)

    def record(self, image: Image.Image | np.ndarray, /, timestamp: datetime = None,
               function_name: str = None, source_file: str = None, line_number: int = None,
               thread_id: int = None) -> None:
        # TUNE: I tried to use frame info but logging does not return it,
        # maybe there is a better way
        if function_name is None or source_file is None or line_number is None:
            calling_frame = inspect.currentframe().f_back
            calling_frame_info = inspect.getframeinfo(calling_frame)
            function_name = calling_frame_info.function
            source_file = calling_frame_info.filename
            line_number = calling_frame_info.lineno

        thread_id = threading.get_native_id()

        # TODO: This aproach does not work with loops or with multiple executions of the same function
        # TUNE; There must be a more pythonic way of doing this
        stream_number = self.__last_trace[source_file, line_number, thread_id]
        self.__last_trace[source_file, line_number, thread_id] = \
            self.__last_trace[source_file, line_number, thread_id] + 1

        previous_trace = None
        if stream_number in self.__traces:
            previous_trace = self.__traces[stream_number][-1]

        trace = Record(
            image,
            timestamp,
            previous_trace,
            function_name=function_name,
            source_file=source_file,
            line_number=line_number,
            thread_id=thread_id
        )

        self.__traces[stream_number].add(trace)

    def __len__(self):
        return len(self.__traces)

    def __getitem__(self, key) -> Record:
        return self.__traces[key]

    def __iter__(self) -> Iterable[Record]:
        return (trace for trace in self.__traces.values())
