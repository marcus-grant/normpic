# Python Data Model Layer

This document covers the Python reference implementation's data
model layer.
It maps the v0.1.0 manifest contract onto Python types, documents
the dataclass-first design, and points to the surrounding
implementation modules.

The contract itself, including field semantics, canonical forms,
nullability rules, and forward-compatibility constraints, lives in
[manifest-contract.md](manifest-contract.md).
This document does not duplicate those rules.
Where contract behavior is referenced here, the contract is
authoritative if the two ever disagree.

## Status

v0.1 draft, aligned with `manifest-contract.md` v0.1.0.
Field set, types, and module paths track the contract.
Updates here follow contract revisions, never the reverse.

## Design principles

The Python data model layer is dataclass-first and pure.
Models hold data, nothing else.
Serialization, validation, file I/O, and migration are separate
concerns living in adjacent modules.
This makes models trivial to test in isolation and lets the
serializer evolve (formats, validation strategies, version
detection) without touching the models themselves.

The separation between model and serializer is covered in detail
in [schema-versioning.md](schema-versioning.md).
That document also covers how `schema/v0.1.0.json` is loaded and
validated against as the single canonical schema.

## Module organization

Data models live under `normpic/model/`.
Serialization lives under `normpic/serializer/`.

```
normpic/
|-- model/
|   |-- pic.py          # Pic dataclass
|   |-- manifest.py     # Manifest dataclass
|   `-- config.py       # producer Config dataclass
`-- serializer/
    `-- manifest.py     # JSON serialize/deserialize/validate
```

## Dataclasses

The code shown below is illustrative.
Field types and presence mirror the manifest contract; refer to
[manifest-contract.md](manifest-contract.md) for what each field
means and which canonical forms are required.

### Pic

```python
@dataclass
class Pic:
    # required
    hash: str               # b3c32: prefixed Crockford Base32
    relative_path: str
    size_bytes: int
    mtime: datetime

    # optional non-nullable
    original_filename: Optional[str] = None

    # optional nullable
    timestamp: Optional[datetime] = None
    timestamp_source: Optional[str] = None
    camera: Optional[str] = None
    gps: Optional[Dict[str, float]] = None

    # optional array (reserved, unpopulated in v0.1.0)
    tag: List[str] = field(default_factory=list)
```

The nullability distinction is contract-meaningful.
`original_filename` is optional but non-nullable: absent or a
non-empty string, never `None` in the serialized form.
The other optionals are nullable: absent and `None` are
equivalent.
See `manifest-contract.md` for the full nullability matrix.

### Manifest

```python
@dataclass
class Manifest:
    # required
    version: str            # "0.1.0"
    collection_name: str
    generated_at: datetime
    collection_root: str    # always emitted; "." when manifest sits
                            # at the collection root
    pic: List[Pic]

    # optional nullable
    collection_description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
```

`collection_root` is always emitted explicitly, including the
default `"."` case.
The `config` field is intentionally loose: it stores whatever
producer-side record the producer chose to embed.
It is not the typed producer Config below.

### Config

The producer-side typed configuration model.
Distinct from the manifest's `config` field, which is a loose
record.
This dataclass is the typed state the producer uses during a
processing run.

```python
@dataclass
class Config:
    collection_name: str
    collection_description: Optional[str] = None
    timestamp_offset_hours: int = 0
    force_reprocess: bool = False
```

Field set is illustrative.
Phase B implementation may add, remove, or rename fields here as
the producer matures.
This is implementation-side state, not contract.

## Serialization

The serializer layer at `normpic/serializer/` is responsible for
JSON read/write, schema validation, and the
datetime-to-RFC-3339-string conversions the contract requires on
the wire.
Models never serialize themselves.

Design rationale and the schema-artifact relationship are covered
in [schema-versioning.md](schema-versioning.md).

## Related projects

- [manifest-contract.md](manifest-contract.md): contract source of
  truth.
  This document is its Python-implementation companion.
- [schema-versioning.md](schema-versioning.md): versioning
  mechanics, serializer separation rationale, schema artifact
  relationship.
- [conformance.md](conformance.md): the conformance requirement
  that this data model layer must satisfy when used as part of a
  conforming producer or consumer.
- `schema/v0.1.0.json`: canonical schema artifact; the data model
  layer validates against this.
- **future Rust port of normpic** (planned): will have its own
  data-model document with native Rust types.
  The same contract applies to both implementations.
