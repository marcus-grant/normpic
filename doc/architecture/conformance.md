# Manifest Conformance Requirement

This document specifies what conformance to the v0.1.0 manifest contract
means, and what any normpic implementation must demonstrate to claim
conformance.
The manifest contract itself lives in
[manifest-contract.md](manifest-contract.md).
This document does not duplicate its rules.
It specifies how those rules are verified.

## Status

v0.1.0 draft, bound to manifest-contract.md v0.1.0.
This document is versioned in lockstep with the manifest contract and
never independently.

## Purpose

The normpic ecosystem is designed for multi-implementation.
The Python reference implementation is one producer.
Future producers (a Rust port of normpic, third-party tools that emit
normpic manifests) and consumers (galleria, SSG plugins, archival
readers) must agree on what a valid manifest is and on how to behave
when one arrives.

A prose contract document is necessary but not sufficient.
Different readers interpret prose differently.
Conformance fixtures, concrete JSON manifests with known expected
behavior, are the cross-implementation safety net.
Two independent implementations that both pass the same conformance
suite agree on the contract in the only sense that matters: observable
behavior on shared input.

Conformance fixtures are implemented per the project-wide TDD
discipline: one fixture at a time, against the schema, with the
fixture inventory below as the coverage target.
They are not bulk-generated.

## Two-layer model

Manifest validity is enforced at two layers.
Conforming implementations MUST apply both.

### Schema layer

The JSON Schema at `schema/v0.1.0.json` mechanically validates the
structural rules expressible in JSON Schema Draft 2020-12: required
fields, types, enum membership, regex patterns, numeric ranges, array
shape.
A manifest that fails the schema is invalid.
No further interpretation is permitted.

### Implementation layer

Some contract rules cannot be expressed in JSON Schema and MUST be
enforced by the implementation directly.
The leading example is the `collection_root` constraint that `..`
segments may only appear as a leading run.
JSON Schema patterns cannot express "no X after the first Y" in the
general case.

Other implementation-layer concerns include cross-field consistency,
file-existence checks where the implementation has filesystem access,
and any future rule that escapes JSON Schema's expressiveness.

The layer that catches each violation is part of the contract surface.
A fixture is not merely "valid" or "invalid".
It is "valid", "rejected by the schema layer", or "rejected by the
implementation layer".

## Fixture categories

Three categories, each proving something different about an
implementation.

### valid

Manifests that are correct per the v0.1.0 contract.
Every conforming producer MUST be capable of emitting an equivalent
manifest given suitable input.
Every conforming consumer MUST accept these manifests and operate on
them without error.
A consumer that rejects one of these is non-conforming.

### invalid

Manifests that violate the contract in exactly one identified way.
The fixture metadata states which rule is violated and which layer
must catch it.
Conforming consumers MUST reject these and identify the violation.
Conforming producers MUST NOT emit them.

Each fixture isolates a single rule violation, so test failures are
unambiguous.
A fixture that fails for two reasons does not prove which rule is
broken.

### consumer-lenient

Manifests that violate the producer contract in a way consumers SHOULD
tolerate after normalization.
The canonical case is a hash with lowercase Crockford Base32 letters:
the producer rule requires uppercase, but the round-trip semantics are
unambiguous and a strict rejection would harm interoperability for
negligible gain.

Producers MUST NOT emit these.
Consumers SHOULD accept them, normalizing on read.
This category encodes Postel's Law selectively, only where it does not
erode the contract.

## Fixture inventory

Each entry below is a required case, not a literal filename.
Implementations are free to add more fixtures.
They MUST cover every case listed here.
Fixture filenames in implementations should match the case names for
traceability across implementations.

### Required valid cases

Each MUST validate clean against the schema and operate correctly in
any conforming consumer.

- **minimal**: only required top-level fields populated, empty pic
  array, `collection_root` set to `"."`.
- **full**: every top-level and per-pic field populated, exercising
  every optional field including `tag`, `gps`, `timestamp_source`, and
  the loose `config` object.
- **collection_root default form**: `collection_root` set to the
  literal string `"."` with at least one pic.
  Verifies the most common producer output.
- **collection_root traversal form**: `collection_root` set to a path
  with leading `..` segments and no segments after the leading run.
  Verifies the traversal use case (manifest stored separately from
  photos).
- **empty collection**: zero pics with top-level optional fields
  populated.
  Verifies that an empty `pic` array is valid and does not force
  omission of top-level metadata.
- **optional fields as null**: every nullable optional field set
  explicitly to `null`.
  Verifies that consumers treat `null` and absence equivalently for
  nullable optionals.

### Required invalid cases

Each MUST be rejected.
The "Layer" column states which layer is responsible.

| Case                                  | Rule violated              | Layer |
|---------------------------------------|----------------------------|----------------|
| hash w/ non-`b3c32:` prefix        | hash algorithm prefix      | schema |
| hash w/ wrong length after prefix   | hash digest length         | schema  |
| relative_path absolute (leading `/`) | relative_path canonical    | schema |
| relative_path w/ `.` segment        | relative_path canonical    | schema |
| relative_path w/ `..` segment       | relative_path canonical    | schema |
| collection_root w/ leading `./`    | collection_root canonical  | schema |
| collection_root w/ non-leading `..` | collection_root canonical  | impl.  |
| timestamp with `+00:00` offset form | timestamp canonical        | schema |
| GPS latitude outside -90..90        | GPS range                  | schema |
| empty required string               | non-empty required strings | schema |
| null for non-nullable optional      | nullability rules          | schema |
| missing required field              | required-field rule        | schema |
| relative_path with backslash        | canonical forms            | schema |
| original_filename w/ path separator | no path component          | schema |
| timestamp w/ invalid calendar value | RFC 3339 validity          | impl.  |
| collection_root with URI scheme     | no URI in v0.1.0           | schema |

Implementations MAY add cases for additional violations of the same
rules (multiple hash-length variants, additional canonical-form
breaks).
Every distinct rule listed above MUST have at least one case.

### Required consumer-lenient cases

- **lowercase Crockford in hash**: producer-side rule violation.
  Consumers SHOULD accept with case-normalization rather than reject.

## Producer responsibilities

A conforming producer MUST:

- emit manifests that pass the schema layer on every input the
  producer accepts.
- emit manifests that satisfy implementation-layer rules the schema
  cannot express.
- never emit a manifest matching any case in the invalid or
  consumer-lenient inventories.
- be capable of emitting an equivalent of every valid case given
  suitable input.

## Consumer responsibilities

A conforming consumer MUST:

- accept every valid case and operate on it without error.
- reject every invalid case with an identifiable error referencing the
  violated rule.
- accept every consumer-lenient case after normalization, rather than
  reject.
- apply both layers of validation (schema first, then
  implementation-layer checks) before operating on manifest data.

## Acceptance criteria for v0.1.0

To claim v0.1.0 conformance an implementation MUST provide a test
suite that:

- exercises every case in the fixture inventory above.
- identifies the layer at which each invalid case is rejected,
  matching the layer column.
- produces a single pass/fail result per case.
- runs deterministically; conformance MUST NOT depend on filesystem
  state, network availability, or wall-clock time.

The Python reference implementation's conformance suite at
`test/fixture/conformance/` is the canonical example.
Independent implementations are encouraged to share fixture files with
the reference suite where format permits.

## Related projects

- **manifest-contract.md**: source of truth for the contract rules
  this document verifies.
  Conformance is conformance to that document.
- **schema/v0.1.0.json**: machine-readable schema for the schema
  layer.
- **galleria** (planned, design documented): first downstream
  consumer.
  Will be validated against the consumer responsibilities here once it
  adopts v0.1.0.
- **composer** (parked): orchestrates normpic invocation in the
  gallery pipeline.
  Does not consume manifests directly but depends on conforming
  behavior from both normpic and galleria.
- **future Rust port of normpic** (planned): primary motivation for
  the cross-implementation safety net this document specifies.

