import os
from unittest import TestCase

import cabinets
from cabinets import register_protocols, CabinetError
from test.test_cabinet import MockCabinet


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


class TestRegisterProtocols(TestCase):

    def test_register_protocols_succeeds(self):
        cls = register_protocols('mock')(MockCabinet)
        self.assertIs(cls, MockCabinet)
        self.assertIn('mock', MockCabinet._protocols)

    def test_register_protocols_fails_on_subclass_check(self):
        with self.assertRaises(CabinetError) as err:
            register_protocols('mock')(int)
        self.assertIn('not a subclass', str(err.exception))

    def test_register_protocols_fails_on_attempt_to_register_instance(self):
        with self.assertRaises(CabinetError) as err:
            register_protocols('mock')(42)
        self.assertIn('must be a class', str(err.exception))
