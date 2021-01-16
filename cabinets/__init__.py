import importlib
import os
import pkgutil

from cabinets.cabinet import CabinetBase, SUPPORTED_PROTOCOLS


def load_plugins(plugin_dir):
    path = os.path.join(os.path.dirname(__file__), plugin_dir)
    pkgs = pkgutil.iter_modules((path,))
    for plugin in pkgs:
        pkg = '.'.join((__package__, plugin_dir, plugin.name))
        importlib.import_module(pkg)


load_plugins('cabinet')
load_plugins('parser')


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
