import importlib
import importlib.util
import os
import pkgutil

from cabinets.logger import info


def discover_built_in(plugin_path):
    plugins = pkgutil.iter_modules((
        os.path.join(os.path.dirname(__file__), plugin_path),
    ))
    for plugin in plugins:
        pkg = '.'.join((__package__, plugin_path, plugin.name))
        importlib.import_module(pkg)
        info(f"Loaded custom plugin '{plugin.name}'")


def discover_custom(*paths):
    plugins = pkgutil.iter_modules(paths)
    for plugin in plugins:
        plugin.module_finder.find_module(plugin.name).load_module()
        info(f"Loaded custom plugin '{plugin.name}'")
