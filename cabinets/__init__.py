import os

from cabinets import plugins
from cabinets.cabinet import (
    Cabinet,
    CabinetError,
    register_protocols,
    SUPPORTED_PROTOCOLS,
)
from cabinets.logger import info
from cabinets.parser import (
    Parser,
    register_extensions,
    SUPPORTED_EXTENSIONS,
)

__all__ = [
    Cabinet,
    CabinetError,
    Parser,
    register_protocols,
    register_extensions,
    SUPPORTED_PROTOCOLS,
    SUPPORTED_EXTENSIONS,
]

PLUGIN_PATH = os.environ.get('PLUGIN_PATH', os.path.join(os.getcwd(), 'cabinets'))
if PLUGIN_PATH == os.path.dirname(__file__):
    PLUGIN_PATH = None

PROTOCOLS, EXTENSIONS = plugins.discover_all(custom_plugin_path=PLUGIN_PATH)
# TODO: May want to ensure that there is no overlap in keys
SUPPORTED_PROTOCOLS.update(PROTOCOLS)
SUPPORTED_EXTENSIONS.update(EXTENSIONS)


class InvalidURIError(Exception):
    pass


def from_uri(uri) -> (Cabinet, str):
    try:
        protocol, path = uri.split('://')
    except ValueError:
        info("No protocol identifier specified: using 'file'")
        protocol, path = 'file', uri
    cabinet_ = SUPPORTED_PROTOCOLS.get(protocol)
    if not cabinet_:
        raise InvalidURIError(f"Unknown protocol '{protocol}'")
    if not path:
        raise InvalidURIError("Empty resource path")
    return cabinet_, path


def set_configuration(protocol, **kwargs):
    cabinet_cls = SUPPORTED_PROTOCOLS.get(protocol)
    if not cabinet_cls:
        raise CabinetError(f"Unsupported protocol: '{protocol}'")
    return cabinet_cls.set_configuration(**kwargs)


def read(uri, parser=True, **kwargs):
    """
    Read file content

    :param str path: Path to file
    :param Union[bool, Type[Parser]] parser: `True` for parsing using default
        file extension Parser, `False` for no parsing, a `Parser` subclass for
        parsing using given parser
    :param dict kwargs: Extra keyword arguments for `Cabinet` or `Parser`
    subclass
        methods
    :return Any: Parsed object read from file
    """
    cabinet_, path = from_uri(uri)
    return cabinet_.read(path, parser=parser, **kwargs)


def create(uri, content, parser=True, **kwargs):
    """
    Create a file

    :param str path: Path to file
    :param Any content: Content to write
    :param Union[bool, Type[Parser]] parser: `True` for parsing using default
        file extension Parser, `False` for no parsing, a `Parser` subclass for
        parsing using given parser
    :param dict kwargs: Extra keyword arguments for `Cabinet` or `Parser`
    subclass
        methods
    :return: None TODO: define standard return type
    """
    cabinet_, path = from_uri(uri)
    return cabinet_.create(path, content, parser=parser, **kwargs)


def delete(uri, **kwargs):
    """
    Delete a file

    :param str path: Path to file
    :param dict kwargs: Extra keyword arguments for `Cabinet` or `Parser`
    subclass
        methods
    """
    cabinet_, path = from_uri(uri)
    return cabinet_.delete(path, **kwargs)
