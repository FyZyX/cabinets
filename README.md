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

## Table of contents

- [Sample Usage](#sample-usage)
    - [Read a file](#read-a-file)
    - [Write a file](#write-a-file)
    - [List files in a directory](#list-files-in-a-directory)
    - [Reading and Writing with Other Protocols](#reading-and-writing-with-other-protocols)
- [Built-in Protocols and Parsers](#built-in-protocols-and-parsers)
    - [Protocols](#protocols)
    - [Parsers](#parsers)
- [Protocol Configuration](#protocol-configuration)
- [Custom Protocols and Parsers](#custom-protocols-and-parsers)
    - [Adding Cabinets](#adding-cabinets)
    - [Adding Parsers](#adding-parsers)
    - [Loading Plugins](#loading-plugins)
- [Contributing](#contributing)

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

new_obj = cabinets.read('test.json')
```

That's it! The file is *loaded* and *parsed* in just one line.

### Write a file

`cabinets` also supports creating files. We can rewrite the first example using
only `cabinets`.

```python
import cabinets

obj = {'test': 1}
cabinets.create('test.json', obj)

new_obj = cabinets.read('test.json')

assert new_obj == obj
```

### List files in a directory

In some situations, you may need to know what files are in a directory before doing 
any operations. `cabinets` also provides an `ls` function to assist with this.

```python
import cabinets

obj = {'test': 1}
cabinets.create('example/test.json', obj)
cabinets.create('example/test2.yaml', obj)
cabinets.create('example/subdir/test3.txt', "test")

assert cabinets.list('example/') == ['test.json', 'test2.yaml']
assert cabinets.list('example/subdir/') == ['test3.txt']

```

> **Important:** For simplicity, `cabinets` restricts the output of `ls` to **only file types**. 
> Subdirectories are excluded, and must be queried separately. 
> Future versions may include a flag in `ls` for returning subdirectories as well. 


### Reading and Writing with Other Protocols

Using `cabinets` allows you to interact with multiple file storage protocols depending
on the URI you specify. In the previous examples, we used
`read()` and `write()` to operate within our local file system; that's
because `cabinets` assumes we're using the `file://` protocol by default. Luckily,
accessing other storage systems is just as easy!

For example, operating on a file on AWS S3 is done exactly the same way:

```python
import cabinets

# Read JSON file from your filesystem
local_obj = cabinets.read('file://test.json')

# Write that object to a file in AWS S3
cabinets.create('s3://test.json', local_obj)

# Read back the same file from AWS S3
remote_obj = cabinets.read('s3://test.json')

assert local_obj == remote_obj
```

The above example will read a file from the local filesystem and create a new file
containing the same data, at the same path in S3.

By prefixing the *path* with `{protocol}://` we specify how and where `cabinets` should
look for a file. Using `file://` (default if none specified) tells `cabinets` to use *
path* on the local filesystem. Using `s3://` on the other hand instructs `cabinets` to
perform operations against that *path* in AWS S3.

> NOTE: The `S3Cabinet` may require initial configuration for the `s3` protocol to
> function properly. See [Protocol Configuration](#protocol-configuration) for details.

See all the natively supported protocols [below](#protocols).

## Built-in Protocols and Parsers

### Protocols

- Local File System (`file://`)
- S3 (`s3://`)

### Parsers

- YAML (`.yml`, `.yaml`)
- JSON (`.json`)
- Python Pickle (`.pickle`)
- CSV *(beta)* (`.csv`)
- TXT (`.txt`)

```python
import cabinets

# .foo file in local filesystem
local_foo_data = cabinets.read('file://test.foo')

# .foo file in S3
s3_foo_data = cabinets.read('s3://test.foo')
```

## Protocol Configuration

Some storage platform protocols may require additional configuration parameters to be
set before they can be used. Each `Cabinet` subclass can expose
a `set_configuration(**config)` class method to take care of any required initial setup.

```python
from cabinets.cabinet.s3_cabinet import S3Cabinet

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

Additionally, there is a top-level `set_configuration()` function so that importing
specific `Cabinet` subclasses is not required. Simply pass the desired protocol as the
first argument.

```python
import cabinets

# *OPTIONAL*: set the AWS S3 region to us-west-2 and specify an access key
cabinets.set_configuration('s3', region_name='us-west-2', aws_access_key_id=...)

# use generic Cabinet with protocol prefix
cabinets.read('s3://bucket-us-west-2/test.json')
```

## Custom Protocols and Parsers

`cabinets` is designed to allow complete extensibility in adding new protocols and
parsers. Just because your desired storage platform or file format is not listed above,
doesn't mean you can't use it with `cabinets`!

### Adding Cabinets

New protocol connections can be added by subclassing abstract base class `Cabinet`, and
registering the class to one or more protocol identifiers:

```python
from cabinets import Cabinet, register_protocols


@register_protocols('foo')
class FooCabinet(Cabinet):

    @classmethod
    def set_configuration(cls, **kwargs):
        # Set up any necessary configuration parameters for "foo" protocol
        ...

    @classmethod
    def read_content(cls, path: str) -> bytes:
        # Custom logic for reading bytes from a path using "foo" protocol
        ...

    @classmethod
    def create_content(cls, path: str, content: bytes):
        # Custom logic for writing bytes to a path  using "foo" protocol
        ...

    @classmethod
    def delete_content(cls, path):
        # Custom logic for deleting the object at a path  using "foo" protocol
        ...

```

Here we define a `FooCabinet`, and register it to the protocol identifier `foo`. Once
this class is loaded, any `cabinets` function calls using the `foo://` prefix will be
processed with this class. This means if we called:

```python
import cabinets
from ... import FooCabinet  # ensure FooCabinet is loaded

cabinets.read('foo://example.json')
```

The first call that occurs will be `FooCabinet.read_content('foo.json)`, and that result
is then parsed by the `JSONParser` before being returned.

> **NOTE**: In order for the protocols to be registered, the class definition must be
> run at least once. Make sure the modules where your custom `Cabinet` classes are defined
> are imported somewhere before they are used, OR use the built in [Plugin](#plugins) system.

### Adding Parsers

`cabinets` also supports custom extension parsing in the exact same way:

```python
from cabinets.parser import Parser, register_extensions


@register_extensions('bar')
class BarParser(Parser):
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
BarParser.load_content(FooCabinet.read_content('foo.bar'))
```

and should return a Python object from your `Foo` cabinet, using your `Bar` parser!

### Loading Plugins

As mentioned in the example above, your custom `Cabinet` and `Parser` classes must be
executed in order to be added to the internal cache `cabinets` uses for protocol and
extension lookup. If your custom classes are imported before any `cabinets` functions
are use then, this won't be an issue. However, in many use cases there is no reason to
import those classes aside from usage with `cabinets` functions. Instead of requiring
each class to be imported manually at the start of your program,
`cabinets` can search a specified path for new `Cabinet` and `Parser` classes, and load
them automatically.

Specifying the `PLUGIN_PATH` environment variable will cause `cabinets` to search for
subdirectories called `cabinet` and `parser` in that path. Modules residing within those
directories will be searched for `Cabinet` and `Parser` subclasses respectively.

```
└─ PLUGIN_PATH
    |
    └───cabinet
    │   │   foo_cabinet.py
    └───parser
    │   │   bar_parser.py
    │   │   baz_parser.py
```

If the above `FooCabinet` and `BarParser` classes are placed in `foo_cabinet.py`
and `bar_parser.py`, they will be loaded and registered to their specified cache without
needing to be referenced anywhere else in the program.

## Contributing

This package is open source (see [LICENSE](LICENSE)), so please feel free
to [contribute](https://opensource.guide/how-to-contribute/)
by submitting a pull request, creating an issue, or contacting the authors directly.

### Authors and Contributors

- Lucas Lofaro *(Co-Author)*: [lucasmlofaro@gmail.com](mailto:lucasmlofaro@gmail.com)
- Sam Hollenbach *(
  Co-Author)*: [samhollenbach@gmail.com](mailto:samhollenbach@gmail.com) 
