import importlib
import importlib.util
import os
import pkgutil
import sys
import inspect

import cabinets.cabinet
import cabinets.parser
from cabinets.logger import info


class CabinetsPluginError(Exception):
    pass


def discover(path, prefix=''):
    plugins = pkgutil.iter_modules(path, prefix)
    modules = set()
    for _, name, _ in plugins:
        module = importlib.import_module(name)
        modules.add(module)
    return modules


def load_protocols(cls, protocols: dict):
    if not cls._protocols:
        raise CabinetsPluginError(f"No protocols registered to '{cls.__name__}'")
    for protocol in cls._protocols:
        if protocol in protocols:
            raise CabinetsPluginError(f'Protocol \'{protocol}\' already registered '
                                      f'to {protocols[protocol].__qualname__}')
        protocols[protocol] = cls
    info(f"Loaded {cabinets.Parser.__name__} plugin '{cls.__name__}'")


# TODO: could be combined with `load_protocols` fairly easily
def load_extensions(cls, extensions: dict):
    if not cls._extensions:
        raise CabinetsPluginError(f"No extensions registered to '{cls.__name__}'")
    for extension in cls._extensions:
        if extension in extensions:
            raise CabinetsPluginError(f"Extension '{extension}' already registered "
                                      f"to {extensions[extension].__qualname__}")
        extensions[extension] = cls
    info(f"Loaded {cabinets.Parser.__name__} plugin '{cls.__name__}'")


def discover_all(custom_plugin_path=None):
    modules = set()
    built_in_cabinet_modules = discover(cabinets.cabinet.__path__,
                                        prefix=cabinets.cabinet.__name__ + '.')
    built_in_parser_modules = discover(cabinets.parser.__path__,
                                       prefix=cabinets.parser.__name__ + '.')
    modules.update(built_in_cabinet_modules)
    modules.update(built_in_parser_modules)
    if custom_plugin_path:
        for pkg in ('cabinet', 'parser'):
            path = os.path.join(custom_plugin_path, pkg)
            sys.path.insert(1, path)
            custom_modules = discover((path,))
            modules.update(custom_modules)

    PROTOCOLS, EXTENSIONS = {}, {}
    for module in modules:
        for name, obj in inspect.getmembers(module):
            if not inspect.isclass(obj):
                continue
            if issubclass(obj, cabinets.Cabinet) and obj is not cabinets.Cabinet:
                load_protocols(obj, PROTOCOLS)
            elif issubclass(obj, cabinets.Parser) and obj is not cabinets.Parser:
                load_extensions(obj, EXTENSIONS)

    return PROTOCOLS, EXTENSIONS
