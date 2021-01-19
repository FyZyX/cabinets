import os
from unittest import TestCase

import cabinets


class TestPlugins(TestCase):

    def test_load_plugins_from_built_in(self):
        PROTOCOLS, EXTENSIONS = cabinets.plugins.discover_all(custom_plugin_path=None)
        self.assertNotIn('mock', PROTOCOLS)
        self.assertNotIn('mock', EXTENSIONS)

        self.assertIn('file', PROTOCOLS)
        self.assertIn('s3', PROTOCOLS)
        self.assertIn('yml', EXTENSIONS)
        self.assertIn('yaml', EXTENSIONS)
        self.assertIn('json', EXTENSIONS)
        self.assertIn('pickle', EXTENSIONS)

    def test_load_plugins_from_custom_path(self):
        plugin_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'plugins')
        PROTOCOLS, EXTENSIONS = cabinets.plugins.discover_all(
            custom_plugin_path=plugin_path)
        self.assertIn('mock', PROTOCOLS)
        self.assertIn('mock', EXTENSIONS)

        self.assertIn('file', PROTOCOLS)
        self.assertIn('s3', PROTOCOLS)
        self.assertIn('yml', EXTENSIONS)
        self.assertIn('yaml', EXTENSIONS)
        self.assertIn('json', EXTENSIONS)
        self.assertIn('pickle', EXTENSIONS)
