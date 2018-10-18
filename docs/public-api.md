# Public API of HODS Python implementation

HODS exposes a Python library to allow other developers to add HODS support to
their applications.

All public API entry points are available from the top level `hods` package,
e.g.:

```python
from hods import Metadata
meta = Metadata({'hello': 'world'})
```

## Classes

### Metadata

Holds structured data with a defined schema (according to HODS specification).

Validates data against schema after each change. Provides interface to
calculate data hashes and to write serialized data structure to files.

#### `__init__(self, data=None, filename=None, fileformat=None)`

Initialize new instance.

Arguments:

- `data` - Any tree-like data structure. If it does not conform to HODS
  specification, it is considered only a payload and the required data
  structures are created around it.
- `filename` - The file name (with path if necessary) to load serialized data
  from.
- `fileformat` - A string specifying the file format. If not provided, the
  file format will be detected based upon the file extension.

If neither `data` nor `filename` are provided an empty Metadata object is
created.

#### `validate_hashes(self, write_updates=False, sections=(), required=('md5', 'sha256'))`

Check validity of data hashes and write updated values if necessary

Arguments:

- `write_updates` - If True, the updated hash value will be written to the
  data structure. If False and the hash does not match its stored value, the
  `HashMismatchError` will be raised.
- `sections` - List of data sections to calculate hashes for. If not provided,
  the hashes will be calculated only for sections that already have some
  previous hash value stored.
- `required` - Sequence of names of hashing algorithms required for each of
  specified sections.

#### `write(self, filename=None, fileformat=None, backup='.hods~')`

Write changed data structure into the file

Arguments:

- `filename` - Path to the destination file. If file does not exist, it will
  be created. If its parent directory does not exist, an exception will be
  raised.
- `fileformat` - A string specifying the file format. If not provided, the
  file format will be detected based upon the file extension.
- `backup` - Suffix for backup files. If write operation finishes
  successfully, the backup file will be deleted. If empty or None, no backups
  will be created before writing.


### TreeStructuredData

Generic data class. Keeps all data in one tree-like object and exposes its
nodes via attributes. Child objects refer to the same data tree as the parent.

Handles reading, modification and validation of data structure.

Also provides dictionary style access as a fallback. The recommended way to
access data values is using attribute notation.

#### `__init__(self, data, parent=None, validator=None)`

Initialize new instance.

Arguments:

- `data` - The underlying data structure. The top level object has to be a
  mapping (the root of the data tree).
- `parent` - Used internally to build relationships in the data tree.
- `validator` - The function used to validate this data structure. Has to
  accept a single argument (data tree) and to raise one of `ValidationErrors`
  in case the supplied data does not pass validation.

#### `validate(self)`

Ensure this data tree and all its parents are valid, raise one of
`ValidationErrors` otherwise.


## Exceptions

### HashMismatchError

This error is raised when data does not match its stored hash value.

### ValidationErrors

This is actually a tuple of exceptions. Use it to catch schema violations.

> Packing validation errors into a tuple is required because the `try/catch`
> block [can not accept][ABC exception bug] abstract base classes, and most
> of schema validation is expected to be performed by third party modules.

[ABC exception bug]: https://bugs.python.org/issue12029
