# Plugin Loader Writing Guide

Loader plugins allow to load a layout description file written in a given
language and generate a Python dict out of it to be parsed later on.

Since layouts are validated using the Python library
[jsonschema](https://python-jsonschema.readthedocs.io/en/stable/), taking a JSON
schema and the Python dictionary to be validated, a custom loader may use any
data serialization language as long as the data can be represented as a Python
dict. Good candidates for alternative languages to YAML can be JSON or TOML.


## How to write a loader

Layoutgen provides the abstract base class
[Loader](../src/layoutgen/abc/loader.py) that one must derive from to create a
specific loader.


### Loader abstract base class

The `Loader` base class has mainly two methods:

```python
Loader.__init__(name: str, extensions: list[str], priority: int = 0)
```

Initialize some general properties available for all loaders:
  * The `name` is used to identify the loader (eg. for logging).
  * The `extensions` list includes all file extensions that should be handled
    by this loader.
  * The `priority` indicates the priority of this plugin against the others. If
    two loaders register for the same file type, only the one with the higher
    priority will handle it. Defaults to 0 and can be negative.

```python
Loader.load(self, layout_file: pathlib.Path) -> dict
```

Abstract method loading the file at path `layout_path` and returning a dict with
the corresponding data.


### Example

Supposed you want to write a JSON layout loader. It will be able to load files
with the extensions `.json` (classic json files) and `.jsonc` (json variant with
comments), then proceed as follow:

1. First, import the `layoutgen` module and the `json` standard module:
```python
import json
import layoutgen
```

2. Create you loader class deriving from `layoutgen.Loader` base class:
```python
class LoaderJson(layoutgen.Loader):
```

3. Define the `__init__` method calling `Loader.__init__`:
```python
    def __init__(self):
        super().__init__(name="LoaderJson", extensions=["json", "jsonc"])
```

4. Override the `load` method responsible for loading a specific file:
```python
    def load(self, layout_file):
        with layout_file.open() as file:
            return json.load(file)
        return {}
```

The complete example looks like this:
```python
import json
import layoutgen

class LoaderJson(layoutgen.Loader):
    def __init__(self):
        super().__init__(name="LoaderJson", extensions=["json", "jsonc"])
    def load(self, layout_file):
        with layout_file.open() as file:
            return json.load(file)
        return {}
```
> **NB**: This example does not include error handling (eg. if a file cannot be
> read).
