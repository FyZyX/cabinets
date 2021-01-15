import os
from abc import ABC, abstractmethod

import boto3

from cabinets.logger import error, info
from cabinets.parser import Parser

_SUPPORTED_PROTOCOLS = {}


def register_protocols(*protocols):
    def decorate_cabinet(cabinet: CabinetBase):
        for protocol in protocols:
            _SUPPORTED_PROTOCOLS[protocol] = cabinet
        return cabinet

    return decorate_cabinet


class Cabinet:

    @classmethod
    def from_uri(cls, uri):
        protocol, path = uri.split('://')
        cabinet = _SUPPORTED_PROTOCOLS.get(protocol)
        return cabinet, path

    @classmethod
    def read(cls, uri, raw=False) -> bytes:
        cabinet, path = cls.from_uri(uri)
        return cabinet.read(path, raw=raw)

    @classmethod
    def create(cls, uri, content, raw=False):
        cabinet, path = cls.from_uri(uri)
        return cabinet.read(path, content, raw=raw)

    @classmethod
    def delete(cls, uri):
        cabinet, path = cls.from_uri(uri)
        return cabinet.delete(path)


class CabinetBase(ABC):

    @classmethod
    @abstractmethod
    def set_configuration(cls, **kwargs):
        pass

    @classmethod
    def read(cls, path, raw=False) -> bytes:
        if raw:
            return cls._read_content(path)
        else:
            return Parser.load(path, cls._read_content(path))

    @classmethod
    def create(cls, path, content, raw=False):
        if raw:
            return cls._create_content(path, content)
        else:
            return cls._create_content(path, Parser.dump(path, content))

    @classmethod
    def delete(cls, path):
        cls._delete_content(path)

    @classmethod
    @abstractmethod
    def _read_content(cls, path) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def _create_content(cls, path, content):
        pass

    @classmethod
    @abstractmethod
    def _delete_content(cls, path):
        pass


@register_protocols('s3')
class S3Cabinet(CabinetBase):
    client = None

    @classmethod
    def set_configuration(cls, region_name='us-east-1', aws_access_key_id=None,
                          aws_secret_access_key=None, aws_session_token=None):
        cls.client = boto3.client('s3', region_name=region_name,
                                  aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key,
                                  aws_session_token=aws_session_token)

    @classmethod
    def _read_content(cls, path) -> bytes:
        bucket, *key = path.split('/')
        if not key:
            raise ValueError('S3 path needs bucket')
        key = '/'.join(key)
        info(f'Downloading {key} from Bucket {bucket}')
        try:
            resp = cls.client.get_object(Bucket=bucket, Key=key)
            return resp.get('Body').read()
        except Exception as ex:
            error(f"Cannot download {path} from S3 Bucket '{bucket}': {ex}")
            raise ex

    @classmethod
    def _create_content(cls, path, content):
        bucket, *key = path.split('/')
        key = '/'.join(key)
        info(f"Uploading {key} to {bucket}")
        try:
            cls.client.put_object(Bucket=bucket, Key=key, Body=content)
            return True
        except Exception as ex:
            error(f"Cannot upload {path} to S3 Bucket '{bucket}': {ex}")
            return False

    @classmethod
    def _delete_content(cls, path):
        bucket, *key = path.split('/')
        key = '/'.join(key)
        info(f"Uploading {key} to {bucket}")
        try:
            cls.client.delete_object(Bucket=bucket, Key=key)
            return True
        except Exception as ex:
            error(f"Cannot delete {path} from S3 Bucket '{bucket}': {ex}")
            return False


@register_protocols('file')
class FileCabinet(CabinetBase):
    @classmethod
    def _read_content(cls, path) -> bytes:
        # TODO: Investigate if binary read mode is always okay
        with open(os.path.normpath(path), 'rb') as file:
            return file.read()

    @classmethod
    def _create_content(cls, path, content):
        dirs = os.path.dirname(os.path.normpath(path))
        if dirs:
            os.makedirs(dirs, exist_ok=True)
        mode = 'w' if isinstance(content, str) else 'wb'
        with open(os.path.normpath(path), mode) as file:
            file.write(content)

    @classmethod
    def _delete_content(cls, path):
        os.remove(os.path.normpath(path))
