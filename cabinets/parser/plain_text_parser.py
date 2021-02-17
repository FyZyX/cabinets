from cabinets.parser import register_extensions, Parser


@register_extensions('txt')
class PlainTextParser(Parser):

    @classmethod
    def load_content(cls, content, encoding='utf-8', **kwargs):
        return content.decode(encoding=encoding)

    @classmethod
    def dump_content(cls, data, encoding='utf-8', **kwargs):
        return bytes(data, encoding=encoding)
