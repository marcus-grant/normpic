# Conformance Test Harness

## Purpose

The conformance harness verifies that the normpic Python implementation
matches the v0.1.0 manifest contract.
It does this through shared fixture files that any conformant
implementation (Python now, anticipated Rust port, future SSG plugins)
can run against.
Two implementations that both pass the same fixture set agree on the
contract in the only sense that matters: observable behavior on shared
input.

The contract rules live in
[architecture/manifest-contract.md](../architecture/manifest-contract.md).
The fixture inventory that defines required coverage lives in
[architecture/conformance.md](../architecture/conformance.md).
This document covers the harness itself: how it is structured, how to
run it, and how to add fixtures.

## Two-layer model

Manifest validity is enforced at two layers.
The harness exercises both.

**Schema layer.**
`jsonschema.Draft202012Validator` validates against `normpic/schema/v0.1.0.json`.
A manifest that fails the schema is invalid; no further interpretation
is permitted.

**Implementation layer.**
Some contract rules cannot be expressed in JSON Schema and are enforced
by code directly.
The leading example is the `collection_root` constraint that `..`
segments may only appear as a leading run.
The implementation-layer validator (`normpic.validate_manifest_extra_rules`)
runs after schema validation.
It is added in `tst/conformance-invalid-impl-layer`; a stub is present
from the first harness commit.

Each fixture is labeled with the layer responsible for its rejection.
See the inventory in `architecture/conformance.md`.

## Fixture categories

Fixtures live under `test/fixture/conformance/`.

```
test/fixture/conformance/
|-- README.md
|-- valid/           Manifests every conforming implementation MUST accept
|-- invalid/         Manifests every conforming implementation MUST reject
`-- consumer-lenient/ Producers MUST NOT emit; consumers SHOULD accept
```

**valid**: correct per the contract; must pass both schema and
implementation-layer validation.

**invalid**: violates exactly one contract rule; must be rejected.
Each filename names the violated rule.

**consumer-lenient**: violates the producer contract in a way consumers
should tolerate (e.g. lowercase Crockford hash).
Schema-layer rejection is expected; a consumer-normalize path accepts
after normalization.

## Harness API

`test/helpers/conformance.py` exports the following.
Import as `from test.helpers.conformance import ...`.

```
CONFORMANCE_DIR   Path to test/fixture/conformance/
SCHEMA_PATH       Path to normpic/schema/v0.1.0.json

load_schema()     -> dict
load_fixture(path: Path) -> dict
schema_validate(manifest: dict) -> list[ValidationError]
```

Future PRs add:

```
impl_validate(manifest: dict) -> list[str]
    (tst/conformance-invalid-impl-layer)

consumer_normalize(manifest: dict) -> dict
    (tst/conformance-consumer-lenient)
```

## Test file

`test/unit/test_conformance.py` contains parametrized tests, one per
fixture category.
At the end of `tst/conformance-harness` only the valid category is
tested; invalid and consumer-lenient tests are added as fixtures are
built in later PRs.

## How to add a fixture

1. Pick the category (`valid/`, `invalid/`, or `consumer-lenient/`).
2. Name the file after the property demonstrated or rule violated.
   Match the name to the inventory entry in `architecture/conformance.md`
   for traceability.
3. For `invalid/` fixtures, violate exactly one rule; keep everything
   else valid so the test signal is unambiguous.
4. Verify the fixture behaves as expected against both the JSON Schema
   and the current Python implementation before committing.
5. Update the layer-of-rejection table in
   `test/fixture/conformance/README.md` for any new `invalid/` fixture.

One fixture per commit per the project TDD discipline, except when
several variants exercise the same rule; in that case group by rule.
