# Plugin Generator Writing Guide

Generator plugins generate something from the layouts dictionary. They may be
used for code generation but can also be useful to generate configuration files
or binaries (image vector table, logical block descriptor, etc).

## How to write a generator

Layoutgen provides the abstract base class
[Generator](../src/layoutgen/abc/generator.py) that one must derive from to
create a specific generator.


### Generator abstract base class

The `Generator` base class has mainly two methods.

```python
Generator.__init__(self,
    name: str, extension: str, priority: int = 0, clone_layout: bool = True)
```

Initialize some general properties available for all generators:
  * The `name` is used to identify the generator (eg. for logging).
  * The `extension` is used for the output file name extension.
  * The `priority` defines the order in which all generators will be executed
    starting with the plugin having the higher priority. If two generators share
    the same priority the order is unspecified. Defaults to 0 and can be
    negative.
  * The `clone_layout` parameter tells whether the layout dict will be cloned
    when passed to the `generate` method. Passing a clone avoids unintended
    side-effects between generators since they are allowed to modify the layout
    dict. Defaults to True.

```python
Generator.generate(self, filename: pathlib.Path, layout: dict)
```

Abstract method taking the layout dictionary and the output file path.
Modifying the layout dict is allowed, but if `clone_layout` is set to True then
changes will not be seen by generators executed afterward. However if
`clone_layout` is False, be aware that every generators executed after the
current one will observed the modifications and this can lead to inconsistent
states or unexpected outputs.

### Block tree traversal

As the layout is structured as a tree of blocks, it can be traversed
recursively to process all the blocks. To do this, layoutgen provides some
utilities to ease this traversal:
- the abstract base class BlockProcessor that one must derive from to execute a
  specific processing.
- the traverse_block_tree function to execute the traversal.


#### The BlockProcessor abstract base class

This abstract base class mainly has 4 methods.

```python
BlockProcessor.block_entry(self, block: dict, level: int)
```

Abstract method called when examining a block for the first time. This is the
most useful callback and is currently used by most processors implemented in the
parser.

```python
BlockProcessor.pre_recurse(self, block: dict, level: int)
```

Abstract method executed before recursing into child blocks.

```python
BlockProcessor.post_recurse(self, block: dict, level: int)
```

Abstract method executed after recursion into child blocks is done. It may be
useful for processing requiring that all children are processed before the
parent.

```python
BlockProcessor.block_exit(self, block: dict, level: int)
```

Abstract method executed when inspection of a block is done, just before moving
to the next sibling.


#### The traverse_block_tree function

```python
traverse_block_tree(processor: BlockProcessor, block: dict)
```

Function implementing a depth-first recursive descent. It takes the `block` from
which the traversal shall start (usually the root node) and use the callbacks
defined in `processor` at the appropriate moment.


### Example

Layoutgen already includes built-in generators to create C headers, Python and
Shell scripts, the S32G Image Vector Table binary, and others.

They make a pretty good set of plugin examples, so do not hesitate to check them
out.
