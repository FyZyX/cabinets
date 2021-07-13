import os
from pathlib import Path
from typing import Union, Type, Any

from cabinets import plugins
from cabinets.cabinet import (
    Cabinet,
    CabinetError,
    register_protocols,
    SUPPORTED_PROTOCOLS,
)
from cabinets.logger import debug
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


def from_uri(uri: Union[str, Path]) -> (Cabinet, str):
    """

    :param Union[str, Path] uri:
    :return:
    """
    if isinstance(uri, Path):
        uri = uri.as_uri()

    try:
        protocol, path = uri.split('://')
    except ValueError:
        debug("No cabinet protocol identifier specified: using 'file'")
        protocol, path = 'file', uri
    cabinet_ = SUPPORTED_PROTOCOLS.get(protocol)
    if not cabinet_:
        raise InvalidURIError(f"Unknown protocol '{protocol}'")
    if not path:
        raise InvalidURIError("Empty resource path")
    return cabinet_, path


def set_configuration(protocol, **kwargs):
    """
    Set configuration parameters for a Cabinet.

    :param str protocol: Protocol identifier of Cabinet
    :param dict kwargs: Configuration parameters passed to delegate method
    """
    cabinet_cls = SUPPORTED_PROTOCOLS.get(protocol)
    if not cabinet_cls:
        raise CabinetError(f"Unsupported protocol: '{protocol}'")
    return cabinet_cls.set_configuration(**kwargs)


def read(uri: Union[str, Path], parser: Union[bool, Type[Parser]] = True,
         **kwargs: Any):
    """
    Read file contents.

    :param  Union[str, Path] uri: Path to file including protocol identifier prefix (
        protocol://) or Path object
    :param Union[bool, Type[Parser]] parser: `True` for parsing using default
        file extension Parser, `False` for no parsing, a `Parser` subclass for
        parsing using given parser
    :param kwargs: Extra keyword arguments for `Cabinet` or `Parser` subclass
        methods
    :return Any: Parsed object read from file
    """
    cabinet_, path = from_uri(uri)
    return cabinet_.read(path, parser=parser, **kwargs)


def create(uri: Union[str, Path], content: Any,
           parser: Union[bool, Type[Parser]] = True, **kwargs: Any):
    """
    Create a file.

    :param Union[str, Path] uri: Path to file including protocol identifier prefix (
        protocol://) or Path object
    :param Any content: Content to write
    :param Union[bool, Type[Parser]] parser: `True` for parsing using default
        file extension Parser, `False` for no parsing, a `Parser` subclass for
        parsing using given parser
    :param kwargs: Extra keyword arguments for `Cabinet` or `Parser` subclass
        methods
    :return: None
    """
    cabinet_, path = from_uri(uri)
    # TODO: define standard return type
    return cabinet_.create(path, content, parser=parser, **kwargs)


def delete(uri: Union[str, Path], **kwargs: Any):
    """
    Delete a file.

    :param Union[str, Path] uri: Path to file including protocol identifier prefix (
        protocol://) or Path object
    :param kwargs: Extra keyword arguments for `Cabinet` or `Parser` subclass
        methods
    """
    cabinet_, path = from_uri(uri)
    return cabinet_.delete(path, **kwargs)
