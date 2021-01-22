from abc import ABC, abstractmethod

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
    def read(cls, path, raw=False):
        if raw:
            return cls.read_content(path)
        else:
            return Parser.load(path, cls.read_content(path))

    @classmethod
    def create(cls, path, content, raw=False):
        if raw:
            return cls.create_content(path, content)
        else:
            return cls.create_content(path, Parser.dump(path, content))

    @classmethod
    def delete(cls, path):
        cls.delete_content(path)

    @classmethod
    @abstractmethod
    def read_content(cls, path) -> bytes:
        pass  # pragma: no cover

    @classmethod
    @abstractmethod
    def create_content(cls, path, content):
        pass  # pragma: no cover

    @classmethod
    @abstractmethod
    def delete_content(cls, path):
        pass  # pragma: no cover
