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
    def read(cls, path, raw=False, **kwargs):
        if raw:
            return cls.read_content(path)
        else:
            return Parser.load(path, cls.read_content(path), **kwargs)

    @classmethod
    def create(cls, path, content, raw=False, **kwargs):
        if raw:
            return cls.create_content(path, content)
        else:
            return cls.create_content(path, Parser.dump(path, content, **kwargs))

    @classmethod
    def delete(cls, path, **kwargs):
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
