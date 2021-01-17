import os

from cabinets import plugins
from cabinets.cabinet import CabinetBase, SUPPORTED_PROTOCOLS


plugins.discover_built_in('cabinet')
plugins.discover_built_in('parser')

PLUGIN_PATHS = os.environ.get('PLUGIN_PATHS')
if PLUGIN_PATHS:
    plugins.discover_custom(*PLUGIN_PATHS.split(','))


class InvalidURIError(Exception):
    pass


def from_uri(uri) -> (CabinetBase, str):
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


def read(uri, raw=False):
    cabinet, path = from_uri(uri)
    return cabinet.read(path, raw=raw)


def create(uri, content, raw=False):
    cabinet, path = from_uri(uri)
    return cabinet.create(path, content, raw=raw)


def delete(uri):
    cabinet, path = from_uri(uri)
    return cabinet.delete(path)
