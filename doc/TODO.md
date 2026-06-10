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

This preamble defines the workflow and document-maintenance rules
that apply to every PR listed in Phase B below.
It exists so individual PR descriptions can stay focused on the
work and not repeat process rules.

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

### PR workflow

Each PR follows the same shape:

1. Branch from the current head with a kebab-case branch name
   matching the PR name (e.g. `Fix/contract-schema-reconciliation`).
2. Work in commits sized for review.
   Group changes by single concern; do not pile unrelated work
   into one commit.
3. Commit titles use the enforced prefix convention: `Pln:`, `Ft:`,
   `Fix:`, `Doc:`, `Ref:`, `Chr:`.
   The commit-msg hook will reject anything else.
   Commit bodies use bullet points with nested detail.
4. The final commit of every PR is the doc-update commit.
   It updates doc/TODO.md, doc/CHANGELOG.md, and any other
   documents affected by the PR's changes (module docs,
   architecture docs, integration guides).
5. Push and submit the PR for review.

### TDD cycle and commits

TDD is the default for any PR that produces behavior change.
Each RED-GREEN-REFACTOR cycle is one logical unit of work.
Cycle phases map to commit prefixes as follows:

- RED (failing test): `Ft:` when introducing a test for a new
  capability, `Fix:` when reproducing a bug.
  The commit message should make clear the test is expected to
  fail at this point and what the failure mode looks like.
- GREEN (minimal implementation): `Ft:` or `Fix:` as appropriate.
  Smallest implementation that turns the test green.
- REFACTOR (optional): `Ref:` for any cleanup that follows.
  Skip the commit if no refactor is warranted.

One fixture or one behavior per cycle.
No bulk generation.

### Document maintenance during a PR

Two documents need maintenance throughout: doc/TODO.md and
doc/CHANGELOG.md.
Both are already large and will grow.
Treat them as append-and-prune.

**Context warning.**
Never `cat` either file in full to make an edit.
Use targeted reads: `grep -n` to find the section, `sed -n A,Bp`
to view a few lines around it, then surgical edits with
`str_replace` or appending with `>>`.
Reading these files end-to-end on every commit burns context for
no benefit.

**Per-commit hygiene.**
After each commit, append one concise line to doc/CHANGELOG.md
under today's date header (create today's header if it does not
yet exist).
Mark the corresponding doc/TODO.md checkbox done in-place, but
do not delete the line yet.

**PR-close consolidation.**
The final doc-update commit of every PR rewrites the per-commit
CHANGELOG one-liners under today's date as one concise
PR-summary block, with the PR name as a sub-header.
Delete the granular one-liners that were just consolidated.
Then delete the now-complete task lines from doc/TODO.md so the
TODO does not balloon.

**Related-document updates.**
If a PR changes anything referenced by a module doc, an
architecture doc, or an integration guide, update those documents
in the same final doc-update commit.
Do not leave reference docs out of sync with the contract or the
implementation.

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
