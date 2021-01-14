import os
from abc import ABC, abstractmethod

from cabinets.logger import error, info
from cabinets.parser import Parser


class Cabinet(ABC):
    @classmethod
    def _get_subclasses(cls):
        subs: {str: Cabinet} = {}
        for subcls in cls.__subclasses__():
            protocol = subcls.__name__.removesuffix('Cabinet').lower()
            subs[protocol] = subcls
            subs.update(subcls._get_subclasses())
        return subs

    @classmethod
    def from_uri(cls, uri):
        protocol, path = uri.split('://')
        cabinets = cls._get_subclasses()
        cabinet = cabinets.get(protocol)
        return cabinet, path

    @classmethod
    def read(cls, uri, raw=False):
        cabinet, path = cls.from_uri(uri)
        if raw:
            return cabinet.get_content(path)
        else:
            return Parser.load(path, cabinet.get_content(path))

    @classmethod
    def write(cls, uri, content, raw=False):
        cabinet, path = cls.from_uri(uri)
        if raw:
            return cabinet.put_content(path, content)
        else:
            return cabinet.put_content(path, Parser.dump(path, content))

    @classmethod
    @abstractmethod
    def get_content(cls, path):
        pass

    @classmethod
    @abstractmethod
    def put_content(cls, path, content):
        pass


class S3Cabinet(Cabinet):
    # client = boto3.client('s3', region_name=NotImplemented)
    client = None

    @classmethod
    def get_content(cls, path):
        bucket, *key = path.split('/')
        key = '/'.join(key)
        info(f'Downloading {key} from Bucket {bucket}')
        try:
            resp = cls.client.get_object(Bucket=bucket, Key=key)
            return resp.get_content('Body').read()
        except Exception as ex:
            error(f"Cannot download {path} from S3 Bucket '{bucket}': {ex}")
            return None

    @classmethod
    def put_content(cls, path, content):
        bucket, *key = path.split('/')
        key = '/'.join(key)
        info(f"Uploading {key} to {bucket}")
        try:
            cls.client.put_object(Bucket=bucket, Key=key, Body=content)
            return True
        except Exception as ex:
            error(f"Cannot upload {path} to S3 Bucket '{bucket}': {ex}")
            return False


class FileCabinet(Cabinet):
    @classmethod
    def get_content(cls, path):
        with open(os.path.normpath(path)) as file:
            return file.read()

    @classmethod
    def put_content(cls, path, content):
        os.makedirs(os.path.dirname(os.path.normpath(path)), exist_ok=True)
        with open(os.path.normpath(path), 'w') as file:
            file.write(content)
