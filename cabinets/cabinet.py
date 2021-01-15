from abc import ABC, abstractmethod
from cabinets.parser import Parser

_SUPPORTED_PROTOCOLS = {}


def register_protocols(*protocols):
    def decorate_cabinet(cabinet: CabinetBase):
        for protocol in protocols:
            _SUPPORTED_PROTOCOLS[protocol] = cabinet
        return cabinet

    return decorate_cabinet


class CabinetBase(ABC):

    @classmethod
    @abstractmethod
    def set_configuration(cls, **kwargs):
        pass

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
        pass

    @classmethod
    @abstractmethod
    def _create_content(cls, path, content):
        pass

    @classmethod
    @abstractmethod
    def _delete_content(cls, path):
        pass



class Cabinets:

    @classmethod
    def from_uri(cls, uri) -> (CabinetBase, str):
        protocol, path = uri.split('://')
        cabinet = _SUPPORTED_PROTOCOLS.get(protocol)
        if not cabinet:
            raise KeyError(f'Could not find Cabinet for protocol key \'{protocol}\'')
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
