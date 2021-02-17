import json

from cabinets.parser import register_extensions, Parser


@register_extensions('json')
class JSONParser(Parser):

    @classmethod
    def load_content(cls, content, **kwargs):
        return json.loads(content)

    @classmethod
    def dump_content(cls, data, **kwargs):
        return json.dumps(data)
