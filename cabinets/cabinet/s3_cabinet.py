import boto3

from cabinets.cabinet import register_protocols, Cabinet
from cabinets.logger import info, error


@register_protocols('s3')
class S3Cabinet(Cabinet):
    client = None

    @classmethod
    def set_configuration(cls, region_name='us-east-1', aws_access_key_id=None,
                          aws_secret_access_key=None, aws_session_token=None):
        cls.client = boto3.client('s3', region_name=region_name,
                                  aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key,
                                  aws_session_token=aws_session_token)

    @classmethod
    def read_content(cls, path, **kwargs) -> bytes:
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
    def create_content(cls, path, content, **kwargs):
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
    def delete_content(cls, path, **kwargs):
        bucket, *key = path.split('/')
        key = '/'.join(key)
        info(f"Uploading {key} to {bucket}")
        try:
            cls.client.delete_object(Bucket=bucket, Key=key)
            return True
        except Exception as ex:
            error(f"Cannot delete {path} from S3 Bucket '{bucket}': {ex}")
            return False
