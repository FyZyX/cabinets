from cabinets import Cabinet, register_protocols


@register_protocols('mock')
class MockCabinet(Cabinet):

    @classmethod
    def set_configuration(cls, **kwargs):
        return NotImplemented

    @classmethod
    def read_content(cls, path) -> bytes:
        return NotImplemented

    @classmethod
    def create_content(cls, path, content):
        return NotImplemented

    @classmethod
    def delete_content(cls, path):
        return NotImplemented
