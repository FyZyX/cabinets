import os
from unittest import TestCase

import cabinets
from cabinets import (register_protocols,
                      register_extensions,
                      CabinetError,
                      Cabinet,
                      Parser)
from cabinets.parser import ParserError


class MockCabinet(Cabinet):
    @classmethod
    def set_configuration(cls, **kwargs):
        return NotImplemented

    @classmethod
    def read_content(cls, path, **kwargs) -> bytes:
        return NotImplemented

    @classmethod
    def create_content(cls, path, content, **kwargs):
        return NotImplemented

    @classmethod
    def delete_content(cls, path, **kwargs):
        return NotImplemented


class MockParser(Parser):
    @classmethod
    def load_content(cls, content: bytes, **kwargs):
        return NotImplemented

    @classmethod
    def dump_content(cls, data, **kwargs):
        return NotImplemented


class TestPlugins(TestCase):

    def tearDown(self) -> None:
        MockCabinet._protocols = set()
        MockParser._extensions = set()

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

    def test_load_protocols(self):
        register_protocols('mock')(MockCabinet)
        protocols = {}
        cabinets.plugins.load_to_cache(MockCabinet, protocols, cabinets.Cabinet)
        self.assertDictEqual(protocols, {'mock': MockCabinet})

    def test_load_protocols_fails_on_no_protocols(self):
        with self.assertRaises(cabinets.plugins.CabinetsPluginError):
            cabinets.plugins.load_to_cache(MockCabinet, {}, cabinets.Cabinet)

    def test_load_protocols_fails_on_repeated_protocol(self):
        register_protocols('mock')(MockCabinet)
        protocols = {}
        cabinets.plugins.load_to_cache(MockCabinet, protocols, cabinets.Cabinet)
        with self.assertRaises(cabinets.plugins.CabinetsPluginError):
            cabinets.plugins.load_to_cache(MockCabinet, protocols, cabinets.Cabinet)

    def test_load_extensions(self):
        register_extensions('mock')(MockParser)
        extensions = {}
        cabinets.plugins.load_to_cache(MockParser, extensions, cabinets.Parser)
        self.assertDictEqual(extensions, {'mock': MockParser})

    def test_load_extensions_fails_on_no_extensions(self):
        with self.assertRaises(cabinets.plugins.CabinetsPluginError):
            cabinets.plugins.load_to_cache(MockParser, {}, cabinets.Parser)

    def test_load_extensions_fails_on_repeated_extension(self):
        register_extensions('mock')(MockParser)
        extensions = {}
        cabinets.plugins.load_to_cache(MockParser, extensions, cabinets.Parser)
        with self.assertRaises(cabinets.plugins.CabinetsPluginError):
            cabinets.plugins.load_to_cache(MockParser, extensions, cabinets.Parser)


class TestRegisterProtocols(TestCase):

    def tearDown(self) -> None:
        MockCabinet._protocols = set()

    def test_register_protocols_succeeds(self):
        cls = register_protocols('mock')(MockCabinet)
        self.assertIs(cls, MockCabinet)
        self.assertIn('mock', MockCabinet._protocols)

    def test_register_protocols_fails_on_double_register(self):
        with self.assertRaises(CabinetError):
            _ = register_protocols('mock')(MockCabinet)
            _ = register_protocols('mock')(MockCabinet)

    def test_register_protocols_fails_on_subclass_check(self):
        with self.assertRaises(CabinetError) as err:
            register_protocols('mock')(int)
        self.assertIn('not a subclass', str(err.exception))

    def test_register_protocols_fails_on_parser_subclass_check(self):
        with self.assertRaises(CabinetError) as err:
            register_protocols('mock')(MockParser)
        self.assertIn('not a subclass', str(err.exception))

    def test_register_protocols_fails_on_attempt_to_register_instance(self):
        with self.assertRaises(CabinetError) as err:
            register_protocols('mock')(42)
        self.assertIn('must be a class', str(err.exception))


class TestRegisterExtensions(TestCase):

    def tearDown(self) -> None:
        MockParser._extensions = set()

    def test_register_extensions_succeeds(self):
        cls = register_extensions('mock')(MockParser)
        self.assertIs(cls, MockParser)
        self.assertIn('mock', MockParser._extensions)

    def test_register_extensions_fails_on_double_register(self):
        with self.assertRaises(ParserError):
            _ = register_extensions('mock')(MockParser)
            _ = register_extensions('mock')(MockParser)

    def test_register_extensions_fails_on_subclass_check(self):
        with self.assertRaises(ParserError) as err:
            register_extensions('mock')(int)
        self.assertIn('not a subclass', str(err.exception))

    def test_register_extensions_fails_on_cabinet_subclass_check(self):
        with self.assertRaises(ParserError) as err:
            register_extensions('mock')(MockCabinet)
        self.assertIn('not a subclass', str(err.exception))

    def test_register_extensions_fails_on_attempt_to_register_instance(self):
        with self.assertRaises(ParserError) as err:
            register_extensions('mock')(42)
        self.assertIn('must be a class', str(err.exception))
