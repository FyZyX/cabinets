import csv
import json
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
    def load(cls, path, content):
        filepath, ext = path.split('.')
        return _SUPPORTED_FILE_TYPES[ext].load_content(content)

    @classmethod
    @abstractmethod
    def load_content(cls, content):
        pass

    @classmethod
    def dump(cls, path, content):
        filepath, ext = path.split('.')
        return _SUPPORTED_FILE_TYPES[ext].dump_content(content)

    @classmethod
    @abstractmethod
    def dump_content(cls, content):
        pass


@register_extensions('json')
class JSONParser(Parser):

    @classmethod
    @abstractmethod
    def load_content(cls, content):
        return json.loads(content)

    @classmethod
    @abstractmethod
    def dump_content(cls, content):
        return json.dumps(content)


@register_extensions('yaml', 'yml')
class YAMLParser(Parser):

    @classmethod
    @abstractmethod
    def load_content(cls, content):
        return yaml.safe_load(content)

    @classmethod
    @abstractmethod
    def dump_content(cls, content):
        return yaml.safe_dump(content)


@register_extensions('csv')
class CSVParser(Parser):

    @classmethod
    @abstractmethod
    def load_content(cls, content):
        return list(csv.reader(content.splitlines()))

    @classmethod
    @abstractmethod
    def dump_content(cls, content):
        csv_buffer = StringIO()
        if type(content[0]) == dict:
            # TODO: Grabbing the field names the first list item is kinda wonky
            fields = list(content[0].keys())
            writer = csv.DictWriter(csv_buffer, fieldnames=fields, lineterminator='\n')
            writer.writeheader()
            writer.writerows(content)
            return csv_buffer.getvalue()
        else:
            csv_buffer = StringIO()
            csv.writer(csv_buffer, lineterminator='\n').writerows(content)
            return csv_buffer.getvalue()
