import json
import os
import unittest
from types import SimpleNamespace

import boto3

from cabinets import Cabinets
from cabinets.protocols.s3 import S3Cabinet
from moto import mock_s3
from pyfakefs import fake_filesystem_unittest


class TestFileSystemCabinet(fake_filesystem_unittest.TestCase):
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')

    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory(self.fixture_path)

    def test_read_json(self):
        protocol = 'file'
        filename = os.path.join(self.fixture_path, 'sample.json')
        data = Cabinets.read(f'{protocol}://{filename}')
        self.assertEqual({'hello': 'world'}, data)

    def test_create_json(self):
        protocol, filename = 'file', 'tmp/sample.json'
        Cabinets.create(f'{protocol}://{filename}', {'hello': 'world'})
        with open(filename) as fh:
            data = json.load(fh)
        self.assertEqual({'hello': 'world'}, data)

    def test_delete(self):
        protocol, filename = 'file', 'delete-me.json'
        data = {'hello': 'world'}
        with open(filename, 'w') as fh:
            json.dump(data, fh)
        self.assertTrue(os.path.isfile(filename))
        Cabinets.delete(f'{protocol}://{filename}')
        self.assertFalse(os.path.isfile(filename))

    def test_read_create_json(self):
        protocol, filename = 'file', 'test.json'
        data = {'I': {'am': ['nested', 1, 'object', None]}}
        Cabinets.create(f'{protocol}://{filename}', data)
        Cabinets.create(f'{protocol}://{filename}', data)
        result = Cabinets.read(f'{protocol}://{filename}')
        self.assertDictEqual(data, result)

    def test_read_create_yaml(self):
        protocol, filename = 'file', 'test.yml'
        data = {'I': {'am': ['nested', 1, 'object', None]}}
        Cabinets.create(f'{protocol}://{filename}', data)
        result = Cabinets.read(f'{protocol}://{filename}')
        self.assertDictEqual(data, result)

    def test_read_create_pickle(self):
        protocol, filename = 'file', 'test.pickle'
        data = {'I': {'am': ['nested', 1 + 2j, 'object', None],
                      'purple': SimpleNamespace(egg=True, fish=42)}}
        Cabinets.create(f'{protocol}://{filename}', data)
        result = Cabinets.read(f'{protocol}://{filename}')
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
        Cabinets.create(f'{protocol}://{filename}', data)
        result = Cabinets.read(f'{protocol}://{filename}')
        Cabinets.delete(f'{protocol}://{filename}')
        self.assertDictEqual(data, result)
        client.delete_bucket(Bucket=bucket)


if __name__ == '__main__':
    unittest.main()
