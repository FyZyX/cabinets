import os
from abc import ABC, abstractmethod

from cabinets.logger import error, info
from cabinets.parser import Parser

_SUPPORTED_PROTOCOLS = {}


def register_protocols(*protocols):
    def decorate_cabinet(cabinet: Cabinet):
        for protocol in protocols:
            _SUPPORTED_PROTOCOLS[protocol] = cabinet
        return cabinet

    return decorate_cabinet


class Cabinet(ABC):

    @classmethod
    def from_uri(cls, uri):
        protocol, path = uri.split('://')
        cabinet = _SUPPORTED_PROTOCOLS.get(protocol)
        return cabinet, path

    @classmethod
    def read(cls, uri, raw=False):
        cabinet, path = cls.from_uri(uri)
        if raw:
            return cabinet._read_content(path)
        else:
            return Parser.load(path, cabinet._read_content(path))

    @classmethod
    def create(cls, uri, content, raw=False):
        cabinet, path = cls.from_uri(uri)
        if raw:
            return cabinet._create_content(path, content)
        else:
            return cabinet._create_content(path, Parser.dump(path, content))

    @classmethod
    def delete(cls, uri):
        cabinet, path = cls.from_uri(uri)
        cabinet._delete_content(path)

    @classmethod
    @abstractmethod
    def _read_content(cls, path):
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
class S3Cabinet(Cabinet):
    # client = boto3.client('s3', region_name=NotImplemented)
    client = None

    @classmethod
    def _read_content(cls, path):
        bucket, *key = path.split('/')
        key = '/'.join(key)
        info(f'Downloading {key} from Bucket {bucket}')
        try:
            resp = cls.client.get_object(Bucket=bucket, Key=key)
            return resp._read_content('Body').read()
        except Exception as ex:
            error(f"Cannot download {path} from S3 Bucket '{bucket}': {ex}")
            return None

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


@register_protocols('file')
class FileCabinet(Cabinet):
    @classmethod
    def _read_content(cls, path):
        # TODO: Investigate if binary read mode is always okay
        with open(os.path.normpath(path), 'rb') as file:
            return file.read()

    @classmethod
    def _create_content(cls, path, content):
        if dirs := os.path.dirname(os.path.normpath(path)):
            os.makedirs(dirs, exist_ok=True)
        mode = 'w' if isinstance(content, str) else 'wb'
        with open(os.path.normpath(path), mode) as file:
            file.write(content)

    @classmethod
    def _delete_content(cls, path):
        os.remove(os.path.normpath(path))
