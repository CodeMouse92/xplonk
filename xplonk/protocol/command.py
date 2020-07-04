from abc import ABCMeta

from typing import Type

from xplonk.protocol import response


class _Command(metaclass=ABCMeta):
    allow_pipelining: bool
    response_class: Type[response._Response]


class CAPABILITIES(_Command):
    allow_pipelining = True
    response_class = response.CAPABILITIES
