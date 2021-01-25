from cabinets.parser import register_extensions, Parser


@register_extensions('txt')
class PlainTextParser(Parser):

    @classmethod
    def load_content(cls, content):
        return content.decode(encoding='utf-8')

    @classmethod
    def dump_content(cls, data):
        return bytes(data, encoding='utf-8')
