from cabinets.cabinet import CabinetBase, SUPPORTED_PROTOCOLS
from cabinets.cabinet.file import FileCabinet  # noqa: F401
from cabinets.cabinet.s3 import S3Cabinet  # noqa: F401
from cabinets.parser.pickle import PickleParser  # noqa: F401
from cabinets.parser.json import JSONParser  # noqa: F401
from cabinets.parser.yaml import YAMLParser  # noqa: F401
from cabinets.parser.csv import CSVParser  # noqa: F401


class InvalidURIError(Exception):
    pass


class Cabinets:

    @classmethod
    def from_uri(cls, uri) -> (CabinetBase, str):
        try:
            protocol, path = uri.split('://')
        except ValueError:
            raise InvalidURIError("Missing protocol identifier")
        cabinet = SUPPORTED_PROTOCOLS.get(protocol)
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
