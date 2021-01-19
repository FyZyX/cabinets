import os
from unittest import TestCase

from cabinets import plugins, SUPPORTED_PROTOCOLS, SUPPORTED_EXTENSIONS


class TestPlugins(TestCase):

    def test_load_plugins_from_built_in(self):
        plugins.discover_all(custom_plugin_path=None)
        self.assertNotIn('mock', SUPPORTED_PROTOCOLS)
        self.assertNotIn('mock', SUPPORTED_EXTENSIONS)

        self.assertIn('file', SUPPORTED_PROTOCOLS)
        self.assertIn('s3', SUPPORTED_PROTOCOLS)
        self.assertIn('yml', SUPPORTED_EXTENSIONS)
        self.assertIn('yaml', SUPPORTED_EXTENSIONS)
        self.assertIn('json', SUPPORTED_EXTENSIONS)
        self.assertIn('pickle', SUPPORTED_EXTENSIONS)

    def test_load_plugins_from_custom_path(self):
        plugin_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'plugins')
        plugins.discover_all(custom_plugin_path=plugin_path)
        self.assertIn('mock', SUPPORTED_PROTOCOLS)
        self.assertIn('mock', SUPPORTED_EXTENSIONS)

        self.assertIn('file', SUPPORTED_PROTOCOLS)
        self.assertIn('s3', SUPPORTED_PROTOCOLS)
        self.assertIn('yml', SUPPORTED_EXTENSIONS)
        self.assertIn('yaml', SUPPORTED_EXTENSIONS)
        self.assertIn('json', SUPPORTED_EXTENSIONS)
        self.assertIn('pickle', SUPPORTED_EXTENSIONS)
