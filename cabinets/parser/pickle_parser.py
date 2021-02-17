import pickle

from cabinets.parser import register_extensions, Parser


@register_extensions('pickle')
class PickleParser(Parser):

    @classmethod
    def load_content(cls, content, **kwargs):
        return pickle.loads(content)

    @classmethod
    def dump_content(cls, data, **kwargs):
        return pickle.dumps(data)
