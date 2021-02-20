import inspect
from abc import ABC, abstractmethod
from typing import Union, Type, Any

from cabinets.parser import Parser

SUPPORTED_PROTOCOLS = {}


class CabinetError(Exception):
    pass


def register_protocols(*protocols):
    def decorate_cabinet(cabinet):
        try:
            if not issubclass(cabinet, Cabinet):
                raise CabinetError(f"Cannot register protocols: Type "
                                   f"'{cabinet.__name__}' is not a subclass of "
                                   f"'{Cabinet.__name__}'")
        except TypeError:
            raise CabinetError(
                "Cannot register protocols: Decorated object must be a class")
        if cabinet._protocols:
            raise CabinetError(
                f"Cannot register protocols: Protocols {tuple(cabinet._protocols)} are "
                f"already registered for {cabinet.__name__}")
        cabinet._protocols = set(protocols)
        return cabinet

    return decorate_cabinet


class Cabinet(ABC):
    _protocols = set()

    @classmethod
    @abstractmethod
    def set_configuration(cls, **kwargs):
        pass  # pragma: no cover

    @classmethod
    def read(cls, path: str, parser: Union[bool, Type[Parser]] = True, **kwargs) -> Any:
        """
        Read file contents using a specific protocol.

        :param str path: Path to file within cabinet
        :param Union[bool, Type[Parser]] parser: `True` for parsing using default
            file extension Parser, `False` for no parsing, a `Parser` subclass for
            parsing using given parser
        :param dict kwargs: Extra keyword arguments for `Cabinet` or `Parser` subclass
            methods
        :return Any: Parsed object read from file
        """
        if parser is True:
            return Parser.load(path, cls.read_content(path, **kwargs), **kwargs)
        elif parser is False:
            return cls.read_content(path, **kwargs)
        elif inspect.isclass(parser) and issubclass(parser, Parser):
            return parser.load_content(cls.read_content(path, **kwargs), **kwargs)

        raise CabinetError(
            'Argument `parser` must be `True`, `False` or a `Parser` subclass')

    @classmethod
    def create(cls, path: str, content: Any, parser: Union[bool, Type[Parser]] = True,
               **kwargs):
        """
        Create a file using a specific protocol.

        :param str path: Path to file within cabinet
        :param Any content: Content to write
        :param Union[bool, Type[Parser]] parser: `True` for parsing using default
            file extension Parser, `False` for no parsing, a `Parser` subclass for
            parsing using given parser
        :param dict kwargs: Extra keyword arguments for `Cabinet` or `Parser` subclass
            methods
        :return: None TODO: define standard return type
        """
        if parser is True:
            return cls.create_content(path, Parser.dump(path, content, **kwargs))
        elif parser is False:
            return cls.create_content(path, content)
        elif inspect.isclass(parser) and issubclass(parser, Parser):
            return cls.create_content(path, parser.dump_content(content, **kwargs))

        raise CabinetError(
            'Argument `parser` must be `True`, `False` or a `Parser` subclass')

    @classmethod
    def delete(cls, path: str, **kwargs):
        """
        Delete a file using a specific protocol.

        :param str path: Path to file within cabinet
        :param dict kwargs: Extra keyword arguments for `Cabinet` or `Parser` subclass
            methods
        """
        cls.delete_content(path, **kwargs)

    @classmethod
    @abstractmethod
    def read_content(cls, path, **kwargs) -> bytes:
        pass  # pragma: no cover

    @classmethod
    @abstractmethod
    def create_content(cls, path, content, **kwargs):
        pass  # pragma: no cover

    @classmethod
    @abstractmethod
    def delete_content(cls, path, **kwargs):
        pass  # pragma: no cover
