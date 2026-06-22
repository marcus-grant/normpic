# NormPic - v0.1 Contract Alignment TODO

## Current Status: v0.1 Contract Redesign In Progress

The manifest contract has been redesigned post-hiatus.
The existing Python implementation reflects the pre-hiatus contract
and is being aligned to the new one.
The pre-hiatus "MVP complete" claim is subsumed by this larger v0.1
scope; existing tests still pass against the old contract but are
updated as part of Phase B below.

See [architecture/manifest-contract.md](architecture/manifest-contract.md)
for the full v0.1 contract.

## Critical Reference Documents

Authoritative planning artifacts for v0.1:

- [Manifest Contract](architecture/manifest-contract.md): the durable
  v0.1 contract.
- [Conformance Requirement](architecture/conformance.md): defines the
  fixture spec all implementations must satisfy to claim v0.1
  conformance.
- `schema/v0.1.0.json`: machine-readable schema artifact.
- `test/fixture/conformance/`: fixtures implementing the conformance
  spec.
  Built per Phase B.
- [Schema Versioning](architecture/schema-versioning.md):
  implementation-side migration mechanics (distinct from the
  contract).
- [ROADMAP.md](ROADMAP.md): post-v0.1 planning.
- [CHANGELOG.md](CHANGELOG.md): development history.

## Conformance Fixture Discipline

Conformance fixtures are implementation artifacts, not planning.
They are built one fixture at a time against the inventory in
`architecture/conformance.md`, per project TDD discipline.
Full inventory coverage is required before Phase D verification.

## Working Discipline

The workflow, planning, TDD, commit, QA, style, and
document-maintenance rules for every PR below live in
[doc/CONTRIBUTE.md](CONTRIBUTE.md).
That document is the source of truth for how work is done here.
This file does not restate those rules, so they cannot drift.

Two points specific to this phase, not in CONTRIBUTE:

- Group conformance fixtures by rule, not by field.
  Several variants of one rule may share a commit; do not bulk
  generate.
- CHANGELOG archival, pre-MVP.
  Before MVP ships, the current doc/CHANGELOG.md is archived (e.g.
  doc/CHANGELOG-v0.1.md) and a fresh CHANGELOG.md started.
  Flagged so the append-and-prune discipline stays sustainable until
  that archival lands.

## Critical Technical Details

- This is a uv-managed project: use `uv run pytest` (NOT
  `python -m pytest`).
- Source code location: `normpic/` directory (was `src/` before the
  packaging fix).
- Test command: `uv run pytest test/` for the full suite.
- Linting: `uv run ruff check` (must pass before commits).

## Open Contract Decisions

See the "Decide before v0.1 ships" section in
`architecture/manifest-contract.md`.

Currently one open item: pre-hiatus field-name reconciliation
(addressed in Phase B below).

The list shrinks to zero before v0.1.0 is published.

## Sequenced Tasks to Ship v0.1.0

Each task carries an explicit upstream trigger so a developer
picking this up knows what to do and when.

### Phase B: Implementation Alignment

Triggered by Phase A planning artifacts merged.

Phase B is sequenced as 14 PRs.
Each PR follows the Working Discipline preamble above.
The PRs in order:

- fix/contract-schema-reconciliation **complete**
- ref/field-name-reconciliation **complete**
- tst/conformance-harness **complete**
- tst/conformance-valid-fixtures **complete**
- tst/conformance-invalid-path-rules **complete**
- tst/conformance-invalid-impl-layer **complete**
- tst/conformance-consumer-lenient **complete**
- tst/conformance-invalid-misc-rules **complete**
- fix/schema-not-pattern-typeguard **complete**
- ft/hash-blake2b-crockford **complete**
- ref/pic-model-v01-contract
- ref/manifest-model-v01-contract
- ref/serializer-v01-contract
- ref/manifest-manager-v01-contract
- chr/pyright-clean (end of Phase B; see body below)

#### chr/pyright-clean

Bring the tree to green under `uv run pyright`, then wire pyright
into the enforced quality gate (pyproject or task runner) so it is
machine-checked, not convention-only.
The tree currently reports 42 pyright errors.

Plan must triage before implementing:

- Real typing gaps in live code: fix with annotations only, no
  change to implementation or test logic.
- Errors originating in stale code (`deleteme-normpic-modules/` or
  other dead artifacts): the fix is deletion, which is a scope and
  behavior change, not a typing pass.
  Escalate the triage outcome for approval before proceeding, since
  it changes the nature of the PR.

Deconflict any deletions here against the Phase E pre-extraction
sweep so the two do not double-claim the same removals.

#### Schema source of truth

The canonical schema/v0.1.0.json is the single source of truth for
manifest validity.
The producer loads and validates against it directly, on both emit
and read.
The hand-maintained dicts in normpic/model/schema_v0.py
(MANIFEST_SCHEMA, PIC_SCHEMA, ERROR_SCHEMA) are deleted.
This closes the prior dual-schema split, where the producer
self-validated against a code dict that could drift from the
contract.
Nothing downstream consumes normpic yet, so this is a clean cutover
with nothing to preserve.
Each PR lands green.
The model PRs keep schema_v0.py in lockstep as their bodies
specify, so the producer stays valid throughout.
ref/serializer-v01-contract performs the cutover: once pic.py and
manifest.py are contract-shaped, it switches validation to
schema/v0.1.0.json and deletes schema_v0.py, and the
producer-conformance test is added and lands green there.

#### fix/contract-schema-reconciliation

Status: complete (2026-06-10).
Pre-flight tightening of v0.1.0 schema, manifest contract doc, and
conformance inventory.
See CHANGELOG entry under 2026-06-10 for the full summary.

#### tst/conformance-harness

Status: complete (2026-06-17).
Conformance fixture directory structure, schema-layer harness, and
minimal valid fixture.
See CHANGELOG entry under 2026-06-17 for the full summary.

#### tst/conformance-valid-fixtures

Status: complete (2026-06-17).
Five valid fixtures completing the required inventory.
See CHANGELOG entry under 2026-06-17 for the full summary.

Verification at PR close: `uv run pytest test/` green; harness
test reports six passing valid fixtures (minimal from
tst/conformance-harness plus the five added here).

#### tst/conformance-invalid-path-rules

Status: complete (2026-06-17).
Seven schema-layer invalid fixtures covering path-rule violations.
See CHANGELOG entry under 2026-06-17 for the full summary.

#### tst/conformance-invalid-misc-rules

Status: complete (2026-06-18).
Seven schema-layer invalid fixtures completing the invalid category.
See CHANGELOG entry under 2026-06-18 for the full summary.

#### tst/conformance-invalid-impl-layer

Status: complete (2026-06-17).
Two impl-layer fixtures driving normpic/util/manifest_validate.py
into existence.
See CHANGELOG entry under 2026-06-17 for the full summary.

#### tst/conformance-consumer-lenient

Status: complete (2026-06-17).
Consumer-lenient fixture and consumer_normalize harness function.
See CHANGELOG entry under 2026-06-17 for the full summary.

#### fix/schema-not-pattern-typeguard

Fix the vacuous not-pattern construction in schema/v0.1.0.json.
The not:{pattern} clauses on relative_path, collection_root, and
original_filename fire vacuously on non-string values, because
pattern is string-only, so not of a vacuously-true pattern is
false.
A null is therefore rejected with misattributed path-separator
errors instead of a clean type error, and the idiom would silently
reject null if reused on a nullable field.

Canonical schema only; no production code, since the producer does
not yet validate against this file (see Schema source of truth).

Commits:

- Fix: type-guard string-content constraints in v0.1.0 schema.
  One TDD cycle.
  Rewrite the three defs so string-content rules apply only to
  strings: a positive pattern where simple (original_filename), an
  if:{type:string} guard around the existing not-pattern set where
  complex (relative_path, collection_root).
  RED: null-for-non-nullable-optional.json yields three errors
  including path-separator misattribution.
  GREEN: one error attributed to type.
  Full suite stays green; no accept/reject verdict changes.
- Doc: PR close per discipline preamble.
  Note in manifest-contract.md that string-content constraints
  must be type-guarded so they never vacuously reject non-strings,
  so the model refactors do not reintroduce a bare not:{pattern}.

Verification: uv run pytest test/ green; the null fixture rejects
with a single type-attributed error.

#### ref/pic-model-v01-contract

Align the Pic model representation in `normpic/model/pic.py` with
the v0.1 contract pic-object fields.
Adds the new `original_filename` field, brings nullability and
types into line with the contract, removes any pre-hiatus fields
that escaped ref/field-name-reconciliation, and updates
`test/unit/test_models.py` in lockstep.

Files touched: `normpic/model/pic.py`,
`normpic/model/__init__.py` if Pic is re-exported there,
`test/unit/test_models.py`.

Pic fields per the v0.1 contract (full semantic detail in
`doc/architecture/manifest-contract.md`):

- `hash`: string in `b2b120:` form, required.
- `relative_path`: string, required.
- `original_filename`: string with no `/` or `\`, optional and
  non-nullable.
- `size_bytes`: non-negative integer, required.
- `mtime`: string in RFC 3339 UTC, required.
- `timestamp`: string in RFC 3339 UTC, optional and nullable.
- `timestamp_source`: enum string, optional and nullable.
  Enum values: `"exif"`, `"filename"`, `"filesystem"`, `"unknown"`.
- `camera`: string, optional and nullable.
- `gps`: object with shape `{lat, lon}`, optional and nullable.
  Range: lat in `[-90, 90]`, lon in `[-180, 180]`.
- `tag`: array of strings, optional.

Commits:

Deferred from ref/field-name-reconciliation:

- [ ] Drop Pic.errors (per-pic error list; not in v0.1 contract).
  Files: normpic/model/pic.py, normpic/model/schema_v0.py,
  normpic/serializer/manifest.py, test/unit/test_models.py,
  test/unit/test_schema.py, test/unit/test_serializer.py,
  test/unit/test_error_handling.py,
  test/integration/test_manifest_loading_workflow.py
- [ ] Resolve Pic.source_path: not a rename of relative_path;
  relative_path is computed by stripping collection_root from
  the source path.
  Files: normpic/model/pic.py, normpic/model/schema_v0.py,
  normpic/serializer/manifest.py, test/unit/test_models.py,
  test/unit/test_schema.py, test/unit/test_serializer.py,
  test/integration/test_manifest_loading_workflow.py
- [ ] Resolve Pic.dest_path: operational state, no v0.1 mapping.
  Decide between removing from serialization or keeping as a
  non-serialized internal attribute.
  Files: normpic/model/pic.py, normpic/model/schema_v0.py,
  normpic/serializer/manifest.py, test/unit/test_models.py,
  test/unit/test_schema.py, test/unit/test_serializer.py,
  test/integration/test_manifest_loading_workflow.py,
  test/integration/test_exif_filename_workflow.py,
  test/integration/test_photo_organization_workflow.py

- `Ft: add original_filename field to Pic model`.
  One TDD cycle.
  Test: construct a Pic with `original_filename` set, with it
  absent, and verify that `None` and the empty string are rejected
  at construction time (per the contract's optional and
  non-nullable semantics).
  Implementation: add the field with an absent-sentinel that the
  serializer can distinguish from explicit `None`.
- `Ref: align remaining Pic fields with v0.1 contract`.
  Nullability and type adjustments for the other fields surfaced
  by the audit, plus `test_models.py` updates in lockstep.
  Skip this commit if ref/field-name-reconciliation already
  cleared everything and only `original_filename` needed adding.
- `Doc: PR close per discipline preamble`.

Verification at PR close: `uv run pytest test/unit/test_models.py`
green; Pic round-trips through construction with every field
configuration in the list above exercised at least once.

#### ref/manifest-model-v01-contract

Align the Manifest top-level model representation in
`normpic/model/manifest.py` and `normpic/model/schema_v0.py` with
the v0.1 contract.
Adds the new `version` and `collection_root` fields, removes
diagnostics from the manifest model (runtime logs only per the
contract), brings nullability into line with the contract, and
rewrites `test/unit/test_schema.py` against the new structure
(test failures here were deferred from
fix/contract-schema-reconciliation).

Files touched: `normpic/model/manifest.py`,
`normpic/model/schema_v0.py`, `normpic/model/__init__.py` if
re-exports change, `test/unit/test_schema.py`,
`test/unit/test_models.py` if it covers Manifest construction.

Manifest top-level fields per the v0.1 contract:

- `version`: string in semver-shape, required.
  Producer emits the schema version it implements (currently
  `"0.1.0"`).
- `collection_name`: non-empty string, required.
- `collection_description`: non-empty string, optional and
  nullable.
- `generated_at`: string in RFC 3339 UTC, required.
- `config`: object, optional and nullable.
  Shape intentionally loose in v0.x; consumers MUST NOT depend on
  its contents.
- `collection_root`: string, optional with default `"."`.
  Resolution rules in the contract; the always-emit-default
  serialization behavior lives in ref/serializer-v01-contract,
  not here.
- `pic`: array of Pic objects, required.

Diagnostics fields from the pre-hiatus contract are removed.
Diagnostics are runtime logs only and do not appear in the
manifest.

Deferred from ref/field-name-reconciliation:

- [ ] Drop Manifest.errors (global error list; not in v0.1 contract).
  Files: normpic/model/manifest.py, normpic/model/schema_v0.py,
  normpic/serializer/manifest.py, normpic/util/error_handling.py,
  test/unit/test_error_handling.py, test/unit/test_schema.py,
  test/unit/test_serializer.py,
  test/integration/test_manifest_loading_workflow.py
- [ ] Drop Manifest.warnings.
  Files: normpic/model/manifest.py, normpic/model/schema_v0.py,
  normpic/serializer/manifest.py
- [ ] Drop Manifest.processing_status.
  Files: normpic/model/manifest.py, normpic/model/schema_v0.py,
  normpic/serializer/manifest.py, normpic/manager/photo_manager.py

Commits:

- `Ft: add version and collection_root fields to Manifest model`.
  One TDD cycle covering both adds.
  Test: construct a Manifest with explicit `version` and
  `collection_root`, then with both at their defaults (`"0.1.0"`
  and `"."`); verify both attributes are accessible.
  Implementation: add the two fields with the documented defaults.
- `Ref: remove diagnostics and align remaining Manifest fields with
  v0.1 contract`.
  Drop any diagnostics-related attribute, helper, or doc reference
  from the model.
  Adjust nullability for `collection_description` and `config` to
  match the contract.
  Update `test_schema.py` in lockstep so tests stay green.
- `Doc: PR close per discipline preamble`.

Verification at PR close: `uv run pytest test/unit/test_schema.py
test/unit/test_models.py` green; the test failures deferred from
fix/contract-schema-reconciliation are now resolved.

#### ref/serializer-v01-contract

Align the manifest serializer at `normpic/serializer/manifest.py`
with the v0.1 contract's producer rules.
Implements always-emit `collection_root` with default `"."`, drops
diagnostics emission, honors canonical forms on emit, and enforces
byte-identical determinism over repeated runs of the same input.

Files touched: `normpic/serializer/manifest.py`,
`test/unit/test_serializer.py`, and any
`test/integration/test_*_workflow.py` files whose golden output
strings change due to the new emit rules.

Serializer obligations per the v0.1 contract:

- `version` and all required fields emitted on every manifest.
- `collection_root` always emitted, including the literal `"."` in
  the default case.
- Hashes emitted with the `b2b120:` prefix in uppercase Crockford,
  unchanged from the producer's input (the hash module from
  ft/hash-blake2b-crockford already returns canonical form).
- Optional + nullable fields: producer prefers absence over
  explicit `null` for unset values.
  No `null` literal in the JSON output for these fields.
- Optional arrays: producer prefers absence over `[]` for unset
  arrays.
  No empty `tag` arrays in the JSON output.
- Canonical forms on emit: UTF-8 without BOM, forward-slash paths
  only, RFC 3339 UTC timestamps with mandatory `Z` suffix, NFC
  Unicode normalization on `relative_path`.
- Byte-identical determinism: the same input produces a
  byte-identical manifest, including pic ordering, across repeated
  runs.
- Diagnostics not emitted (now logs-only per contract).

Commits:

- `Ref: align serializer field-presence with v0.1 contract`.
  Always-emit `collection_root` including default, drop
  diagnostics emission, and prefer absence over `null` or `[]` for
  optional fields and arrays.
  `test_serializer.py` updated in lockstep.
- `Ref: serializer enforces canonical forms and determinism on
  emit`.
  NFC normalization of `relative_path` on emit, RFC 3339 UTC with
  `Z` suffix verified, UTF-8 without BOM, deterministic key order,
  no trailing whitespace differences across runs.
  A determinism test that serializes the same model twice and
  asserts byte-identical output anchors the cycle.
- Ref: cut serializer validation over to the canonical schema.
  Load schema/v0.1.0.json and validate against it on both
  serialize and deserialize; remove the schema_v0.MANIFEST_SCHEMA
  import and use; delete the schema_v0.py dicts (whole module if
  nothing else imports it).
  Add a producer-conformance test: build a contract-shaped
  Manifest, serialize, and assert the output validates against
  schema/v0.1.0.json.
  Depends on ref/pic-model and ref/manifest-model landing first so
  the emitted manifest validates clean.
- `Doc: PR close per discipline preamble`.

Verification at PR close: `uv run pytest
test/unit/test_serializer.py test/integration/` green; the
determinism test asserts byte-identical output across repeated
serializations of the same model.

#### ref/manifest-manager-v01-contract

Wire the v0.1 contract through
`normpic/manager/manifest_manager.py`.
Rewrites the manager's unit tests and the manifest-loading
integration workflow test, then exercises the wedding-archive
end-to-end run as the closing acceptance for Phase B.
This is the first exercise of the wedding-acceptance line from
Phase D.

Files touched: `normpic/manager/manifest_manager.py`,
`test/unit/test_manifest_manager.py`,
`test/integration/test_manifest_loading_workflow.py`,
any call sites in `normpic/cli/` if their manager API contract
changed.

What the manager must do by this PR's end:

- Construct Manifest and Pic models per the v0.1 contract.
- Compute pic hashes via the `b2b120_hash` function from
  ft/hash-blake2b-crockford.
- Emit manifests via the serializer from
  ref/serializer-v01-contract, which honors all contract producer
  rules.
- Apply the implementation-layer validators from
  tst/conformance-invalid-impl-layer at the write boundary so
  invalid manifests cannot be persisted.
- Read existing manifests, validating with both schema-layer and
  implementation-layer checks before operating on their contents.

Commits:

- `Ref: align manifest manager with v0.1 contract`.
  Update the manager's construction, write, and read paths to use
  the new model, serializer, and hash function.
  Update `test_manifest_manager.py` in lockstep.
- `Ref: rewrite manifest-loading integration workflow for v0.1`.
  Rewrite `test_manifest_loading_workflow.py` against the new
  contract: new field names, new hash format, new emit rules.
  Round-trip integration: load a v0.1 manifest fixture, validate
  through both layers, modify a field, write back, re-read, and
  verify the manifest matches the expected v0.1-shaped output.
  Fold into the previous commit if changes are minor and the
  lockstep update is not bloated.
- `Doc: PR close per discipline preamble`.
  Includes the wedding-archive end-to-end dogfood result in the
  PR-summary block: manifest emitted successfully, schema-valid,
  implementation-valid, expected pic count and shape.

Verification at PR close: `uv run pytest test/` green; the wedding
archive produces a valid v0.1.0 manifest end-to-end, exercising
the wedding-acceptance line for the first time.
Phase D may rerun this as part of broader verification (Galleria
consumption etc.).

### Phase C: Documentation Downstream of Contract

Triggered by Phase A merged; parallelizable with Phase B.

- [ ] Update `modules/manifest.md` examples to the new contract.
- [ ] Update `guides/manifest-integration.md`.
- [ ] Update `guides/gallery-builder-integration.md`.
- [ ] Update `modules/schema.md` to document `schema/v0.1.0.json`
      as the single schema artifact the producer loads and
      validates against; remove any reference to the deleted
      `schema_v0.py` code module.
- [ ] Update `architecture/data-models.md` to point at
      `manifest-contract.md` as the source of truth, dropping the
      parallel code-schema framing; the canonical
      `schema/v0.1.0.json` is the only schema.
- [ ] Flip `architecture/schema-versioning.md` to "load
      `schema/v{version}.json`" instead of the
      code-dict-per-version approach; `schema_v0.py` is deleted.

### Phase D: Verification

Triggered by Phase B and Phase C merged.

- [ ] Bootstrap root `Justfile` per project convention.
  Task aliases for `uv run pytest`, `uv run ruff check`, schema
  check, etc.
  Deferred until manifest is ready for galleria consumption.
- [ ] All Python tests pass against the new contract.
- [ ] Conformance fixtures pass against the Python implementation,
      with the layer (schema or implementation) catching each
      invalid case matching `architecture/conformance.md`.
- [ ] Producer-conformance: every emitted manifest validates
      against `schema/v0.1.0.json`, with no separate code schema in
      the validation path.
- [ ] Wedding archive processes successfully end-to-end.
- [ ] Galleria consumes a v0.1.0 manifest and produces a working
      gallery.

### Phase E: Cleanup and Release

Triggered by Phase D verified.

- [ ] Pre-extraction sweep, planned into its own PR with
      verifications.
      normpic is extracted to its own repository; confirm and remove
      `deleteme-normpic-modules/` and any stale code or artifacts,
      then run the full quality gate green.
      Coordinate with chr/pyright-clean so stale-code deletions are
      not claimed twice.
- [ ] Final stale-content sweep across all docs.
- [ ] v0.1.0 stable release tag and `CHANGELOG.md` entry.
- [ ] Confirm "Decide before v0.1 ships" list is empty.

## Wedding Gallery Acceptance

The real-world driver for v0.1.0.

Final acceptance: wedding manifest produced from the source archive,
Galleria renders it, gallery deployed on a subdomain accessible to
Marcus and Christine.

## MVP Scope Decision: Compressed Variant Collections

The current planned consumer (galleria, for the wedding archive)
will serve originals that can be very heavy.
Showing originals by default for casual browsing is bandwidth-heavy
and slow.

The feature in concept: NormPic produces (or accepts as input) a
compressed copy of the collection, of theoretically any name,
sitting alongside the original collection.
Galleries render the lightweight variant by default and serve
originals only on explicit request.

This is parked as a v0.1 open question rather than a roadmap item.
The ongoing wedding gallery work, as it progresses toward MVP,
will make clear whether compressed variants are a launch blocker or
can defer to v0.2.
File-size impact and load performance under realistic conditions
are what flip the decision.

If it lands in v0.1, two design constraints apply:

- ergonomic handling needs real planning.
  How variants are addressed, how a consumer knows which variant to
  use, and how producers indicate variant relationships are open
  questions.
- the design should impose minimal change on the manifest schema.
  Treating variants as separate sibling collections each with their
  own manifest is one approach; a contract extension adding a
  variant-pointer field is another; there may be cleaner
  approaches.

If it rolls to v0.2, the placeholder entry already exists in
[ROADMAP.md](ROADMAP.md) under Implementation-Side Enhancements.

## Post-v0.1 Roadmap

See [ROADMAP.md](ROADMAP.md) for v0.x extensions, implementation-side
enhancements, Rust rewrite plans, remote adapters, and long-term
speculation.

## Integration Points

### For Galleria (gallery builder)

- Consumes v0.1.0 manifests per `architecture/manifest-contract.md`.
- Standardized filenames and content-addressed identity enable
  consistent URLs.
- Schema validation ensures compatibility.

### For Parent Site Project (personal-site)

- Orchestrates NormPic and Galleria.
- composer / marcustack handles git-hook-triggered runs.
- Manifest enables incremental builds.

### For 11ty Plugin (anticipated, post-Rust-port)

- Consumes the v0.1.0 contract through the WASM-compiled core.
- The implementation-agnostic manifest contract is the seam that
  makes this plugin path viable.

## Development Rules

Superseded by [doc/CONTRIBUTE.md](CONTRIBUTE.md), which is the source
of truth for TDD, the quality gate, commits, QA, and documentation
discipline.

Domain rules specific to normpic's behavior, not covered there:

- Lazy processing by default: skip unchanged pics.
- Warnings continue; errors stop.
