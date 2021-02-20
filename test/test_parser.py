import os

from pyfakefs import fake_filesystem_unittest

import cabinets
from cabinets import Parser


class MockTextParser(Parser):
    @classmethod
    def load_content(cls, content: bytes, **kwargs):
        return {'mock-parser': content.decode('utf-8')}


class TestParserArgument(fake_filesystem_unittest.TestCase):
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')

    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory(self.fixture_path)

    def test_read_plain_text_standard_parser(self):
        protocol = 'file'
        filename = os.path.join(self.fixture_path, 'sample_small.txt')
        data = cabinets.read(f'{protocol}://{filename}', parser=True)
        expected = "I am sample text!"
        self.assertIsInstance(data, str)
        self.assertEqual(expected, data)

    def test_read_plain_text_no_parser(self):
        protocol = 'file'
        filename = os.path.join(self.fixture_path, 'sample_small.txt')
        data = cabinets.read(f'{protocol}://{filename}', parser=False)
        expected = bytes("I am sample text!", encoding='utf-8')
        self.assertIsInstance(data, bytes)
        self.assertEqual(expected, data)

    def test_read_plain_text_custom_parser(self):
        protocol = 'file'
        filename = os.path.join(self.fixture_path, 'sample_small.txt')
        data = cabinets.read(f'{protocol}://{filename}', parser=MockTextParser)
        expected = {'mock-parser': "I am sample text!"}
        self.assertIsInstance(data, dict)
        self.assertDictEqual(expected, data)
