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

### Phase A: Planning Artifacts

- [x] Define manifest contract:
      `architecture/manifest-contract.md`.
- [x] Define conformance requirement:
      `architecture/conformance.md`.
- [x] Update `architecture/README.md` with the manifest-contract
      reference.
- [x] Update `architecture/README.md` to add the
      conformance-requirement reference.
- [x] Update planning docs: this TODO, `README.md`, top `README.md`,
      `CHANGELOG.md`, `ROADMAP.md` (initial v0.1 planning PR).
- [x] Create `schema/v0.1.0.json` (machine-readable schema artifact).
- [x] Split or expand `architecture/schema-versioning.md` to
      distinguish implementation migration from consumer-facing
      contract stability.

### Phase B: Implementation Alignment

Triggered by Phase A planning artifacts merged.

- [ ] Field-name reconciliation audit.
      Own PR, early task.
      Identify any pre-hiatus field names still in the codebase and
      align them to the contract.
- [ ] Build conformance fixtures per
      `architecture/conformance.md`, one fixture at a time per
      project TDD discipline.
      Each fixture drives the implementation work that makes it
      pass.
      Full inventory coverage required before Phase D.
- [ ] Update `normpic/model/schema_v0.py` to encode the new contract.
- [ ] Update hash module: SHA-256 to BLAKE2b-120 with Crockford
      Base32 and `b2b120:` prefix.
- [ ] Implement strict `relative_path` semantics (relative-only, no
      `./`, no `..`, no aliasing).
- [ ] Implement `collection_root` field with explicit-default
      emission (`"."` when manifest sits at collection root).
- [ ] Add `original_filename` field.
- [ ] Remove diagnostics from manifest (logs-only at runtime).
- [ ] Reject `null` for non-nullable optionals (validation).
- [ ] Reject empty strings for required string fields (validation).
- [ ] Validate GPS coordinate ranges (`-90 <= lat <= 90`,
      `-180 <= lon <= 180`).
- [ ] Update test fixtures to the new contract.
- [ ] Update integration tests to validate against the new schema.

### Phase C: Documentation Downstream of Contract

Triggered by Phase A merged; parallelizable with Phase B.

- [ ] Update `modules/manifest.md` examples to the new contract.
- [ ] Update `guides/manifest-integration.md`.
- [ ] Update `guides/gallery-builder-integration.md`.
- [ ] Update `modules/schema.md`.
- [ ] Update `architecture/data-models.md` to point at
      `manifest-contract.md` as the source of truth and retain its
      role as the Python-implementation companion.

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
- [ ] Wedding archive processes successfully end-to-end.
- [ ] Galleria consumes a v0.1.0 manifest and produces a working
      gallery.

### Phase E: Cleanup and Release

Triggered by Phase D verified.

- [ ] Remove `deleteme-normpic-modules/`.
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

1. TDD: Write integration test -> fail -> write unit tests ->
   implement -> green -> refactor.
2. No commits without passing tests (except checkpoint branches:
   `Chk: [description]`).
3. All code must pass ruff checks.
4. Use mocked filesystem in tests.
5. Lazy processing by default (skip unchanged pics).
6. Warnings continue, errors stop.
7. JSON Schema validation for all manifest operations.
8. Update documentation with every commit.
9. Log changes in `CHANGELOG.md` daily.
10. Documentation discipline: any new doc gets a reference and
    summary added to its peer `README.md`.
    Keep `manifest-contract.md` and its peer-README index in sync.
11. Reference and adapt useful specs from
    `deleteme-normpic-modules/`; delete obsolete content there as it
    is replaced (full directory removal in Phase E).
