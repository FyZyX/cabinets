from abc import ABC, abstractmethod
from cabinets.parser import Parser

_SUPPORTED_PROTOCOLS = {}


class CabinetError(Exception):
    pass


def register_protocols(*protocols):
    def decorate_cabinet(cabinet):
        try:
            if not issubclass(cabinet, CabinetBase):
                raise CabinetError(f"Cannot register protocol: Type "
                                   f"'{cabinet.__name__}' is not a subclass of "
                                   f"'{CabinetBase.__name__}'")
        except TypeError:
            raise CabinetError(
                "Cannot register protocol: Decorated object must be a class")
        for protocol in protocols:
            if protocol in _SUPPORTED_PROTOCOLS:
                raise CabinetError(f"Protocol already associated with Cabinet "
                                   f"'{_SUPPORTED_PROTOCOLS[protocol].__qualname__}'")
            _SUPPORTED_PROTOCOLS[protocol] = cabinet
        return cabinet

    return decorate_cabinet


class CabinetBase(ABC):

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


class InvalidURIError(Exception):
    pass


class Cabinets:

    @classmethod
    def from_uri(cls, uri) -> (CabinetBase, str):
        try:
            protocol, path = uri.split('://')
        except ValueError:
            raise InvalidURIError("Missing protocol identifier")
        cabinet = _SUPPORTED_PROTOCOLS.get(protocol)
        if not cabinet:
            raise InvalidURIError(f"Unknown protocol '{protocol}'")
        if not path:
            raise InvalidURIError("Empty resource path")
        return cabinet, path

    @classmethod
    def read(cls, uri, raw=False):
        cabinet, path = cls.from_uri(uri)
        return cabinet.read(path, raw=raw)

    @classmethod
    def create(cls, uri, content, raw=False):
        cabinet, path = cls.from_uri(uri)
        return cabinet.create(path, content, raw=raw)

    @classmethod
    def delete(cls, uri):
        cabinet, path = cls.from_uri(uri)
        return cabinet.delete(path)
