import json
import os
import unittest

from cabinets.cabinet import Cabinet


class TestCabinet(unittest.TestCase):
    def test_read_json(self):
        protocol, filename = 'file', 'fixtures/sample.json'
        data = Cabinet.read(f'{protocol}://{filename}')
        self.assertEqual({'hello': 'world'}, data)

    def test_create_json(self):
        protocol, filename = 'file', 'fixtures/sample.json'
        Cabinet.create(f'{protocol}://{filename}', {'hello': 'world'})
        with open(filename) as fh:
            data = json.load(fh)
        self.assertEqual({'hello': 'world'}, data)

    def test_delete(self):
        protocol, filename = 'file', 'fixtures/delete-me.json'
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


if __name__ == '__main__':
    unittest.main()
