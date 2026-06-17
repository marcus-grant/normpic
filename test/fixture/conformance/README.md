# Conformance Fixtures


## Purpose

This directory contains manifest fixtures used as the
cross-implementation contract test for NormPic's manifest format.

Every conformant implementation of the manifest contract (Python now,
anticipated Rust port, future Static Site Generator plugins) MUST:

- Accept every fixture under `valid/` without errors.
- Reject every fixture under `invalid/` for the reason indicated by
  its filename.
- Accept every fixture under `consumer-lenient/` when acting as a
  consumer, but never emit such fixtures when acting as a producer.

The contract these fixtures encode lives in
[doc/architecture/manifest-contract.md](../../../doc/architecture/manifest-contract.md).
The machine-readable schema is at
[schema/v0.1.0.json](../../../schema/v0.1.0.json).

## Directory Structure

```
test/fixture/conformance/
|-- README.md                # This file
|-- valid/                   # Manifests every implementation MUST accept
|-- invalid/                 # Manifests every implementation MUST reject
`-- consumer-lenient/        # Manifests producers MUST NOT emit but
                             # consumers SHOULD accept (e.g. lowercase
                             # Crockford on read)
```

## Categories

### Valid

Manifests that are correct per the v0.1.0 contract and MUST pass both
JSON Schema validation and any additional implementation-level
validation.

Each file demonstrates a particular shape worth covering:

- `minimal.json`: smallest valid manifest (no pics, default
  `collection_root`).
- `full.json`: all top-level and per-pic fields populated.
- `collection-root-default.json`: explicit `"."` for collection root
  (the canonical form when manifest sits at collection root).
- `collection-root-traversal.json`: leading `..` segments navigating
  from manifest location to collection root.
- `empty-collection.json`: zero pics, all top-level fields present.
- `optional-fields-as-null.json`: nullable optional fields emitted as
  explicit `null` (producer SHOULD prefer absence, but `null` is
  contractually accepted).

### Invalid

Manifests that violate exactly one contract rule and MUST be rejected.
Each filename names the violated rule.

Two layers of rejection are possible:

- **JSON Schema layer**: rejected by validating against
  `schema/v0.1.0.json`.
- **Implementation layer**: rejected by additional checks beyond
  what the JSON Schema can express (e.g. `..` segments after the
  leading run in `collection_root`).

Filenames carry a hint about which layer catches the violation:

| Fixture                                         | Caught by      |
|-------------------------------------------------|----------------|
| `hash-bad-prefix.json`                          | JSON Schema    |
| `hash-wrong-length.json`                        | JSON Schema    |
| `relative-path-absolute.json`                   | JSON Schema    |
| `relative-path-dot-segment.json`                | JSON Schema    |
| `relative-path-dotdot-segment.json`             | JSON Schema    |
| `relative-path-backslash.json`                  | JSON Schema    |
| `collection-root-leading-dotslash.json`         | JSON Schema    |
| `collection-root-uri-scheme.json`               | JSON Schema    |
| `timestamp-offset-form.json`                    | JSON Schema    |
| `gps-lat-out-of-range.json`                     | JSON Schema    |
| `empty-required-string.json`                    | JSON Schema    |
| `null-for-non-nullable-optional.json`           | JSON Schema    |
| `missing-required-field.json`                   | JSON Schema    |
| `original-filename-path-separator.json`         | JSON Schema    |

Implementation-layer fixtures live in `invalid/impl/`.
They pass JSON Schema validation and are caught by
`normpic.util.manifest_validate.impl_validate`:

| Fixture (in `invalid/impl/`)                    | Caught by      |
|-------------------------------------------------|----------------|
| `collection-root-nonleading-dotdot.json`        | Implementation |
| `timestamp-bad-calendar.json`                   | Implementation |

A conformant implementation rejects all of these regardless of which
layer detects the violation.
The split exists so a dev debugging a failing fixture knows where to
look.

### Consumer-Lenient

Manifests that violate the producer side of the contract but that
consumers SHOULD accept (the "be lenient in what you accept" half of
Postel's law, applied at the points the contract explicitly allows).

- `lowercase-crockford-hash.json`: hash emitted in lowercase
  Crockford Base32.
  Producers MUST emit uppercase, but consumers SHOULD tolerate
  lowercase on read (see Hash identity section of the contract doc).

## Usage Pattern

The intended test pattern in Python:

```python
import json
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator

CONFORMANCE = Path(__file__).parent / "fixture" / "conformance"
SCHEMA = json.loads(
    (Path(__file__).parent.parent / "schema" / "v0.1.0.json").read_text()
)
VALIDATOR = Draft202012Validator(SCHEMA)


@pytest.mark.parametrize("path", sorted((CONFORMANCE / "valid").glob("*.json")))
def test_valid_fixture_passes_schema(path):
    manifest = json.loads(path.read_text())
    errors = list(VALIDATOR.iter_errors(manifest))
    assert not errors, f"{path.name}: expected valid, got {errors}"


@pytest.mark.parametrize("path", sorted((CONFORMANCE / "invalid").glob("*.json")))
def test_invalid_fixture_rejected(path):
    manifest = json.loads(path.read_text())
    schema_errors = list(VALIDATOR.iter_errors(manifest))
    impl_errors = normpic.validate_manifest_extra_rules(manifest)
    assert schema_errors or impl_errors, (
        f"{path.name}: expected rejection, neither layer caught it"
    )


@pytest.mark.parametrize(
    "path", sorted((CONFORMANCE / "consumer-lenient").glob("*.json"))
)
def test_consumer_lenient_fixture_accepted_by_consumer(path):
    manifest = json.loads(path.read_text())
    result = normpic.read_manifest(manifest)
    assert result is not None
```

The Rust port runs the equivalent against its own validator and
parser; the fixture set is the shared contract test.

## Adding New Fixtures

When adding a fixture:

1. Decide which directory it belongs in (`valid/`, `invalid/`, or
   `consumer-lenient/`).
2. Name the file after the property it demonstrates or the rule it
   violates.
3. For `invalid/` fixtures, violate exactly one rule.
   The rest of the manifest should be otherwise valid so the
   intended test signal is unambiguous.
4. Update the table above if adding an `invalid/` fixture so the
   layer-of-rejection annotation stays current.
5. Confirm the fixture behaves as expected against both the JSON
   Schema and the current Python implementation before committing.

## References

- [Manifest contract](../../../doc/architecture/manifest-contract.md):
  authoritative semantic contract.
- [JSON Schema artifact](../../../schema/v0.1.0.json): mechanical
  validation rules.
- [Schema versioning](../../../doc/architecture/schema-versioning.md):
  implementation-side migration mechanics (distinct from the
  consumer-facing contract).