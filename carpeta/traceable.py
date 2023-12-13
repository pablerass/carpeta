from __future__ import annotations

from typing import Callable, TypeVar, Generic, NewType, Any
from uuid import uuid4


TraceId = NewType('TraceId', str)


def random_trace_id() -> TraceId:
    return str(uuid4())


T = TypeVar('T')


# Probably this is too dirty and should just not be implemented
class Traceable(Generic[T]):
    def __init__(self, value: T, trace_id: TraceId = None):
        self.__value = value
        if trace_id is None:
            trace_id = random_trace_id
        self.__trace_id = trace_id

    @property
    def value(self) -> T:
        return self.__value

    @property
    def trace_id(self) -> TraceId:
        return self.__trace_id

    def __str__(self):
        return f"{self.__value}[{self.__trace_id}]"

    def bind(self, function: Callable[[T], T], *args) -> Traceable[T]:
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


# TUNE: Make this testable
_ID_EXTRACTORS = {
    Traceable: lambda x: x.trace_id
}


def register_id_extractor(_type: type[T], extractor: Callable[T, TraceId]):
    _ID_EXTRACTORS.update({
        _type: extractor
    })


def extract_id(value: Any) -> TraceId:
    if type(value) in _ID_EXTRACTORS:
        return _ID_EXTRACTORS[type(value)](value)

    for _type, function in _ID_EXTRACTORS.items():
        if isinstance(value, _type):
            return function(value)

    return random_trace_id()
