# HODS - Human Oriented/Owned Data Storage

Do not depend on any specific piece of software to own your data!


## Project status

Work in progress, early stages


## Installation and usage

Install latest version with pip:

```
$ pip install https://github.com/sio/hods/archive/master.zip
```

Use command line interface:

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

Incorporate HODS into your Python projects:

```python
from hods import Metadata
meta = Metadata({'hello': 'world'})
```


## Support and contributing

If you need help using HODS from command line or including it into your Python
project, please create **[an issue](https://github.com/sio/hods/issues)**.
Issues are also the primary venue for reporting bugs and posting feature
requests. General discussion related to this project is also acceptable and
very welcome!

In case you wish to contribute code or documentation, feel free to open **[a
pull request](https://github.com/sio/hods/pulls)**. That would certainly make
my day!

I'm open to dialog and I promise to behave responsibly and treat all
contributors with respect. Please try to do the same, and treat others the way
you want to be treated.

If for some reason you'd rather not use the issue tracker, contacting me via
email is OK too. Please use a descriptive subject line to enhance visibility
of your message. Also please keep in mind that public discussion channels are
preferable because that way many other people may benefit from reading past
conversations.  My email is visible under the GitHub profile and in the commit
log.


## License and copyright

Copyright 2018 Vitaly Potyarkin

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
