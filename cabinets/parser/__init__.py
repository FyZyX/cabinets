import os
from abc import ABC, abstractmethod
from typing import Any

SUPPORTED_EXTENSIONS = {}


class ParserError(Exception):
    pass


def register_extensions(*file_types):
    def decorate_parser(parser):
        try:
            if not issubclass(parser, Parser):
                raise ParserError(f"Cannot register extensions: Type "
                                  f"'{parser.__name__}' is not a subclass of "
                                  f"'{Parser.__name__}'")
        except TypeError:
            raise ParserError(
                "Cannot register extensions: Decorated object must be a class")
        if parser._extensions:
            raise ParserError(
                f"Cannot register extensions: Extensions {tuple(parser._extensions)} "
                f"are already registered for {parser.__name__}")
        parser._extensions = set(file_types)
        return parser

    return decorate_parser


class Parser(ABC):
    _extensions = set()

    @classmethod
    def _split_path(cls, path: str) -> (str, str):
        path = os.path.abspath(path)
        dot_index = path.rfind('.')
        filepath = path[:dot_index]
        ext = path[dot_index + 1:]
        return filepath, ext

    @classmethod
    def load(cls, path, content: bytes, **kwargs):
        if not isinstance(content, bytes):
            raise ValueError("Content must have type `bytes`")
        _, ext = cls._split_path(path)
        return SUPPORTED_EXTENSIONS[ext].load_content(content, **kwargs)

    @classmethod
    @abstractmethod
    def load_content(cls, content: bytes, **kwargs):
        pass  # pragma: no cover

    @classmethod
    def dump(cls, path, data: Any, **kwargs):
        _, ext = cls._split_path(path)
        return SUPPORTED_EXTENSIONS[ext].dump_content(data, **kwargs)

    @classmethod
    @abstractmethod
    def dump_content(cls, data: Any, **kwargs):
        pass  # pragma: no cover
