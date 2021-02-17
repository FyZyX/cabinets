import yaml

from cabinets.parser import register_extensions, Parser


@register_extensions('yaml', 'yml')
class YAMLParser(Parser):

    @classmethod
    def load_content(cls, content):
        return yaml.safe_load(content)

    @classmethod
    def dump_content(cls, data):
        return yaml.safe_dump(data)
