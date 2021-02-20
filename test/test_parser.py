import os
import json
from typing import Any

from pyfakefs import fake_filesystem_unittest

import cabinets
from cabinets import Parser


class MockTextParser(Parser):

    @classmethod
    def dump_content(cls, data: Any, **kwargs):
        data['mock'] = 'parser'
        return json.dumps(data)

    @classmethod
    def load_content(cls, content: bytes, **kwargs):
        return {'mock-parser': content.decode('utf-8')}


class TestParserArgument(fake_filesystem_unittest.TestCase):
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')

    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory(self.fixture_path)

    def test_read_plain_text_default_parser(self):
        protocol = 'file'
        filename = os.path.join(self.fixture_path, 'sample_small.txt')
        data = cabinets.read(f'{protocol}://{filename}', parser=True)
        self.assertIsInstance(data, str)
        expected = "I am sample text!"
        self.assertEqual(expected, data)

    def test_read_plain_text_no_parser(self):
        protocol = 'file'
        filename = os.path.join(self.fixture_path, 'sample_small.txt')
        data = cabinets.read(f'{protocol}://{filename}', parser=False)
        self.assertIsInstance(data, bytes)
        expected = bytes("I am sample text!", encoding='utf-8')
        self.assertEqual(expected, data)

    def test_read_plain_text_custom_parser(self):
        protocol = 'file'
        filename = os.path.join(self.fixture_path, 'sample_small.txt')
        data = cabinets.read(f'{protocol}://{filename}', parser=MockTextParser)
        self.assertIsInstance(data, dict)
        expected = {'mock-parser': "I am sample text!"}
        self.assertDictEqual(expected, data)

    def test_create_json_default_parser(self):
        protocol, filename = 'file', 'tmp/sample.json'
        content = {"hello": "world"}
        cabinets.create(f'{protocol}://{filename}', content, parser=True)
        with open(filename) as fh:
            data = fh.read()
        self.assertEqual('{"hello": "world"}', data)

    def test_create_json_default_parser_fails(self):
        protocol, filename = 'file', 'tmp/sample.json'
        content = bytes('{"test":"bytes"}', encoding="utf-8")
        with self.assertRaises(TypeError):
            cabinets.create(f'{protocol}://{filename}', content, parser=True)

    def test_create_json_no_parser(self):
        protocol, filename = 'file', 'tmp/sample.json'
        content = bytes('{"test":"bytes"}', encoding="utf-8")
        cabinets.create(f'{protocol}://{filename}', content, parser=False)
        with open(filename) as fh:
            data = json.load(fh)
        self.assertEqual({"test": "bytes"}, data)

    def test_create_json_custom_parser(self):
        protocol, filename = 'file', 'tmp/sample.json'
        content = {"hello": "world"}
        cabinets.create(f'{protocol}://{filename}', content, parser=MockTextParser)
        with open(filename) as fh:
            data = json.load(fh)
        self.assertDictEqual({"hello": "world", "mock": "parser"}, data)

    def test_read_text_custom_parser_raises(self):
        with self.assertRaises(cabinets.CabinetError):
            cabinets.read(os.path.join(self.fixture_path, 'sample.txt'), parser=str)
        with self.assertRaises(cabinets.CabinetError):
            cabinets.read(os.path.join(self.fixture_path, 'sample.txt'), parser=1)
        with self.assertRaises(cabinets.CabinetError):
            cabinets.read(os.path.join(self.fixture_path, 'sample.txt'), parser=None)

    def test_create_text_custom_parser_raises(self):
        with self.assertRaises(cabinets.CabinetError):
            cabinets.create('file://tmp/sample.txt', "foo", parser=str)
        with self.assertRaises(cabinets.CabinetError):
            cabinets.create('file://tmp/sample.txt', "foo", parser=1)
        with self.assertRaises(cabinets.CabinetError):
            cabinets.create('file://tmp/sample.txt', "foo", parser=None)
