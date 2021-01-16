# Cabinets
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cabinets?style=flat-square)](#cabinets)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/lucasmlofaro/cabinets/Python%20package?style=flat-square)](#cabinets)
[![PyPI](https://img.shields.io/pypi/v/cabinets?style=flat-square)](https://pypi.org/project/cabinets/)

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
    def _load_content(cls, content: bytes) -> Any:
        return deserialize_foo(content)  # custom deserialization logic

    @classmethod
    def _dump_content(cls, data: Any) -> bytes:
        return serialize_foo(data)  # custom serialization logic

```

Then to load a `test.foo` file you can simply use `Cabinet.read`. 

> **NOTE**: In order for the extension to be registered, the class definition must be
> run at least once. Make sure the modules where your custom `Parser` classes are defined
> are imported somewhere before they are used.

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
from cabinets.cabinet.s3 import S3Cabinet

# set the AWS S3 region to us-west-2 and specify an access key
S3Cabinet.set_configuration(region_name='us-west-2', aws_access_key_id=...)

# use specific Cabinet to avoid protocol prefix
S3Cabinet.read('bucket-in-us-west-2/test.json') 
# or use generic Cabinet with protocol prefix
from cabinets import Cabinets
Cabinets.read('s3://bucket-us-west-2/test.json')
```

See the documentation of specific `Cabinet` classes for what configuration parameters are available.
