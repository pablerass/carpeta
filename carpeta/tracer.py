from __future__ import annotations

import inspect
import threading

from datetime import datetime
from multiprocessing import Manager, Queue
from typing import Iterable
from queue import Empty

from .traceable import Traceable
from .trace import Trace, Record


class Tracer:
    def __init__(self):
        self._traces = {}

    def record(self, traceable: Traceable, /, timestamp: datetime = None, message: str = None,
               function_name: str = None, source_file: str = None,
               line_number: int = None) -> tuple[str, Record]:
        # TUNE: I tried to use frame info but logging does not return it,
        # maybe there is a better way
        if function_name is None or source_file is None or line_number is None:
            calling_frame = inspect.currentframe().f_back
            calling_frame_info = inspect.getframeinfo(calling_frame)
            function_name = calling_frame_info.function
            source_file = calling_frame_info.filename
            line_number = calling_frame_info.lineno

        thread_id = threading.get_native_id()

        if traceable.trace_id in self._traces:
            previous_trace = self._traces[traceable.trace_id][-1]
        else:
            self._traces[traceable.trace_id] = Trace(traceable.trace_id)
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
        self._traces[traceable.trace_id].add(record)

        return (traceable.trace_id, Record)

    def __len__(self):
        return len(self._traces)

    def __getitem__(self, trace_id) -> Trace:
        return self._traces[trace_id]

    def __iter__(self) -> Iterable[Trace]:
        return (trace for trace in self._traces.values())


class _RemoteTracer(Tracer):
    def __init__(self, queue: Queue):
        super().__init__()

        self.__queue = queue

    def record(self, *args, **kwargs) -> tuple[str, Record]:
        value = super().record(*args, **kwargs)
        self.__queue.put(value)


class ProcessTracer(Tracer):
    def __init__(self):
        super().__init__()

        self.__queue = None
        self.__remote_tracer = None
        self.__is_closed = False
        self.__receive_thread = None

    def __receive(self) -> None:
        while True:
            try:
                if self.__is_closed and self.__queue.empty():
                    break

                trace_id, record = self.__queue.get()
                if trace_id not in self._traces:
                    self._traces[trace_id] = Trace(trace_id)
                self._traces[trace_id].add(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except (EOFError, OSError):
                break  # The queue was closed by child?
            except Empty:
                pass

    @property
    def remote_tracer(self) -> ProcessTracer:
        if self.__remote_tracer is None:
            self.__queue = Manager().Queue(-1)
            self.__is_closed = False
            self.__receive_thread = threading.Thread(target=self.__receive)
            self.__receive_thread.daemon = True
            self.__receive_thread.start()

            self.__remote_tracer = _RemoteTracer(self.__queue)

        return self.__remote_tracer
