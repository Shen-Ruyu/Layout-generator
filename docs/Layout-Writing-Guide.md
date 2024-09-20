# Layout Writing Guide

This document provides detailed instructions about how to write a layout
configuration file.
It gives also useful hints, general considerations, and some design notes about
the underlying parser.

Layout files are configured using YAML, as this is currently the only supported
language.
You may also [define your own loader plugin](./Plugin-Loader-Writing-Guide.md)
if you want to use an other language.
However, the following instructions will be valid for YAML-based layouts
but not necessarily for other languages.


## Layout validation

Layouts are validated using the
[layout JSON schema](../src/layoutgen/layout_schema.json),
based on the JSON Schema specification (draft version 2020-12) from
[json-schema.org](https://json-schema.org/).

The schema describes the keys usable inside a layout file, which ones are
required, and the expected format for the values. Default values are also
mentioned for some non-required fields but are just indicative and are not
used by the parser. Do not hesitate to take a look at it.


## Layout structure

Layout configuration files contain mainly two type of components: layout and
block descriptors.

The top-level object is always a layout descriptor.
With the current schema definition, arrays of layout descriptors are not
accepted, so there can be only one layout descriptor per file.

A layout descriptor includes a list of block descriptors, which may in turn
include other blocks descriptors. Consequently, the layout document forms a
tree of descriptors. We will therefore use in this guide some terminology
related to trees and graphs like root, parent, children and sibling nodes, a
single node being a descriptor (either layout for the root or block).


### Layout descriptor

The layout descriptor includes the following keys:
- `name`: the layout name
- `version`: its version
- `project`: the project it is part of
- `start_address`: the memory device mapped address
- `size`: the memory device size in bytes
- `blocks`: a list of block descriptors

All those properties are required.


### Block descriptor

A block descriptor contains the following keys:
- `name`: the block name
- `size:` its size in bytes
- `alignment`: its alignment in bytes
- `start_address`: its start address
- `binary`: the name of the binary file that should be flashed within this
    block
- `blocks`: a list of sub-block descriptors

> **Warnings**:
> - The blocks shall be listed in a consistent ascending address order.
>   Descending order may be added in the future.
> - Sibling blocks shall not overlap.
> - If both start_address and alignment are explicitly provided, they shall be
>   coherent.
>
> Otherwise, errors will be emitted during parsing.

Currently, only the block name is strictly required. The other fields either
have a default value (refer to the schema), or may be inferred if enough
information are given.

The default alignment value is 1 byte.

The default binary file is an empty string.

The following rules are applied to infer the block start address if it is not
explicitly provided:
- if there is no previous sibling block then use the parent's start address
- otherwise use the previous sibling block start address aligned at the given
  alignment

The following rules are applied to infer the block size if it is not explicitly
provided:
- if there is no child block then use a 0 byte size
- otherwise the size will be the difference between the lower-most child start
  address and the upper-most child end address

> **NB**: Blocks with 0 byte size can be useful to declare markers or labels.


### Other properties

#### Useful properties

Some properties shall not appear in the layout description file, but may still
be used by the code generator plugins:
- `end_address`: the end address of a descriptor (`start_address` + `size`).
- `comment`: both layout and block descriptors support comments. Even if YAML
  natively supports comment, some other languages might not (eg. JSON). Also it
  can be used to add some metadata to a descriptor providing additional
  information to a generator.

#### Private properties

If you dive into the parser code or take a look at the generated dictionary,
you may find the following keys starting with an `_`.

Those are private properties that shall only be used by the parser and not by
the code generators.

Still, here is a bit of explanation about those keys as a design note:
- `_block_order_ascending`: boolean specific to the layout descriptor,
  it specifies the detected layout order (True if ascending, False otherwise).
- `_size_pending`: temporary boolean property used to defer the computation of a
  block size until all its children start address and size are known.


### Fields format

The following formats are used for the fields of both the layout and block
descriptors.

#### Name and project

The `name` and `project` values should be valid identifier for most
programming languages: ASCII characters including letters, numbers or
underscore, and must not start by a number.

#### Size and alignment

The `size` and `alignment` values can just be plain integers, but for a better
clarity they may include the following byte units: `B`, `KB`, `MB`, `GB` or
`TB`. Those are 1024 factor, not 1000. Hence, `1KB` will be 1024 bytes and `1MB`
will be 1048576 (1024*1024) bytes.

#### Start_address and end_address

The `start_address` and `end_address` value is a plain integer, but for clarity
it is highly recommended to use the hexadecimal notation with _ as digit
separator, eg. `0x_DEAD_BEEF`.
