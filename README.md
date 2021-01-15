# Cabinets

`cabinets` is a Python library that provides a consistent interface for file operations
across multiple storage platforms. File extensions are dynamically detected to allow
automatic serialization and deserialization of Python objects.
`cabinets` [supports](#built-in-protocols-and-parsers) a variety of protocols and file
format parsers natively, and new protocols or parsers can be
easily [registered](#custom-protocols-and-parsers).

## Sample Usage

### Read a file

Set up a test file in your local filesystem:

```python
import json

obj = {'test': 1}

with open('data.json', 'w') as fh:
    json.dump(obj, fh)
```

Read back and parse the file using `cabinets`:

```python
from cabinets import Cabinets

new_obj = Cabinets.read('file://test.json')

assert new_obj == obj
```

That's it! The file is *loaded* and *parsed* in just one line.

### Write a file

`Cabinet` also supports creating files. We can rewrite the first example using
only `cabinets`.

```python
from cabinets import Cabinets

obj = {'test': 1}

Cabinets.create('file://test.json', obj)

new_obj = Cabinets.read('file://test.json')

assert new_obj == obj
```

## Built-in Protocols and Parsers

### Protocols

- Local File System (`file://`)
- S3 (`s3://`)

### Parsers

- YAML (`.yml`, `.yaml`)
- JSON (`.json`)
- Python Pickle (`.pickle`)
- CSV *(beta)* (`.csv`)

## Custom Protocols and Parsers

`cabinets` is designed to allow complete extensibility in adding new protocols and
parsers. Just because your desired storage platform or file format is not listed above,
doesn't mean you can't use it with `cabinets`!

### Adding a Parser

Adding a new parser is as simple as subclassing `cabinets.parser.Parser` and registers
associated file extensions.

```python
from typing import Any
from cabinets.parser import Parser, register_extensions


@register_extensions('foo', 'bar')
class FooParser(Parser):

    @classmethod
    def load_content(cls, content: bytes):
        return deserialize_foo(content)  # custom deserialization logic

    @classmethod
    def dump_content(cls, data: Any):
        return serialize_foo(data)  # custom serialization logic

```

Then to load a `test.foo` file you can simply use `Cabinet.read`

```python
from cabinets import Cabinets

# .foo file in local filesystem
local_foo_data = Cabinets.read('file://test.foo')

# .foo file in S3
s3_foo_data = Cabinets.read('s3://test.foo')
```


## Protocol Configuration

Some storage platform protocols may require some configuration parameters to be set before they can be used.
Each `Cabinet` subclass can expose a `set_configuration(**config)` classmethod to take 
care of any required initial setup.

```python
from cabinets.cabinet import Cabinets, S3Cabinet

S3Cabinet.set_configuration(region_name='us-west-2')

S3Cabinet.read('bucket-us-west-2/test.json')
# or
Cabinets.read('s3://bucket-us-west-2/test.json')

```

