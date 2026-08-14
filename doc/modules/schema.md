# Manifest schema

## What this is

The manifest schema is a single JSON Schema (Draft 2020-12) artifact
at [`normpic/schema/v0.1.0.json`](../../normpic/schema/v0.1.0.json).
It is the mechanical-validation half of the two-layer contract: the
schema enforces structure and canonical forms that JSON Schema can
express, and the implementation enforces the rest.

## Single source of truth

Field names, semantics, required and optional splits, and canonical
forms are defined once, in
[manifest-contract.md](../architecture/manifest-contract.md).
This document does not restate them.
The schema artifact carries a `description` on each definition, so the
file is self-documenting; read it alongside the contract.

## How the producer uses it

The producer loads `schema/v{version}.json` from disk at validation
time and validates every emitted manifest against it.
There is no per-version Python schema module.
The JSON artifact is the only schema, so a single standard is shared
across any language or framework that implements the contract.

## Validation layers

Rules that JSON Schema cannot express (semantic equivalence of absent
and null, producer style preferences, and the restriction on `..`
segments at non-leading positions in `collection_root`) are defined in
the contract and enforced by implementations.
See [conformance.md](../architecture/conformance.md) for the full list
of cases and which layer catches each.

## Versioning

Schema versions are files: `schema/v{version}.json`.
A new contract version ships a new file; the producer loads the file
matching the manifest `version`.
See [schema-versioning.md](../architecture/schema-versioning.md).
