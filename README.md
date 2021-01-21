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
import cabinets

new_obj = cabinets.read('file://test.json')
```

That's it! The file is *loaded* and *parsed* in just one line.

### Write a file

`cabinets` also supports creating files. We can rewrite the first example using
only `cabinets`.

```python
import cabinets

obj = {'test': 1}
cabinets.create('file://test.json', obj)

new_obj = cabinets.read('file://test.json')

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
import cabinets

# .foo file in local filesystem
local_foo_data = cabinets.read('file://test.foo')

# .foo file in S3
s3_foo_data = cabinets.read('s3://test.foo')
```

## Protocol Configuration

Some storage platform protocols may require some configuration parameters to be set
before they can be used. Each `Cabinet` subclass can expose
a `set_configuration(**config)` classmethod to take care of any required initial setup.

```python
from cabinets.cabinet.s3 import S3Cabinet

# set the AWS S3 region to us-west-2 and specify an access key
S3Cabinet.set_configuration(region_name='us-west-2', aws_access_key_id=...)

# use specific Cabinet to avoid protocol prefix
S3Cabinet.read('bucket-in-us-west-2/test.json')
# or use generic Cabinet with protocol prefix
import cabinets

cabinets.read('s3://bucket-us-west-2/test.json')
```

See the documentation of specific `Cabinet` classes for what configuration parameters
are available.

## Plugins

`cabinets` supports the ability to register custom `Cabinet` and `Parser` classes on any
protocol prefixes or file extensions.

### Adding Cabinets

New protocol connection can be added by subclassing abstract base class `Cabinet`, and
registering the class to one or more protocol identifiers:

```python
from cabinets import Cabinet, register_protocols


@register_protocols('Foo')
class FooCabinet(Cabinet):

    @classmethod
    def set_configuration(cls, **kwargs):
        # Set up any necessary configuration parameters for "foo" protocol
        ...

    @classmethod
    def _read_content(cls, path: str) -> bytes:
        # Custom logic for reading bytes from a path using "foo" protocol
        ...

    @classmethod
    def _create_content(cls, path: str, content: bytes):
        # Custom logic for writing bytes to a path  using "foo" protocol
        ...

    @classmethod
    def _delete_content(cls, path):
        # Custom logic for deleting the object at a path  using "foo" protocol
        ...

```

Here we begin to define a new `Cabinet`, and register it to the protocol
identifier `example`. Once this class is loaded, any `cabinets` function calls using
the `foo://` prefix will be processed with this class. This means if we called:

```python
from ... import FooCabinet  # ensure FooCabinet is loaded

cabinets.read('foo://example.json')
```

The first call that occurs will be `FooCabinet._read_content('foo.json)`, and that
result is then parsed by the `JSONParser` before being returned.

### Adding Parsers

`cabinets` also supports custom extension parsing in the exact same way:

```python
from cabinets.parser import Parser, register_extensions


@register_extensions('bar')
class MockParser(Parser):
    @classmethod
    def load_content(cls, content: bytes):
        # Parse bytes from "bar" file format into a Python object
        ...

    @classmethod
    def dump_content(cls, data: Any):
        # Dump a Python object into bytes in the "bar" file format
        ...
```

Now if we redo our above example using the `.bar` extension:

```python
from ... import FooCabinet, BarParser  # ensure FooCabinet and BarParser are loaded

cabinets.read('foo://example.bar')
```

This statement is roughly equivalent to:

```python
BarParser.load_content(FooCabinet._read_content('foo.bar'))
```

and should return a Python object from your `Foo` protocol, using your `Bar` parser!

### Loading Plugins

As mentioned in the example above, your custom `Cabinet` and `Parser` classes must be
executed in order to be added to the internal cache `cabinets` uses for extension and
protocol lookup. If your custom classes are imported before any `cabinets` functions are
used then this won't be an issue. However, in many use cases there is no reason to
import those classes aside from usage with `cabinets` functions. Instead of requiring
each class to be imported manually at the start of your program,
`cabinets` can search a specified path for new `Cabinet` and `Parser` classes, and load
them automatically.

If the environment variable `PLUGIN_PATH` is specified, `cabinets`
will search that path for subdirectories called `cabinet` and `parser`. Modules residing
within those directories will be searched for `Cabinet` and `Parser` subclasses,
respectively.

```
└─ PLUGIN_PATH
    |
    └───cabinet
    │   │   custom_cabinet.py   
    └───parser
    │   │   custom_parser_1.py
    │   │   custom_parser_2.py
```

If the above `FooCabinet` and `BarParser` classes are placed in
`custom_cabinet.py` and `custom_parser_1.py` (or `custom_parser_2.py`) they will be
loaded and registered to their specified protocols/extensions without needing to be
referenced anywhere else in the program.

## Contributing

This package is open source (see [LICENSE](LICENSE)), so please feel free
to [contribute](https://opensource.guide/how-to-contribute/)
by submitting a pull request, or contacting the authors directly.

### Authors and Contributors:

* Lucas Lofaro *(Co-Author)*: [lucasmlofaro@gmail.com](mailto:lucasmlofaro@gmail.com)
* Sam Hollenbach *(
  Co-Author)*: [samhollenbach@gmail.com](mailto:samhollenbach@gmail.com) 