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

Resolved (not a manifest-contract item): persistence of operation
parameters and the source-to-copy derivation link belongs to
marcustack as invocation config, not to normpic and not to either
manifest.
Manifests stay contract-pure and describe only their own
collection.
For MVP, the symlink-copy operation is specified per run via CLI
args or env vars.
A post-MVP normpic config feature is deferred; see the post-v0.1
roadmap note.

The list shrinks to zero before v0.1.0 is published.

## Sequenced Tasks to Ship v0.1.0

Each task carries an explicit upstream trigger so a developer
picking this up knows what to do and when.

### Phase B: Implementation Alignment

Triggered by Phase A planning artifacts merged.

Phase B is sequenced as 18 PRs (expanded from 14: the
manifest-manager work split into a parallel-build-then-cutover
sequence once the two-manifest model was settled).
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
- ref/pic-model-v01-contract **complete**
- ref/manifest-model-v01-contract **complete**
- ft/source-manifest-read
- ft/hash-keyed-reprocessing
- ref/copy-manifest-contract-fields **complete**
- ref/symlink-reconcile-by-hash **complete**
- ref/drop-source-dest-cutover
- ref/serializer-v01-contract
- chr/pyright-clean (end of Phase B; see body below)

Ordering note: the canonical-schema cutover (point serializer
validation at schema/v0.1.0.json, delete schema_v0.py) lands in
ref/drop-source-dest-cutover, the PR that removes
source_path/dest_path -- the first point producer output
validates clean against the canonical schema.
ref/serializer-v01-contract no longer carries a schema-source
dependency and may sit anywhere after the model PRs.
The deferred Pic.errors / source_path / dest_path drops land in
ref/drop-source-dest-cutover, not in the model PRs.

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
  strings: a positive pattern where simple (original_filename),
  an if:{type:string} guard around the existing not-pattern set
  where complex (relative_path, collection_root).
  RED: null-for-non-nullable-optional.json yields three errors
  including path-separator misattribution.
  GREEN: one error attributed to type.
  Full suite stays green; no accept/reject verdict changes.
- Doc: PR close per discipline preamble.
  Note in manifest-contract.md that string-content constraints
  must be type-guarded so they never vacuously reject
  non-strings, so the model refactors do not reintroduce a bare
  not:{pattern}.

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

Deferred from ref/field-name-reconciliation.
These three now resolve in ref/drop-source-dest-cutover (the
cutover PR of the manifest-manager sequence), where source_path
and dest_path leave serialization and Pic.errors is dropped.
Resolution settled: dest_path is not persisted; it is recomputable
at runtime from the deterministic rename heuristic, so it is
neither serialized nor kept as a model field.

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
  Removed from serialization and not kept as a model field;
  recomputed at runtime per the resolution noted above.
  Files: normpic/model/pic.py, normpic/model/schema_v0.py,
  normpic/serializer/manifest.py, test/unit/test_models.py,
  test/unit/test_schema.py, test/unit/test_serializer.py,
  test/integration/test_manifest_loading_workflow.py,
  test/integration/test_exif_filename_workflow.py,
  test/integration/test_photo_organization_workflow.py

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
- `Doc: PR close per discipline preamble`.

Verification at PR close: `uv run pytest
test/unit/test_serializer.py test/integration/` green; the
determinism test asserts byte-identical output across repeated
serializations of the same model.

#### ft/source-manifest-read

First of the manifest-manager parallel-build sequence.
normpic reads the source collection's own manifest when present,
and creates it by scanning source_dir when absent.
This adds the capability only; nothing consumes the source manifest
for reprocessing yet, and the existing source_path-keyed
incremental path continues to run unchanged.

Files touched: `normpic/manager/photo_manager.py`,
`normpic/manager/manifest_manager.py`,
`test/unit/test_manifest_manager.py`,
`test/integration/test_manifest_loading_workflow.py`.

What must be true by this PR's end:

- normpic locates the source manifest at the source collection
  (manifest beside the source photos, contract default
  collection_root ".").
- If present, it is read and validated through schema-layer and
  implementation-layer checks before use.
- If absent, normpic scans source_dir and writes a contract-shaped
  source manifest.
- The existing dest-side single-manifest reprocessing path is
  untouched and green.

Commits:

- `Ft: read or create source collection manifest`.
  Add the source-manifest read/create path; unit-test present and
  absent cases.
- `Doc: PR close per discipline preamble`.

Verification at PR close: `uv run pytest test/` green; source
manifest is read when present and created when absent, old path
unchanged.

#### ft/hash-keyed-reprocessing

Add change detection keyed by the b2b120 hash, matching source
photos against the source manifest by content identity rather than
by source path.
Runs alongside the existing source_path-keyed match; the new path
is asserted equivalent to the old over the same inputs.
No removal in this PR.

Files touched: `normpic/manager/photo_manager.py`,
`normpic/manager/manifest_manager.py`,
`test/unit/test_manifest_manager.py`.

What must be true by this PR's end:

- A hash-keyed lookup matches each source photo to its source
  manifest entry by b2b120 hash.
- Change detection (new, changed, unchanged) is computed from the
  hash-keyed match.
- A test asserts the hash-keyed result agrees with the existing
  source_path-keyed result on a shared fixture, proving
  equivalence before cutover.

Commits:

- `Ft: add hash-keyed reprocessing match`.
  Implement the hash-keyed lookup and change detection alongside
  the existing path; add the equivalence test.
- `Doc: PR close per discipline preamble`.

Verification at PR close: `uv run pytest test/` green; hash-keyed
and source_path-keyed change detection agree on the fixture.

#### ref/copy-manifest-contract-fields

Status: complete (2026-06-30).
Copy manifest populated with relative_path in canonical form;
source_path/dest_path still emitted; parked hash index relocated.
See CHANGELOG entry under 2026-06-30 for the full summary.

#### ref/symlink-reconcile-by-hash

Switch symlink creation to reconcile the source and copy manifests
by hash at runtime, computing the transient source and dest paths
from the two manifests instead of reading stored source_path and
dest_path off pics.
The dest filename is recomputable from the deterministic heuristic;
the source location resolves from the source manifest via the
contract resolution algorithm (manifest dir + collection_root +
relative_path).

Files touched: `normpic/manager/photo_manager.py`,
`test/unit/test_manifest_manager.py`,
`test/integration/test_photo_organization_workflow.py`.

What must be true by this PR's end:

- Symlink creation derives each (source, dest) pair by matching the
  two manifests on b2b120 hash, at runtime.
- No symlink path is read from a stored source_path or dest_path
  field.
- The duplicated burst-counter filename loop in _create_ordered_pics
  is collapsed to a single computation while here.

Commits:

- `Ref: reconcile symlink paths by hash at runtime`.
  Replace stored-field path use with hash reconciliation; collapse
  the duplicate counter loop; update tests.
- `Doc: PR close per discipline preamble`.

Verification at PR close: `uv run pytest test/` green; symlinks are
created from runtime hash reconciliation, not stored paths.

#### ref/drop-source-dest-cutover

The cutover.
Remove source_path and dest_path from the Pic model and from
serialization, delete the old source_path-keyed reprocessing path,
and drop the deferred Pic.errors field.
After this PR the copy manifest is fully contract-pure and the old
single-manifest behavior is gone.
The wedding-archive end-to-end run is the Phase B acceptance gate
and lands here.

Files touched: `normpic/model/pic.py`,
`normpic/model/schema_v0.py`,
`normpic/serializer/manifest.py`,
`normpic/manager/photo_manager.py`,
`test/unit/test_models.py`, `test/unit/test_serializer.py`,
`test/unit/test_schema.py`,
`test/integration/test_manifest_loading_workflow.py`,
`test/integration/test_photo_organization_workflow.py`,
`test/integration/test_exif_filename_workflow.py`.

What must be true by this PR's end:

- Pic no longer defines or serializes source_path, dest_path, or
  errors.
- schema_v0.py PIC_SCHEMA no longer lists the dropped fields.
- The source_path-keyed reprocessing path is deleted; hash-keyed
  reprocessing is the only path.
- The deferred TODO boxes (Pic.errors, Pic.source_path,
  Pic.dest_path under ref/pic-model) are resolved and removed here.
- serializer.validate/deserialize run against schema/v0.1.0.json
  loaded from disk, not against schema_v0.MANIFEST_SCHEMA.
- schema_v0.py is deleted entirely (no remaining importers;
  test_schema.py retargeted at the canonical schema).

Commits:

- `Ref: drop source_path, dest_path, errors from Pic and cut over`.
  Remove the fields and the legacy reprocessing path; update all
  tests.
- `Ref: cut serializer validation to canonical schema`.
  Load schema/v0.1.0.json and validate against it on serialize
  and deserialize; remove the schema_v0.MANIFEST_SCHEMA import;
  delete schema_v0.py; retarget test_schema.py at the canonical
  schema.  Add a producer-conformance test: build a
  contract-shaped Manifest, serialize, assert the output
  validates against schema/v0.1.0.json.  This is the only point
  producer output validates clean against canonical, because
  source_path/dest_path are gone as of the prior commit.
- `Doc: PR close per discipline preamble`.
  Include the wedding-archive end-to-end result in the summary:
  manifest emitted, schema-valid, implementation-valid, expected
  pic count and shape.

Verification at PR close: `uv run pytest test/` green; the wedding
archive produces a valid v0.1.0 copy manifest end-to-end via
hash-reconciled symlinks, with no source_path/dest_path/errors in
the output.
This is the Phase B acceptance gate.

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

Deferred feature, needs a planning pass before it is scheduled:
normpic operation config.
A persisted config describing a symlink-copy operation (source and
copy manifest locations, the rename heuristic, the derivation link
between source and copy) so the operation need not be fully
re-specified via CLI or env each run.
Open question for that pass: the boundary between this config and
marcustack's invocation config, since marcustack owns operation
composition for the ecosystem.
Resolved for now: the relationship lives in marcustack and normpic
takes CLI/env per run; this item only revisits whether normpic
should also own a local config later.
Decide where this belongs (normpic vs marcustack) and at what
version before adding it to the roadmap proper.

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
