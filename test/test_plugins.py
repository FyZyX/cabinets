import os
from unittest import TestCase

import cabinets


class TestPlugins(TestCase):

    def setUp(self) -> None:
        cabinets.SUPPORTED_PROTOCOLS.clear()
        cabinets.SUPPORTED_EXTENSIONS.clear()

    def test_load_plugins_from_built_in(self):
        cabinets.plugins.discover_all(custom_plugin_path=None)
        self.assertNotIn('mock', cabinets.SUPPORTED_PROTOCOLS)
        self.assertNotIn('mock', cabinets.SUPPORTED_EXTENSIONS)

        self.assertIn('file', cabinets.SUPPORTED_PROTOCOLS)
        self.assertIn('s3', cabinets.SUPPORTED_PROTOCOLS)
        self.assertIn('yml', cabinets.SUPPORTED_EXTENSIONS)
        self.assertIn('yaml', cabinets.SUPPORTED_EXTENSIONS)
        self.assertIn('json', cabinets.SUPPORTED_EXTENSIONS)
        self.assertIn('pickle', cabinets.SUPPORTED_EXTENSIONS)

    def test_load_plugins_from_custom_path(self):
        plugin_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'plugins')
        cabinets.plugins.discover_all(custom_plugin_path=plugin_path)
        self.assertIn('mock', cabinets.SUPPORTED_PROTOCOLS)
        self.assertIn('mock', cabinets.SUPPORTED_EXTENSIONS)

        self.assertIn('file', cabinets.SUPPORTED_PROTOCOLS)
        self.assertIn('s3', cabinets.SUPPORTED_PROTOCOLS)
        self.assertIn('yml', cabinets.SUPPORTED_EXTENSIONS)
        self.assertIn('yaml', cabinets.SUPPORTED_EXTENSIONS)
        self.assertIn('json', cabinets.SUPPORTED_EXTENSIONS)
        self.assertIn('pickle', cabinets.SUPPORTED_EXTENSIONS)
