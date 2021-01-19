from abc import ABC, abstractmethod
from typing import Any

SUPPORTED_EXTENSIONS = {}


def register_extensions(*file_types):
    def decorate_parser(parser: Parser):
        parser._extensions = set(file_types)
        return parser

    return decorate_parser


class Parser(ABC):
    _extensions = set()

    @classmethod
    def load(cls, path, content: bytes):
        filepath, ext = path.split('.')
        return SUPPORTED_EXTENSIONS[ext].load_content(content)

    @classmethod
    @abstractmethod
    def load_content(cls, content: bytes):
        pass

    @classmethod
    def dump(cls, path, data: Any):
        filepath, ext = path.split('.')
        return SUPPORTED_EXTENSIONS[ext].dump_content(data)

    @classmethod
    @abstractmethod
    def dump_content(cls, data: Any):
        pass
