from __future__ import annotations

from typing import Callable, TypeVar, Generic


T = TypeVar('T')


# Probably this is too dirty and should just not be implemented
class Traceable(Generic[T]):
    def __init__(self, value: T, trace_id: str):
        self.__value = value
        self.__trace_id = trace_id

    @property
    def value(self) -> T:
        return self.__value

    @property
    def trace_id(self) -> str:
        return self.__trace_id

    def __str__(self):
        return f"{self.__value}[{self.__trace_id}]"

    def bind(self, function: Callable[[T], T], *args) -> Traceable:
        return Traceable(function(self.value, *args), self.trace_id)

    def __getattr__(self, name: str):
        if name == "trace_id":
            return self.trace_id

        attr = getattr(self.value, name)
        if callable(attr):
            def f(*args):
                return Traceable(attr(*args), self.trace_id)

            return f
        else:
            return getattr(self.value, name)

    def __len__(self) -> int:
        return len(self.value)

    def __getstate__(self) -> dict:
        return self.__dict__

    def __setstate__(self, d: dict):
        self.__dict__ = d
