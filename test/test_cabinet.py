import json
import os
import unittest
from types import SimpleNamespace

import boto3
from moto import mock_s3
from pyfakefs import fake_filesystem_unittest

import cabinets
from cabinets import InvalidURIError, CabinetError
from cabinets.cabinet.file_cabinet import FileCabinet
from cabinets.cabinet.s3_cabinet import S3Cabinet


class TestFileCabinet(fake_filesystem_unittest.TestCase):
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')

    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory(self.fixture_path)

    def test_read_json(self):
        protocol = 'file'
        filename = os.path.join(self.fixture_path, 'sample.json')
        data = cabinets.read(f'{protocol}://{filename}')
        self.assertEqual({'hello': 'world'}, data)

    def test_create_json(self):
        protocol, filename = 'file', 'tmp/sample.json'
        cabinets.create(f'{protocol}://{filename}', {'hello': 'world'})
        with open(filename) as fh:
            data = json.load(fh)
        self.assertEqual({'hello': 'world'}, data)

    def test_delete(self):
        protocol, filename = 'file', 'delete-me.json'
        data = {'hello': 'world'}
        with open(filename, 'w') as fh:
            json.dump(data, fh)
        self.assertTrue(os.path.isfile(filename))
        cabinets.delete(f'{protocol}://{filename}')
        self.assertFalse(os.path.isfile(filename))

    def test_read_create_json(self):
        protocol, filename = 'file', 'test.json'
        data = {'I': {'am': ['nested', 1, 'object', None]}}
        cabinets.create(f'{protocol}://{filename}', data)
        cabinets.create(f'{protocol}://{filename}', data)
        result = cabinets.read(f'{protocol}://{filename}')
        self.assertDictEqual(data, result)

    def test_read_create_yaml(self):
        protocol, filename = 'file', 'test.yml'
        data = {'I': {'am': ['nested', 1, 'object', None]}}
        cabinets.create(f'{protocol}://{filename}', data)
        result = cabinets.read(f'{protocol}://{filename}')
        self.assertDictEqual(data, result)

    def test_read_create_pickle(self):
        protocol, filename = 'file', 'test.pickle'
        data = {'I': {'am': ['nested', 1 + 2j, 'object', None],
                      'purple': SimpleNamespace(egg=True, fish=42)}}
        cabinets.create(f'{protocol}://{filename}', data)
        result = cabinets.read(f'{protocol}://{filename}')
        self.assertDictEqual(data, result)

    def test_read_plain_text(self):
        protocol = 'file'
        filename = os.path.join(self.fixture_path, 'sample.txt')
        data = cabinets.read(f'{protocol}://{filename}')
        expected = "I am sample text!\nThis file has more than one line.\n" \
                   "Hey look, a panda.\n\nその鶏のサイズを見てください\nNow it's a " \
                   "new paragraph. This line has two sentences.\n🤯🦄\n"
        self.assertEqual(expected, data)

    def test_create_plain_text(self):
        protocol, filename = 'file', 'tmp/sample.txt'
        content = "I am sample text!\nThis file has more than one line.\n" \
                  "Hey look, a panda.\n\nその鶏のサイズを見てください\nNow it's a " \
                  "new paragraph. This line has two sentences.\n🤯🦄\n"
        cabinets.create(f'{protocol}://{filename}', content)
        with open(filename) as fh:
            data = fh.read()
        self.assertEqual(content, data)

    def test_read_plain_text_single_byte_encoding(self):
        protocol = 'file'
        filename = os.path.join(self.fixture_path, 'sample_single_byte.txt')
        data = cabinets.read(f'{protocol}://{filename}', encoding='iso-8859-1')
        expected = "I am sample text!\nThis file has more than one line.\n" \
                   "Hey look, a panda.\n\nNow it's a new paragraph. This line has " \
                   "two sentences.\n"
        self.assertEqual(expected, data)

    def test_create_plain_text_single_byte_encoding(self):
        protocol, filename = 'file', 'tmp/sample_single_byte.txt'
        content = "I am sample text!\nThis file has more than one line.\n" \
                  "Hey look, a panda.\n\nNow it's a new paragraph. This line has " \
                  "two sentences.\n"
        cabinets.create(f'{protocol}://{filename}', content, encoding='iso-8859-1')
        with open(filename) as fh:
            data = fh.read()
        self.assertEqual(content, data)


@mock_s3
class TestTopLevelConfiguration(unittest.TestCase):

    def test_set_configuration_region(self):
        cabinets.set_configuration('s3', region_name='us-west-2')
        self.assertIsNotNone(S3Cabinet.client)
        self.assertEqual(S3Cabinet.client.meta.region_name, 'us-west-2')

    def test_set_configuration_region_bad_protocol(self):
        with self.assertRaises(CabinetError):
            cabinets.set_configuration('s4', region_name='us-west-2')


@mock_s3
class TestS3Cabinet(unittest.TestCase):

    def setUp(self) -> None:
        S3Cabinet.set_configuration(region_name='us-west-2')

    def test_set_configuration_region(self):
        self.assertIsNotNone(S3Cabinet.client)
        self.assertEqual(S3Cabinet.client.meta.region_name, 'us-west-2')

    def test_read_create_s3_cabinet(self):
        client = boto3.client('s3', region_name='us-west-2')
        bucket = 'mock-bucket'
        client.create_bucket(Bucket=bucket)
        filename = f'{bucket}/test.yml'
        data = {'I': {'am': ['nested', 1, 'object', None]}}
        S3Cabinet.create(f'{filename}', data)
        result = S3Cabinet.read(f'{filename}')
        S3Cabinet.delete(f'{filename}')
        self.assertDictEqual(data, result)
        client.delete_bucket(Bucket=bucket)

    def test_read_create(self):
        client = boto3.client('s3', region_name='us-west-2')
        bucket = 'mock-bucket'
        client.create_bucket(Bucket=bucket)
        protocol, filename = 's3', f'{bucket}/test.yml'
        data = {'I': {'am': ['nested', 1, 'object', None]}}
        cabinets.create(f'{protocol}://{filename}', data)
        result = cabinets.read(f'{protocol}://{filename}')
        cabinets.delete(f'{protocol}://{filename}')
        self.assertDictEqual(data, result)
        client.delete_bucket(Bucket=bucket)


class TestURI(unittest.TestCase):

    def test_cabinet_from_uri_missing_protocol_defaults_to_file(self):
        uri = 'path/to/file'
        cabinet, path = cabinets.from_uri(uri)
        self.assertEqual(cabinet, FileCabinet)
        self.assertEqual(path, uri)

    def test_cabinet_from_uri_fails_on_unknown_protocol(self):
        uri = 'foo://path/to/file'
        with self.assertRaises(InvalidURIError):
            cabinets.from_uri(uri)

    def test_cabinet_from_uri_fails_on_empty_path(self):
        uri = 'file://'
        with self.assertRaises(InvalidURIError):
            cabinets.from_uri(uri)


if __name__ == '__main__':
    unittest.main()
