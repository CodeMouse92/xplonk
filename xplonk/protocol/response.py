from abc import ABCMeta, abstractmethod


class _Response(metaclass=ABCMeta):
    multi_line: bool

    @abstractmethod
    async def from_stream(self, stream: None) -> "_Response":
        ...


class GREETING(_Response):
    multi_line = False

    async def from_stream(self, stream: None) -> "GREETING":
        return self


class CAPABILITIES(_Response):
    multi_line = True
