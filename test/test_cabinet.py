import json
import os
import unittest
from types import SimpleNamespace

import boto3
from moto import mock_s3
from pyfakefs import fake_filesystem_unittest

import cabinets
from cabinets import InvalidURIError
from cabinets.cabinet.file import FileCabinet
from cabinets.cabinet.s3 import S3Cabinet


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
