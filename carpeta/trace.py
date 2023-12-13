from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, TypeVar


T = TypeVar('T')


class Record:
    def __init__(self, value: T, /, timestamp: datetime = None, previous: Record = None,
                 message: str = None, function_name: str = None, source_file: str | Path = None,
                 line_number: int = None, thread_id: int = None):
        self.__value = value

        if timestamp is None:
            timestamp = datetime.now()
        self.__timestamp = timestamp

        self.__function_name = function_name
        self.__source_file = source_file
        self.__line_number = line_number
        self.__thread_id = thread_id
        self.__previous = previous
        self.__message = message

        self.__value_uri = None
        self.__code_lines = None

    @property
    def value(self) -> T:
        return self.__value

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
