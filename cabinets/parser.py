import csv
import json
import pickle
from typing import Any
from abc import ABC, abstractmethod
from io import StringIO

import yaml

_SUPPORTED_FILE_TYPES = {}


def register_extensions(*file_types):
    def decorate_parser(parser: Parser):
        for file_type in file_types:
            _SUPPORTED_FILE_TYPES[file_type] = parser
        return parser

    return decorate_parser


class Parser(ABC):

    @classmethod
    def load(cls, path, content: bytes):
        filepath, ext = path.split('.')
        return _SUPPORTED_FILE_TYPES[ext].load_content(content)

    @classmethod
    @abstractmethod
    def load_content(cls, content: bytes):
        pass

    @classmethod
    def dump(cls, path, data: Any):
        filepath, ext = path.split('.')
        return _SUPPORTED_FILE_TYPES[ext].dump_content(data)

    @classmethod
    @abstractmethod
    def dump_content(cls, data: Any):
        pass


@register_extensions('pickle')
class PickleParser(Parser):

    @classmethod
    def load_content(cls, content):
        return pickle.loads(content)

    @classmethod
    def dump_content(cls, data):
        return pickle.dumps(data)


@register_extensions('json')
class JSONParser(Parser):

    @classmethod
    def load_content(cls, content):
        return json.loads(content)

    @classmethod
    def dump_content(cls, data):
        return json.dumps(data)


@register_extensions('yaml', 'yml')
class YAMLParser(Parser):

    @classmethod
    def load_content(cls, content):
        return yaml.safe_load(content)

    @classmethod
    def dump_content(cls, data):
        return yaml.safe_dump(data)


@register_extensions('csv')
class CSVParser(Parser):

    @classmethod
    def load_content(cls, content):
        return list(csv.reader(content.decode('utf-8').splitlines()))

    @classmethod
    def dump_content(cls, data):
        csv_buffer = StringIO()
        if type(data[0]) == dict:
            # TODO: Grabbing the field names the first list item is kinda wonky
            fields = list(data[0].keys())
            writer = csv.DictWriter(csv_buffer, fieldnames=fields, lineterminator='\n')
            writer.writeheader()
            writer.writerows(data)
            return csv_buffer.getvalue()
        else:
            csv_buffer = StringIO()
            csv.writer(csv_buffer, lineterminator='\n').writerows(data)
            return csv_buffer.getvalue()
