# NormPic TODO

## Current Status: v0.2 planning

Post-v0.1 is contract-free and opportunistic: see ROADMAP.md.
We will be picking out good next items that are more self contained.
Eventually a picture of v0.2 will form.
Then we will pick out a sequence and remove ROADMAP items.
Those items will be given mechanistic details and
added to this TODO list.
Any contract change lands in
[architecture/manifest-contract.md](architecture/manifest-contract.md),
which holds the frozen v0.1 contract.

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

## Working Discipline

The workflow, planning, TDD, commit, QA, style, and
document-maintenance rules for every PR below live in
[doc/CONTRIBUTE.md](CONTRIBUTE.md).
That document is the source of truth for how work is done here.
This file does not restate those rules, so they cannot drift.

## Development rules

See [CONTRIBUTE.md](CONTRIBUTE.md) for TDD, the quality gate, commits,
QA, and documentation discipline.
Domain rules specific to normpic, not covered there:

- Lazy processing by default: skip unchanged pics.
- Warnings continue; errors stop.
