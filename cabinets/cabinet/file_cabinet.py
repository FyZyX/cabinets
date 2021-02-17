import os

from cabinets.cabinet import register_protocols, Cabinet


@register_protocols('file')
class FileCabinet(Cabinet):
    @classmethod
    def read_content(cls, path) -> bytes:
        # TODO: Investigate if binary read mode is always okay
        with open(os.path.normpath(path), 'rb') as file:
            return file.read()

    @classmethod
    def create_content(cls, path, content):
        dirs = os.path.dirname(os.path.normpath(path))
        if dirs:
            os.makedirs(dirs, exist_ok=True)
        mode = 'w' if isinstance(content, str) else 'wb'
        with open(os.path.normpath(path), mode) as file:
            file.write(content)

    @classmethod
    def delete_content(cls, path):
        os.remove(os.path.normpath(path))
