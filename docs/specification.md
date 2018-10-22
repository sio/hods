# Specification for Human Oriented Data Storage


> Work in progress. In case of any inconsistencies please open an [issue] at
> GitHub repo. Meanwhile please refer to the formal [schema] and to the
> overview on [main page](/)


Human Oriented Data Storage (HODS) is a convention for storing structured and
semi-structured data in a format that is readable and editable both by humans
and by machines. We do not impose specific implementation technologies to make
this convention long lasting and extremely portable between different
environments.

1. **HODS data is stored in _documents_**. A document is a single file that
contains structured or semi-structured data in form of a tree. Documents have
to be readable and editable by humans as well as by software. The recommended
way to enable that is to store documents as plain text files with some
lightweight serialization markup.

2. **Each document contains one _info section_ and zero or more _payload
sections_**.
    - _Sections_ are tree-like data structures that are stored directly under
      the top level of the document.
    - _Info section_ is a section that contains internal metadata required by
      HODS: schema identifiers for the whole document and for individual
      payload sections, data hashes for payload sections. It must be stored
      under the following key: `info`.
    - _Payload sections_ are used to store the document's content. Payload
      data may be assigned to any other keys at the top level of the document
      tree. Such keys are refered to as _payload section names_.

3. **Each payload section should be described by a _schema_**. A schema is a
description of the data structure in a formal language. Each schema must have
a unique text identifier (e.g. the URL it is published at). Schemas are used
to ensure validity of data structures after modification.

4. **Each payload section should have a hash checksum of its content**. Hash
sums are used to ensure data integrity throughout its life cycle.

5. **All HODS implementations must use the following process to calculate hash
checksums of payload sections**:
    - Any hashing algorithm may be used. It must have a commonly known name to
      be identifyable by other users.
    - Before processing with that algorithm the data must be serialized into
      JSON string without any formatting whitespace and with all keys sorted
      alphabetically.
    - Multiple hash sums created with different hashing algorithms may be
      provided.
    - Time of hash calculation has to be stored in the _info section_ along
      with the hash value.
    - These requirements are included into the specification to ensure
      compatibility of HODS documents between different HODS implementations.

6. **HODS document must conform to the [schema] published along with this
specification**. It specifies the data structure for the _info section_ and
allows any structure for the _payload sections_. Brief overview of info
section structure is available below:

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


[issue]: https://github.com/sio/hods/issues
[schema]: schemas.md
