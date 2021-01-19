from typing import Any

from cabinets import Parser, register_extensions


@register_extensions('mock')
class MockParser(Parser):
    @classmethod
    def load_content(cls, content: bytes):
        return NotImplemented

    @classmethod
    def dump_content(cls, data: Any):
        return NotImplemented
