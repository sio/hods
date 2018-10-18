# Command line interface to HODS

HODS offers an easy to use command line interface inspired by git. All
actions are relayed to one of subcommands.

To invoke command line interface either use `hods` or execute the Python
module directly: `python -m hods`.


## Usage

```
$ hods --help
Usage: hods SUBCOMMAND [ARGUMENTS]
       hods help SUBCOMMAND

Manage structured data stored in plain text files with YAML or JSON formatting.

Available subcommands:
    check
    edit
    new
    rehash

To view help message for a specific subcommand use:
    hods help SUBCOMMAND
```


## Subcommands

### hods check

```
hods check --recursive [FILENAME1] [FILENAME2] ...
```

Check hash values and validate schemas for metadata file(s).

Outputs short status message for each of checked files. If not files are
listed in the commandline `check` looks for known filetypes in the current
directory (and in its subdirectories if `--recursive` tag is specified).

### hods edit

```
hods edit [FILENAME1] [FILENAME2] ...
```

Edit metadata file(s) with default `$EDITOR`. Data hashes are updated
automatically after closing the editor.

If changed document does not conform to its schema or the editor crashes, you
can recover the previous version of the document from `*.hods~` file in the
same directory.

### hods new

```
hods new [--type=ClassName] [FILENAME1] [FILENAME2] ...
```

Create metadata file(s) and open them for editing.

Supports specifying HODS metadata class name like `--type=Metadata` (default)
or arbitrary Python classes with full import path, e.g:
`--type=package.module.CustomMetadata`.

File type is detected automatically based on filename extension:

- `*.json` for JSON files
- `*.yml` or `*.yaml` for YAML files

If no filename is specified, a single file named `data.hods.yml` is created.

### hods rehash

```
hods rehash [--sections=SECTION1,SECTION2|--sections-all]
    [FILENAME1] [FILENAME2] ...
```

Update hash values for metadata file(s).

If the names of sections are provided, hashes will be calculated only for those
sections.

If no section names are provided, hashes will be calculated only for sections
that already have some previous hash value.
