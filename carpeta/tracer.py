from __future__ import annotations

import inspect
import queue
import threading

from datetime import datetime
from multiprocessing import Manager, Queue
from typing import Iterable, Any

from .traceable import TraceId, Traceable, extract_id
from .trace import Trace, Record


class Tracer:
    def __init__(self):
        self._traces = {}

    def record(self, item: Any, /, trace_id: TraceId = None,
               timestamp: datetime = None, message: str = None,
               function_name: str = None, source_file: str = None,
               line_number: int = None) -> tuple[TraceId, Record]:
        # TUNE: I tried to use frame info but logging does not return it,
        # maybe there is a better way
        if function_name is None or source_file is None or line_number is None:
            calling_frame = inspect.currentframe().f_back
            calling_frame_info = inspect.getframeinfo(calling_frame)
            function_name = calling_frame_info.function
            source_file = calling_frame_info.filename
            line_number = calling_frame_info.lineno

        thread_id = threading.get_native_id()

        value = item
        if isinstance(item, Traceable):
            value = item.value
        if trace_id is None:
            trace_id = extract_id(item)

        if trace_id in self._traces:
            previous_trace = self._traces[trace_id][-1]
        else:
            self._traces[trace_id] = Trace(trace_id)
            previous_trace = None

        record = Record(
            value,
            timestamp=timestamp,
            previous=previous_trace,
            message=message,
            function_name=function_name,
            source_file=source_file,
            line_number=line_number,
            thread_id=thread_id
        )
        self._traces[trace_id].add(record)

        return (trace_id, record)

    def __len__(self):
        return len(self._traces)

    def __getitem__(self, trace_id) -> Trace:
        return self._traces[trace_id]

    def __iter__(self) -> Iterable[Trace]:
        return (trace for trace in self._traces.values())


class ProcessTracer(Tracer):
    class _RemoteTracer(Tracer):
        def __init__(self, queue: Queue):
            super().__init__()

            self.__queue = queue

        # TUNE: Try to avoid this arguments repetition
        def record(self, item: Any, /, trace_id: TraceId = None,
                   timestamp: datetime = None, message: str = None,
                   function_name: str = None, source_file: str = None,
                   line_number: int = None) -> tuple[TraceId, Record]:
            # TUNE: If this is not specified the original function call is not kept
            if function_name is None or source_file is None or line_number is None:
                calling_frame = inspect.currentframe().f_back
                calling_frame_info = inspect.getframeinfo(calling_frame)
                function_name = calling_frame_info.function
                source_file = calling_frame_info.filename
                line_number = calling_frame_info.lineno

            # TUNE: Value variable name is used too much in this code
            value = super().record(item, trace_id=trace_id,
                                   timestamp=timestamp, message=message,
                                   function_name=function_name, source_file=source_file,
                                   line_number=line_number)
            self.__queue.put(value)

    def __init__(self):
        super().__init__()

        self.__remote_tracer = None
        self.__receive_thread = None

    def __receive(self) -> None:
        while True:
            try:
                value = self.__queue.get()
                # TUNE: This is dirty but works
                if value == 'STOP':
                    break
                trace_id, record = value
                if trace_id not in self._traces:
                    self._traces[trace_id] = Trace(trace_id)
                self._traces[trace_id].add(record)
            except queue.Empty:
                pass
            except (EOFError, OSError):
                break  # The queue was closed by child?
            except Exception as e:
                raise e

    @property
    def remote_tracer(self) -> Tracer:
        if self.__remote_tracer is None:
            self.__queue = Manager().Queue(-1)
            self.__run = True
            self.__receive_thread = threading.Thread(target=self.__receive)
            self.__receive_thread.daemon = True
            self.__receive_thread.start()

            self.__remote_tracer = self._RemoteTracer(self.__queue)

        return self.__remote_tracer

    # TUNE: I would want to find another way to ensure all content is properly received before shutdown
    def wait_and_stop(self) -> None:
        if self.__receive_thread is not None:
            self.__queue.put('STOP')
            self.__receive_thread.join()
