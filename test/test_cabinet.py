import json
import unittest

from cabinets.cabinet import Cabinet


class TestCabinet(unittest.TestCase):
    def test_read_json(self):
        data = Cabinet.read('file://fixtures/sample.json')
        self.assertEqual({'hello': 'world'}, data)

    def test_write_json(self):
        file = 'fixtures/sample.json'
        Cabinet.write(f'file://{file}', {'hello': 'world'})
        with open(file) as fh:
            data = json.load(fh)
        self.assertEqual({'hello': 'world'}, data)


if __name__ == '__main__':
    unittest.main()
