# NormPic - v0.1 Contract Alignment TODO

## Current Status: v0.1 contract frozen; Phase B complete

The v0.1 copy-manifest contract is frozen: relative_path-only pics,
hash-keyed reconciliation, canonical schema/v0.1.0.json enforced,
legacy source_path/dest_path/errors removed.
Verified end-to-end on the real wedding archive (645 pics, zero
dangling symlinks, canonical-valid).

Remaining to publish v0.1.0: Phase C/D/E (docs, verification,
release). Phase B and chr/pyright-clean complete.

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

### Phase C: Documentation Downstream of Contract

Triggered by Phase A merged; parallelizable with Phase B.

- [ ] Update `modules/manifest.md` examples to the new contract.
- [ ] Update `guides/manifest-integration.md`.
- [ ] Update `guides/gallery-builder-integration.md`.
- [x] Purge all stale `schema_v0.py` references now that the single
      JSON schema is the sole cross-language source of truth.
      Affected: `modules/schema.md`, `architecture/schema-versioning.md`,
      `architecture/data-models.md`, `architecture/package-structure.md`,
      `architecture/README.md`.
      Point each at `schema/v0.1.0.json` as the artifact the producer
      loads and validates against.
- [x] Update `architecture/data-models.md` to point at
      `manifest-contract.md` as the source of truth, dropping the
      parallel code-schema framing; the canonical
      `schema/v0.1.0.json` is the only schema.
- [x] Flip `architecture/schema-versioning.md` to "load
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
