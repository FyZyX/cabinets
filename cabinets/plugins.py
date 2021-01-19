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
                if not obj._protocols:
                    error(f'No protocols registered to \'{name}\'')
                    continue
                for protocol in obj._protocols:
                    if protocol in PROTOCOLS:
                        error(f'Protocol \'{protocol}\' already registered to '
                              f'{PROTOCOLS[protocol].__qualname__}')
                        continue
                    PROTOCOLS[protocol] = obj
                info(f"Loaded {cabinets.Cabinet.__name__} plugin '{name}'")
            elif issubclass(obj, cabinets.Parser) and obj is not cabinets.Parser:
                if not obj._extensions:
                    error(f'No extensions registered to \'{name}\'')
                    continue
                for extension in obj._extensions:
                    if extension in EXTENSIONS:
                        error(f'Extension \'{extension}\' already registered  to '
                              f'{EXTENSIONS[extension].__qualname__}')
                        continue
                    EXTENSIONS[extension] = obj
                info(f"Loaded {cabinets.Parser.__name__} plugin '{name}'")
    return PROTOCOLS, EXTENSIONS
