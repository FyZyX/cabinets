import importlib
import importlib.util
import os
import pkgutil
import sys

import cabinets.cabinet
import cabinets.parser
from cabinets.logger import info


def discover(path, prefix):
    plugins = pkgutil.iter_modules(path, prefix + '.')
    for _, name, _ in plugins:
        importlib.import_module(name)
        info(f"Loaded plugin '{name}'")


def discover_all(custom_plugin_path=None):
    discover(cabinets.cabinet.__path__, prefix=cabinets.cabinet.__name__)
    discover(cabinets.parser.__path__, prefix=cabinets.parser.__name__)
    if custom_plugin_path:
        info(f'Using custom plugin path: {custom_plugin_path}')
        sys.path.insert(1, custom_plugin_path)
        for pkg in ['cabinet', 'parser']:
            path = os.path.join(custom_plugin_path, pkg)
            discover((path,), prefix=pkg)
