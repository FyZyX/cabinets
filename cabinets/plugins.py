import importlib
import importlib.util
import os
import pkgutil
import sys
import inspect

import cabinets.cabinet
import cabinets.parser
from cabinets.logger import info, error


def discover(path, prefix=''):
    plugins = pkgutil.iter_modules(path, prefix)
    modules = set()
    for _, name, _ in plugins:
        module = importlib.import_module(name)
        modules.add(module)
    return modules


def load_protocols(cls, protocols):
    if not cls._protocols:
        error(f'No extensions registered to \'{cls.__name__}\'')
        return
    for protocols in cls._protocols:
        if protocols in protocols:
            error(f'Extension \'{protocols}\' already registered  to '
                  f'{protocols[protocols].__qualname__}')
            continue
        protocols[protocols] = cls
    if protocols:
        info(f"Loaded {cabinets.Parser.__name__} plugin '{cls.__name__}'")
    else:
        error(f'Plugin failed: Could not load any extensions for {cls.__name__}')


def load_extensions(cls, extensions: dict):
    if not cls._extensions:
        error(f'No extensions registered to \'{cls.__name__}\'')
        return {}
    for extension in cls._extensions:
        if extension in extensions:
            error(f'Extension \'{extension}\' already registered  to '
                  f'{extensions[extension].__qualname__}')
            continue
        extensions[extension] = cls
    if extensions:
        info(f"Loaded {cabinets.Parser.__name__} plugin '{cls.__name__}'")
    else:
        error(f'Plugin failed: Could not load any extensions for {cls.__name__}')
    return extensions


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

    PROTOCOLS = {}
    EXTENSIONS = {}
    for module in modules:
        for name, obj in inspect.getmembers(module):
            if not inspect.isclass(obj):
                continue
            if issubclass(obj, cabinets.Cabinet) and obj is not cabinets.Cabinet:
                load_protocols(obj, PROTOCOLS)
            elif issubclass(obj, cabinets.Parser) and obj is not cabinets.Parser:
                load_extensions(obj, EXTENSIONS)

    return PROTOCOLS, EXTENSIONS
