# Human Oriented Data Storage (HODS)

Do not depend on any specific piece of software to own your data!


## Project status

Work in progress, early stages


## Overview

World around us generates data at crazy speeds. Thanks to advances in
information technology each day more of that data becomes available to end
users in some machine-readable form. We rely on complex software (database
management systems) or on third parties (Facebook, Gmail) to manage and store
that data. When (and if) we want to *own* our data we are faced with multiple
obstacles:

- It is difficult to setup and configure an instance of database management
  system
- It is difficult to implement (and enforce) a reliable backup strategy
- We become dependent on several very specific pieces of software:
    - The database engine
    - The application that interacts with that engine to perform basic data
      manipulations (create-read-update-delete)

Faced with that many obstacles most of us do not even bother to store
data of relatively low importance. And those who do are risking to lose that
data, which is not unexpected given such a long list of points of failure.

For the reasons stated above most of structured data floating around is
*company*-oriented or *application*-oriented or *machine*-oriented. Not
intended for immediate consumption by *humans*.

*Making structured data more accessible to humans* is the reason this
project exists.

## How it works

To make the idea of Human Oriented Data Storage time proof and extremely
portable we intend to impose as little restrictions as possible. In fact, the
whole [specification][spec] boils down to less than a dozen data points.
Everything else is up to the implementation and can be replaced at any moment.

The main ideas are:

- **Structured data is to be stored in plain text files** serialized with some
  markup that is readable both by humans and by machines. YAML is a very good
  example, JSON is mostly OK too. Any other markup language is acceptable.
- **Each data structure has to be described by a schema** to ensure data validity
  throughout its lifecycle. Jsonschema is a good example, XSD might work for
  some people. As with markup language, selecting the specific schema engine
  is up to implementation.
- **Hash sums are to be used for ensuring data integrity**. To make checksum
  calculation implementation-independent we define the process as follows:
    - Hash sum of the arbitrary data point is the hash sum of that data point
      serialized into a JSON string without any formatting whitespace and
      with all keys ordered alphabetically.
    - Selecting the specific hash algorithm is up to the implementation.

And that's it! To enable compatibility between different implementations the
required information has to be stored in the following way (the corresponding
JSON [schema][schemas] is available in reference implementation):

```javascript
{
    "info": {
        "version": string, // schema identifier for the whole document (usually URL)
        "schema": {
            "data": string,  // schema identifier for 'data' payload: url, filepath or name
            "extra": string  // schema identifier for 'extra' payload
        },
        "hashes": {
            "data": {
                "timestamp": string, // ISO-8601 datetime with timezone (human-readable)
                "md5": string,
                "sha1": string
                // any number of pairs <algorithm name: hash value>
            },
            "extra": { ... }
        }
    },
    "data": { ... },  // 'data' payload, must correspond to the schema referenced above
    "extra": { ... }  // 'extra' payload, must correspond to the schema referenced above
    // any number of payload sections
    // section names 'data' and 'extra' are just used in example and are not required
}
```


## Reference implementation

This repository contains the reference implementation of HODS ideas in Python
language: a [library] and a [command-line application][cli].

Reference implementation supports:

- Storing data in JSON or YAML. StrictYAML is being worked on.
- Validating the data against JSON schema.
- Calculating the most common hash sums: md5, sha1, sha2 family.

The list of supported technologies does not impose any restrictions on authors
of alternative implementations and may be extended in future.


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


[cli]:     docs/commandline.md
[library]: docs/public-api.md
[schemas]: docs/schemas.md
[spec]:    docs/specification.md
