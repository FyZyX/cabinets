from abc import ABC, abstractmethod

from cabinets.parser import Parser

SUPPORTED_PROTOCOLS = {}


class CabinetError(Exception):
    pass


def register_protocols(*protocols):
    def decorate_cabinet(cabinet):
        try:
            if not issubclass(cabinet, Cabinet):
                raise CabinetError(f"Cannot register protocol: Type "
                                   f"'{cabinet.__name__}' is not a subclass of "
                                   f"'{Cabinet.__name__}'")
        except TypeError:
            raise CabinetError(
                "Cannot register protocol: Decorated object must be a class")
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
    def read(cls, path, raw=False):
        if raw:
            return cls._read_content(path)
        else:
            return Parser.load(path, cls._read_content(path))

    @classmethod
    def create(cls, path, content, raw=False):
        if raw:
            return cls._create_content(path, content)
        else:
            return cls._create_content(path, Parser.dump(path, content))

    @classmethod
    def delete(cls, path):
        cls._delete_content(path)

    @classmethod
    @abstractmethod
    def _read_content(cls, path) -> bytes:
        pass  # pragma: no cover

    @classmethod
    @abstractmethod
    def _create_content(cls, path, content):
        pass  # pragma: no cover

    @classmethod
    @abstractmethod
    def _delete_content(cls, path):
        pass  # pragma: no cover
