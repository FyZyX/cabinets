import csv
from io import StringIO

from cabinets.parser import register_extensions, Parser


@register_extensions('csv')
class CSVParser(Parser):

    @classmethod
    def load_content(cls, content, **kwargs):
        return list(csv.reader(content.decode('utf-8').splitlines()))

    @classmethod
    def dump_content(cls, data, **kwargs):
        csv_buffer = StringIO()
        if type(data[0]) == dict:
            # TODO: Grabbing the field names the first list item is kinda wonky
            fields = list(data[0].keys())
            writer = csv.DictWriter(csv_buffer, fieldnames=fields, lineterminator='\n')
            writer.writeheader()
            writer.writerows(data)
            return csv_buffer.getvalue()
        else:
            csv_buffer = StringIO()
            csv.writer(csv_buffer, lineterminator='\n').writerows(data)
            return csv_buffer.getvalue()
