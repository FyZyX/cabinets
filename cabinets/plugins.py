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


def load_to_cache(cls, cache: dict, allowed_type: type):
    if not issubclass(cls, allowed_type):
        raise CabinetsPluginError(
            f"Plugin type not allowed: {cls.__name__} is not a subclass of "
            f"{allowed_type.__name__}")

    if issubclass(cls, cabinets.Cabinet):
        keys = cls._protocols
    elif issubclass(cls, cabinets.Parser):
        keys = cls._extensions
    else:
        raise CabinetsPluginError(
            f"Cannot load plugin: type {cls.__name__} is not allowed")
    if not keys:
        raise CabinetsPluginError(
            f"No {allowed_type.__name__}s registered to '{cls.__name__}'")
    for key in keys:
        if key in cache:
            raise CabinetsPluginError(
                f"Plugin already registered: {allowed_type.__name__} '{key}' is "
                f"currently associated with {cache[key].__qualname__}")
        cache[key] = cls
    info(f"Loaded {allowed_type.__name__} plugin '{cls.__name__}'")


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
                load_to_cache(obj, PROTOCOLS, cabinets.Cabinet)
            elif issubclass(obj, cabinets.Parser) and obj is not cabinets.Parser:
                load_to_cache(obj, EXTENSIONS, cabinets.Parser)

    return PROTOCOLS, EXTENSIONS
