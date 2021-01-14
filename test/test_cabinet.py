import json
import os
import unittest
from types import SimpleNamespace

from cabinets.cabinet import Cabinet
from pyfakefs import fake_filesystem_unittest


class TestCabinet(fake_filesystem_unittest.TestCase):
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')

    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory(self.fixture_path)

    def test_read_json(self):
        protocol = 'file'
        filename = os.path.join(self.fixture_path, 'sample.json')
        data = Cabinet.read(f'{protocol}://{filename}')
        self.assertEqual({'hello': 'world'}, data)

    def test_create_json(self):
        protocol, filename = 'file', 'tmp/sample.json'
        Cabinet.create(f'{protocol}://{filename}', {'hello': 'world'})
        with open(filename) as fh:
            data = json.load(fh)
        self.assertEqual({'hello': 'world'}, data)

    def test_delete(self):
        protocol, filename = 'file', 'delete-me.json'
        data = {'hello': 'world'}
        with open(filename, 'w') as fh:
            json.dump(data, fh)
        self.assertTrue(os.path.isfile(filename))
        Cabinet.delete(f'{protocol}://{filename}')
        self.assertFalse(os.path.isfile(filename))

    def test_read_create_json(self):
        protocol, filename = 'file', 'test.json'
        data = {'I': {'am': ['nested', 1, 'object', None]}}
        Cabinet.create(f'{protocol}://{filename}', data)
        result = Cabinet.read(f'{protocol}://{filename}')
        self.assertDictEqual(data, result)

    def test_read_create_yaml(self):
        protocol, filename = 'file', 'test.yml'
        data = {'I': {'am': ['nested', 1, 'object', None]}}
        Cabinet.create(f'{protocol}://{filename}', data)
        result = Cabinet.read(f'{protocol}://{filename}')
        self.assertDictEqual(data, result)

    def test_read_create_pickle(self):
        protocol, filename = 'file', 'test.pickle'
        data = {'I': {'am': ['nested', 1 + 2j, 'object', None],
                      'purple': SimpleNamespace(egg=True, fish=42)}}
        Cabinet.create(f'{protocol}://{filename}', data)
        result = Cabinet.read(f'{protocol}://{filename}')
        self.assertDictEqual(data, result)


if __name__ == '__main__':
    unittest.main()
