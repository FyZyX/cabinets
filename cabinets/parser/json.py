import json

from cabinets.parser import register_extensions, Parser


@register_extensions('json')
class JSONParser(Parser):

    @classmethod
    def load_content(cls, content):
        return json.loads(content)

    @classmethod
    def dump_content(cls, data):
        return json.dumps(data)
