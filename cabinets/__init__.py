import os
from pathlib import Path, PurePath
from typing import Union, Type, Any, List

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


def _parse_protocol(uri: Union[str, Path]) -> (Cabinet, str):
    """Separate a URI string or Path object into a protocol and path

    :param Union[str, Path] uri: String URI or Path object representing a file
    :return: Protocol to use for reading the file and its associated path
    :rtype: (str, str)
    """
    if isinstance(uri, PurePath):
        # only standard Path objects have `resolve()`, however checking for
        # Path instead of PurePath breaks testing with the `pyfakefs` library
        # which mocks PosixPath and WindowsPath objects with library types
        # which use a library type Path base class
        try:
            uri = uri.resolve().as_uri()
        except AttributeError:
            uri = uri.as_uri()

    parts = uri.split('://')
    if len(parts) < 2:
        debug("No cabinet protocol identifier specified: using 'file'")
        protocol, path = 'file', uri
    elif len(parts) > 2:
        raise InvalidURIError("Must specify a single protocol separator '://'")
    else:
        protocol, path = parts

    return protocol, path


def from_uri(uri: Union[str, Path]) -> (Cabinet, str):
    """Creates a Cabinet instance from a URI or Path

    :param Union[str, Path] uri: String URI or Path object representing a file
    :return: Cabinet class to use and path at which to find file using the Cabinet
    :rtype: (Cabinet, str)
    """
    protocol, path = _parse_protocol(uri)

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


def list(directory_uri: Union[str, Path], **kwargs: Any) -> List[str]:
    """
    List files in a directory. Will not include subdirectories.

    :param Union[str, Path] directory_uri: Path to directory including protocol
        identifier prefix (protocol://) or Path object
    :param kwargs: Extra keyword arguments for `Cabinet` or `Parser` subclass
        methods
    :return List[str]: List of filenames in directory
    """
    cabinet_, dir = from_uri(directory_uri)
    return cabinet_.list(dir, **kwargs)
