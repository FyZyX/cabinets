import csv
import json
from io import StringIO

import yaml


class Parser:

    @staticmethod
    def load_csv(content):
        return list(csv.reader(content.splitlines()))

    @staticmethod
    def load_json(content):
        return json.loads(content)

    @staticmethod
    def load_yaml(content):
        return yaml.safe_load(content)

    @classmethod
    def load(cls, path, content):
        filepath, ext = path.split('.')
        return {
            'yml': cls.load_yaml,
            'yaml': cls.load_yaml,
            'json': cls.load_json,
            'csv': cls.load_csv,
        }[ext](content)

    @staticmethod
    def dump_csv(content):
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

    @staticmethod
    def dump_json(content):
        return json.dumps(content)

    @staticmethod
    def dump_yaml(content):
        return yaml.dump(content)

    @classmethod
    def dump(cls, path, content):
        filepath, ext = path.split('.')
        return {
            'yml': cls.dump_yaml,
            'yaml': cls.dump_yaml,
            'json': cls.dump_json,
            'csv': cls.dump_csv,
        }[ext](content)
