# Implementation-Side Schema Versioning

This document covers the implementation-side mechanics of schema
versioning in the Python reference implementation of normpic.
It describes how versioned schemas are organized in code, how the
JSON schema artifact relates to Python-side schema modules, how
serialization is separated from the data model, and how future
migration between schema versions is structured.

The contract-side policy lives in
[manifest-contract.md](manifest-contract.md).
That document defines what version numbers mean, what consumers
must accept or reject, and what changes are breaking.
This document does not duplicate that policy.

## Status

v0.1 draft, aligned with `manifest-contract.md` v0.1.0.
This document tracks the contract.
Updates here follow contract revisions, never the reverse.

## Schema artifact and Python module

The JSON Schema at `schema/v0.1.0.json` is the canonical
machine-readable schema artifact.
The Python implementation uses a schema module at
`normpic/model/schema_v0.py` for ergonomic in-Python access.

The relationship between these two artifacts is unresolved as of
v0.1.0 planning.
The Python module could load the JSON at import time, be generated
from the JSON at build time, or be maintained in parallel with an
equivalence test gating commits.
The decision is deferred to Phase B implementation work.

Whichever approach is chosen, the JSON file remains canonical.
The Python module is a convenience over it, never a source of
truth.

## Versioned module structure

Schema modules live under `normpic/model/`.

```
normpic/model/
|-- schema_v0.py      # current v0.x schema
|-- pic.py            # data models
|-- manifest.py
`-- config.py
```

Per the contract policy, v0.x minor bumps may be breaking.
If a migration window requires supporting two v0.x schemas
simultaneously, separate modules are introduced (e.g.
`schema_v0_2.py` alongside a renamed `schema_v0_1.py`).
Otherwise the single `schema_v0.py` is updated in place.
When v1.0 lands, the v0 module is retained for legacy reading
until removal is scheduled.

## Serializer separation

Serialization is a distinct concern from the data model.
The serializer layer at `normpic/serializer/` handles JSON
read/write and JSON Schema validation against the loaded schema
artifact.
Data models in `normpic/model/` remain pure data structures with
no I/O.

This separation allows additional output formats in the future
(YAML, MessagePack, whatever a consumer needs) without changes to
the model layer.

## Future migration

For v0.1.0, migration is out of scope.
Only v0.1.x manifests are supported by the v0.1.x implementation.
Any pre-hiatus manifests on disk are regenerated rather than
migrated.

The migration concern returns when v0.2.0 introduces a breaking
contract change, or when v1.0 lands and v0 manifests need a
forward path.
At that point an implementation module (tentatively
`normpic/migration/`) detects the schema version of incoming
manifests, applies migration steps to bring them forward to the
current internal schema in memory, and rejects manifests that
cannot be migrated.

Migration is asymmetric between producer and consumer.
Producers always emit the current version.
Consumers handle older versions via the migration system.

## Related projects

- [manifest-contract.md](manifest-contract.md): the contract-side
  policy this document complements.
  This document is its implementation-side counterpart.
- [conformance.md](conformance.md): the conformance requirement
  that defines consumer-facing version-handling responsibilities.
- `schema/v0.1.0.json`: the canonical schema artifact the Python
  module mirrors.
- **galleria** (planned, design documented): future consumer that
  will rely on the migration system once it must consume more than
  one schema version.
- **future Rust port of normpic** (planned): will need its own
  implementation-side versioning document analogous to this one.
  The contract-side policy in `manifest-contract.md` applies
  identically across implementations.