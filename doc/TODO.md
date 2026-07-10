# NormPic - v0.1 Contract Alignment TODO

## Current Status: v0.1 contract frozen; Phase B complete

The v0.1 copy-manifest contract is frozen: relative_path-only pics,
hash-keyed reconciliation, canonical schema/v0.1.0.json enforced,
legacy source_path/dest_path/errors removed.
Verified end-to-end on the real wedding archive (645 pics, zero
dangling symlinks, canonical-valid).

Remaining to publish v0.1.0: chr/pyright-clean, then Phase C/D/E
(docs, verification, release).

Downstream, gated on v0.1.0 publishing: galleria binds its manifest
reader to the frozen contract, then marcustack (composer; live deploy
is the largest unexamined risk).

Post-v0.1 is contract-free and opportunistic: see ROADMAP.md.
The existing Python implementation reflects the pre-hiatus contract
and is being aligned to the new one.
The pre-hiatus "MVP complete" claim is subsumed by this larger v0.1
scope; existing tests were updated during Phase B (now complete).

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

The pre-hiatus field-name reconciliation item is resolved (Phase B
complete; see CHANGELOG 2026-06-10 through 2026-07-07).
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

Complete as of 2026-07-07. See CHANGELOG entries 2026-06-10 through
2026-07-07 for per-PR detail. Two items remain open:

#### ref/serializer-v01-contract

Align the manifest serializer at `normpic/serializer/manifest.py`
with the v0.1 contract's producer rules.
Implements always-emit `collection_root` with default `"."`, drops
diagnostics emission, honors canonical forms on emit, and enforces
byte-identical determinism over repeated runs of the same input.
The model and schema are already contract-shaped (see CHANGELOG
2026-06-23 through 2026-07-07); this PR closes the emit side.

Files touched: `normpic/serializer/manifest.py`,
`test/unit/test_serializer.py`, and any
`test/integration/test_*_workflow.py` files whose golden output
strings change due to the new emit rules.

Serializer obligations per the v0.1 contract:

- `version` and all required fields emitted on every manifest.
- `collection_root` always emitted, including the literal `"."` in
  the default case.
- Hashes emitted with the `b2b120:` prefix in uppercase Crockford,
  unchanged from the producer's input (the hash module already
  returns canonical form).
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

## Development Rules

Superseded by [doc/CONTRIBUTE.md](CONTRIBUTE.md), which is the source
of truth for TDD, the quality gate, commits, QA, and documentation
discipline.

Domain rules specific to normpic's behavior, not covered there:

- Lazy processing by default: skip unchanged pics.
- Warnings continue; errors stop.
