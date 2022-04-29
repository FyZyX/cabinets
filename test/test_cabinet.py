import json
import os
import unittest
import pathlib
from types import SimpleNamespace
from unittest.mock import patch

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

    def test_list(self):
        self.assertCountEqual(
            cabinets.list(os.path.join(self.fixture_path, 'example')),
            ['test.json', 'test2.yaml'])
        self.assertCountEqual(
            cabinets.list(os.path.join(self.fixture_path, 'example', 'subdir')),
            ['test3.txt'])

        # make an empty subdirectory
        os.makedirs(os.path.join(self.fixture_path, 'example', 'empty_subdir'))
        self.assertCountEqual(
            cabinets.list(os.path.join(self.fixture_path, 'example', 'empty_subdir')),
            [])


class TestFileCabinetWithPathObjects(fake_filesystem_unittest.TestCase):
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')

    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory(self.fixture_path)

    def test_read_json(self):
        filename = os.path.join(self.fixture_path, 'sample.json')
        path = pathlib.Path(filename)
        data = cabinets.read(path)
        self.assertEqual({'hello': 'world'}, data)

    def test_create_json(self):
        filename = 'tmp/sample.json'
        path = pathlib.Path(filename)
        cabinets.create(path, {'hello': 'world'})
        with open(filename) as fh:
            data = json.load(fh)
        self.assertEqual({'hello': 'world'}, data)

    def test_delete(self):
        filename = 'delete-me.json'
        path = pathlib.Path(filename)
        data = {'hello': 'world'}
        with open(path, 'w') as fh:
            json.dump(data, fh)
        self.assertTrue(path.exists())
        cabinets.delete(path)
        self.assertFalse(path.exists())


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
@patch.dict(os.environ, {'AWS_ACCESS_KEY_ID': 'testing',
                         'AWS_SECRET_ACCESS_KEY': 'testing',
                         'AWS_SECURITY_TOKEN': 'testing',
                         'AWS_SESSION_TOKEN': 'testing', })
class TestS3CabinetNoRegion(unittest.TestCase):

    def setUp(self) -> None:
        self.client = None
        self._bucket = 'mock-bucket'

    def tearDown(self) -> None:
        if self.client:
            response = self.client.list_objects_v2(Bucket=self._bucket)
            for content in response.get('Contents', []):
                key = content.get('Key')
                self.client.delete_object(Bucket=self._bucket, Key=key)
            self.client.delete_bucket(Bucket=self._bucket)

    def test_set_configuration_region(self):
        self.assertIsNotNone(S3Cabinet.client)

    def test_read_create_s3_cabinet(self):
        self.client = boto3.client('s3')
        self.client.create_bucket(Bucket=self._bucket)
        filename = f'{self._bucket}/test.yml'
        data = {'I': {'am': ['nested', 1, 'object', None]}}
        S3Cabinet.create(f'{filename}', data)
        result = S3Cabinet.read(f'{filename}')
        self.assertDictEqual(data, result)

    def test_read_create(self):
        self.client = boto3.client('s3')
        self.client.create_bucket(Bucket=self._bucket)
        protocol, filename = 's3', f'{self._bucket}/test.yml'
        data = {'I': {'am': ['nested', 1, 'object', None]}}
        cabinets.create(f'{protocol}://{filename}', data)
        result = cabinets.read(f'{protocol}://{filename}')
        self.assertDictEqual(data, result)

    def test_read_create_with_different_region(self):
        self.client = boto3.client('s3', 'us-east-2')
        self.client.create_bucket(
            Bucket=self._bucket,
            CreateBucketConfiguration={'LocationConstraint': 'us-east-2'}
        )
        protocol, filename = 's3', f'{self._bucket}/test.yml'
        data = {'I': {'am': ['nested', 1, 'object', None]}}
        cabinets.create(f'{protocol}://{filename}', data)
        result = cabinets.read(f'{protocol}://{filename}')
        self.assertDictEqual(data, result)

    def test_list_bucket_level(self):
        self.client = boto3.client('s3', 'us-east-2')
        self.client.create_bucket(
            Bucket=self._bucket,
            CreateBucketConfiguration={'LocationConstraint': 'us-east-2'}
        )
        files = ['file1.txt', 'file2.yml', 'file3']
        for file in files:
            self.client.put_object(Bucket=self._bucket, Key=file, Body='abcd'.encode())

        listed_files = cabinets.list(f's3://{self._bucket}')
        self.assertCountEqual(listed_files, files)

    def test_list_bucket_level_with_subdir(self):
        self.client = boto3.client('s3', 'us-east-2')
        self.client.create_bucket(
            Bucket=self._bucket,
            CreateBucketConfiguration={'LocationConstraint': 'us-east-2'}
        )
        files = ['file1.txt', 'file2.yml', 'subdir/file3.txt']
        for file in files:
            self.client.put_object(Bucket=self._bucket, Key=file, Body='abcd'.encode())

        listed_files = cabinets.list(f's3://{self._bucket}')
        self.assertCountEqual(listed_files, ['file1.txt', 'file2.yml'])

    def test_list_subdir_level(self):
        self.client = boto3.client('s3', 'us-east-2')
        self.client.create_bucket(
            Bucket=self._bucket,
            CreateBucketConfiguration={'LocationConstraint': 'us-east-2'}
        )
        files = ['file1.txt', 'subdir/file2.txt', 'subdir/file3',
                 'subdir/subdir2/file4']
        for file in files:
            self.client.put_object(Bucket=self._bucket, Key=file, Body='abcd'.encode())

        listed_files = cabinets.list(f's3://{self._bucket}/subdir')
        self.assertCountEqual(listed_files, ['file2.txt', 'file3'])


@mock_s3
@patch.dict(os.environ, {'AWS_ACCESS_KEY_ID': 'testing',
                         'AWS_SECRET_ACCESS_KEY': 'testing',
                         'AWS_SECURITY_TOKEN': 'testing',
                         'AWS_SESSION_TOKEN': 'testing', })
class TestS3CabinetWithRegion(unittest.TestCase):

    def setUp(self) -> None:
        self.client = None
        self._bucket = 'mock-bucket'
        self._region = 'us-west-2'
        S3Cabinet.set_configuration(region_name=self._region)

    def tearDown(self) -> None:
        if self.client:
            self.client.delete_bucket(Bucket=self._bucket)

    def test_set_configuration_region(self):
        self.assertIsNotNone(S3Cabinet.client)
        self.assertEqual(S3Cabinet.client.meta.region_name, self._region)

    def test_read_create_s3_cabinet(self):
        self.client = boto3.client('s3', region_name=self._region)
        self.client.create_bucket(
            Bucket=self._bucket,
            CreateBucketConfiguration={'LocationConstraint': self._region}
        )
        filename = f'{self._bucket}/test.yml'
        data = {'I': {'am': ['nested', 1, 'object', None]}}
        S3Cabinet.create(f'{filename}', data)
        result = S3Cabinet.read(f'{filename}')
        self.assertDictEqual(data, result)

        # clean up file in mocked s3
        S3Cabinet.delete(f'{filename}')

    def test_read_create(self):
        self.client = boto3.client('s3', region_name=self._region)
        self.client.create_bucket(
            Bucket=self._bucket,
            CreateBucketConfiguration={'LocationConstraint': self._region}
        )
        protocol, filename = 's3', f'{self._bucket}/test.yml'
        data = {'I': {'am': ['nested', 1, 'object', None]}}
        cabinets.create(f'{protocol}://{filename}', data)
        result = cabinets.read(f'{protocol}://{filename}')
        self.assertDictEqual(data, result)

        # clean up file in mocked s3
        cabinets.delete(f'{protocol}://{filename}')

    def test_read_create_different_region(self):
        # still works since s3 is global
        self.client = boto3.client('s3', region_name='us-west-1')
        self.client.create_bucket(
            Bucket=self._bucket,
            CreateBucketConfiguration={'LocationConstraint': 'us-west-1'}
        )
        protocol, filename = 's3', f'{self._bucket}/test.yml'
        data = {'I': {'am': ['nested', 1, 'object', None]}}
        cabinets.create(f'{protocol}://{filename}', data)
        result = cabinets.read(f'{protocol}://{filename}')
        self.assertDictEqual(data, result)

        # clean up file in mocked s3
        cabinets.delete(f'{protocol}://{filename}')


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

    def test_cabinet_from_uri_fails_on_multiple_protocol_separators(self):
        uri = 'file://path/to/file://path/to/another/file'
        with self.assertRaises(InvalidURIError):
            cabinets.from_uri(uri)


if __name__ == '__main__':
    unittest.main()
