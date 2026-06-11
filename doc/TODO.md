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

### PR workflow

Each PR follows the same shape:

1. Branch from the current head.
   Branch and PR names use a lowercase prefix, a slash, and a
   kebab-case slug: `pln/`, `ft/`, `fix/`, `doc/`, `ref/`, `chr/`,
   plus `tst/` for test-only PRs.
   Examples: `tst/conformance-harness`,
   `ref/manifest-manager-v01-contract`.
2. Work in commits sized for review.
   Group changes by single concern; do not pile unrelated work
   into one commit.
3. Commit titles use a different convention than branch names.
   The enforced six prefixes only, with leading capital and a
   colon: `Pln:`, `Ft:`, `Fix:`, `Doc:`, `Ref:`, `Chr:`.
   The commit-msg hook will reject anything else.
   Commit bodies use bullet points with nested detail.
4. Reference other PRs by branch name, never by an ordinal like
   "PR 4."
   Ordinals are positional, lose meaning when the sequence shifts,
   and force the reader to count.
5. The final commit of every PR is the doc-update commit.
   It updates doc/TODO.md, doc/CHANGELOG.md, and any other
   documents affected by the PR's changes (module docs,
   architecture docs, integration guides).
6. Push and submit the PR for review.

### TDD cycle and commits

TDD is the default for any PR that produces behavior change.
RED-GREEN-REFACTOR is the workflow you follow at the keyboard, not
a sequence of commits.
Each commit captures a completed cycle: one test added, the
implementation that makes it pass, any refactor done in the same
sitting.
The RED moment is ephemeral; broken code is not committed.

One commit, one cycle, one behavior.
The commit prefix reflects what the commit ultimately delivers:
`Ft:` for new capability, `Fix:` for a bug, `Ref:` only when the
commit is pure refactor with no new test or behavior.

Group cycles by acceptance unit, not by category.
A rule's valid and invalid cases belong together because they test
the same boundary.
Splitting "all valid" from "all invalid" across two PRs forces a
reviewer to hold two PRs in mind to verify one rule.

One fixture per commit when building conformance fixtures, except
when several variants exercise the same rule, in which case group
by rule.
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

**CHANGELOG archival, pre-MVP.**
Before MVP ships, the current doc/CHANGELOG.md will be archived
(e.g. moved to doc/CHANGELOG-v0.1.md) and a fresh CHANGELOG.md
started.
Out of Phase B scope; flagged here so the discipline above is
sustainable until that archival lands.

### Style and format conventions

These apply to all in-repo prose: markdown, code comments,
docstrings, commit messages.

- Lines under 80 characters.
- ASCII only.
  No em dashes; use sentence breaks with periods instead.
- Sentence-ending punctuation (`.`, `!`, `?`) is always followed by
  a newline.
- Singular directory and field names by default: `doc/` not
  `docs/`, `test/` not `tests/`, `asset/` not `assets/`.
- Every new document gets a reference and one-line summary added
  to its peer `README.md`.
- README link convention: each directory level links only to peer
  markdown files at the same level or one level down to a
  subdirectory README, never deeper.

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

Phase B is sequenced as 13 PRs.
Each PR follows the Working Discipline preamble above.
The PRs in order:

- fix/contract-schema-reconciliation [complete]
- ref/field-name-reconciliation
- tst/conformance-harness
- tst/conformance-valid-fixtures
- tst/conformance-invalid-path-rules
- tst/conformance-invalid-misc-rules
- tst/conformance-invalid-impl-layer
- tst/conformance-consumer-lenient
- ft/hash-blake2b-crockford
- ref/pic-model-v01-contract
- ref/manifest-model-v01-contract
- ref/serializer-v01-contract
- ref/manifest-manager-v01-contract

#### fix/contract-schema-reconciliation

Status: complete (2026-06-10).
Pre-flight tightening of v0.1.0 schema, manifest contract doc, and
conformance inventory.
See CHANGELOG entry under 2026-06-10 for the full summary.

#### ref/field-name-reconciliation

Audit the codebase for pre-hiatus field names and align them to the
v0.1 contract.
Pure rename refactor, no behavior change.
Tests stay green after every commit (parallel-change pattern:
rename source and tests in the same commit).

Files touched: `normpic/model/`, `normpic/serializer/`,
`normpic/manager/`, `test/unit/`, `test/integration/`.

Commits:

- `Doc: field-name reconciliation audit findings`.
  Grep `normpic/` for field names used in manifest and pic
  structures.
  Grep `test/` for references.
  Compare against the v0.1 contract field list.
  Write findings to `doc/architecture/field-rename-audit.md` as a
  temporary working document.
  Each finding line: `old_name -> new_name, files: [list]`.
- `Ref: rename <old> to <new> across normpic and test`.
  One commit per logical rename group.
  Count determined by audit findings.
  If audit surfaces zero discrepancies, this commit set is empty.
- `Chr: drop field-rename-audit.md`.
  The audit doc is working scaffolding; once renames are done it
  has no readers.
- `Doc: PR close per discipline preamble`.

Verification at PR close: `uv run pytest test/` green.

#### tst/conformance-harness

Build the conformance test harness with the first valid fixture
(`minimal`).
Establish the directory structure and harness API that every later
fixture PR reuses.
Read `test/fixture/conformance/README.md` before designing the
harness; honor any existing spec there.

Files touched: `test/fixture/conformance/`, `test/unit/` (or
equivalent test home), `doc/test/conformance.md` (new),
`doc/test/README.md`.

Commits:

- `Chr: review existing test/fixture/conformance/README.md`.
  No-code commit.
  Read the README, confirm or revise harness design, note any
  constraints it imposes.
- `Ft: conformance harness with minimal valid fixture`.
  One TDD cycle.
  Test loads `valid/minimal.json` through a harness loader and
  validates it against `schema/v0.1.0.json` using `jsonschema`.
  Implementation creates
  `test/fixture/conformance/{valid,invalid,consumer-lenient}/`
  subdirectories, adds `valid/minimal.json` with required top-level
  fields only (empty pic array, `collection_root` `"."`), and
  implements the loader plus schema-validate function under
  `test/helpers/` or `test/conformance.py`.
- `Doc: add doc/test/conformance.md and reference in peer README`.
  New doc covering harness usage, fixture categories, two-layer
  model cross-reference to `architecture/conformance.md`, and how
  to add new fixtures.
  Update `doc/test/README.md` per doc discipline.
- `Doc: PR close per discipline preamble`.

Verification at PR close: `uv run pytest test/` green.

#### tst/conformance-valid-fixtures

Add the remaining five valid fixtures per
`architecture/conformance.md` inventory.
One TDD cycle per fixture: write the test that loads it through
the harness and validates against `schema/v0.1.0.json`, add the
fixture file, confirm green, refactor if warranted.

Files touched: `test/fixture/conformance/valid/`,
`test/unit/test_conformance.py`.

Commits:

- `Ft: conformance fixture, valid/full`.
  Every top-level and per-pic field populated, exercising every
  optional field including `tag`, `gps`, `timestamp_source`, and
  the loose `config` object.
- `Ft: conformance fixture, valid/collection-root-default`.
  `collection_root` set to the literal `"."` with at least one pic.
- `Ft: conformance fixture, valid/collection-root-traversal`.
  `collection_root` set to a path with leading `..` segments and
  no segments after the leading run.
- `Ft: conformance fixture, valid/empty-collection`.
  Zero pics with top-level optional fields populated.
- `Ft: conformance fixture, valid/optional-fields-null`.
  Every nullable optional field set explicitly to `null`.
- `Doc: PR close per discipline preamble`.

Verification at PR close: `uv run pytest test/` green; harness
test reports six passing valid fixtures (minimal from
tst/conformance-harness plus the five added here).

#### tst/conformance-invalid-path-rules

Add the seven invalid schema-layer fixtures covering path-rule
violations.
Grouped by field so each commit validates one rule family
end-to-end.

Files touched: `test/fixture/conformance/invalid/`,
`test/unit/test_conformance.py`.

Commits:

- `Ft: conformance fixtures, invalid relative_path forms`.
  Four fixtures asserting schema-layer rejection:
  - `invalid/relative-path-absolute.json` (leading `/`)
  - `invalid/relative-path-dot-segment.json`
  - `invalid/relative-path-dotdot-segment.json`
  - `invalid/relative-path-backslash.json`
- `Ft: conformance fixtures, invalid collection_root forms`.
  Two fixtures asserting schema-layer rejection:
  - `invalid/collection-root-leading-dotslash.json`
  - `invalid/collection-root-uri-scheme.json`
- `Ft: conformance fixture, invalid original_filename with path
  separator`.
  One fixture asserting schema-layer rejection:
  - `invalid/original-filename-path-separator.json`
- `Doc: PR close per discipline preamble`.

Each fixture's accompanying test asserts the schema rejects the
fixture and the rejection's error path points at the violated
field.

Verification at PR close: `uv run pytest test/` green; harness
test reports all seven invalid fixtures rejected by the schema
layer.

#### tst/conformance-invalid-misc-rules

Add the seven invalid schema-layer fixtures covering hash,
timestamp, range, and presence/type rule violations.
Grouped by rule family so each commit covers one boundary.

Files touched: `test/fixture/conformance/invalid/`,
`test/unit/test_conformance.py`.

Commits:

- `Ft: conformance fixtures, invalid hash forms`.
  Two fixtures asserting schema-layer rejection:
  - `invalid/hash-bad-prefix.json` (non-`b2b120:` prefix)
  - `invalid/hash-wrong-length.json` (wrong digest length after
    prefix)
- `Ft: conformance fixture, invalid timestamp offset form`.
  One fixture asserting schema-layer rejection:
  - `invalid/timestamp-offset-form.json` (`+00:00` instead of `Z`)
- `Ft: conformance fixture, invalid GPS latitude range`.
  One fixture asserting schema-layer rejection:
  - `invalid/gps-lat-out-of-range.json` (latitude outside -90..90)
- `Ft: conformance fixtures, invalid presence and string rules`.
  Three fixtures asserting schema-layer rejection:
  - `invalid/empty-required-string.json`
  - `invalid/null-for-non-nullable-optional.json`
  - `invalid/missing-required-field.json`
- `Doc: PR close per discipline preamble`.

Each fixture's accompanying test asserts schema rejection with the
error path pointing at the violated field.

Verification at PR close: `uv run pytest test/` green; harness
test reports all seven invalid-misc fixtures rejected by the
schema layer.

#### tst/conformance-invalid-impl-layer

Add the two invalid implementation-layer fixtures.
Each fixture passes schema validation but is rejected by the
implementation layer.
These fixtures drive the first implementation-layer validator code
into existence.

The harness from tst/conformance-harness extends here: alongside
the existing schema-validate function, add an
implementation-validate function that runs after schema validation
and applies layer-2 checks.

Files touched: `test/fixture/conformance/invalid/`,
`test/unit/test_conformance.py`, harness module from
tst/conformance-harness, and a new implementation-layer validator
module (surface its location during the cycle, likely
`normpic/util/manifest_validate.py` or under `normpic/model/`).

Commits:

- `Ft: conformance fixture, invalid collection_root with non-leading
  ..`.
  One TDD cycle.
  Test asserts schema accepts the fixture but implementation
  rejects it with an error identifying the non-leading `..`.
  Implementation adds a `collection_root` validator that checks
  `..` appears only in the leading run.
  Fixture: `invalid/collection-root-nonleading-dotdot.json`.
- `Ft: conformance fixture, invalid timestamp with bad calendar
  value`.
  One TDD cycle.
  Test asserts schema accepts the fixture but implementation
  rejects it via Python's datetime parser failing on an impossible
  calendar value (e.g. month 13).
  Implementation ensures the timestamp parser is invoked at
  validate time and surfaces a clear error.
  Fixture: `invalid/timestamp-bad-calendar.json` (well-formed
  pattern, invalid value).
- `Doc: PR close per discipline preamble`.

The implementation-layer validator module emerging from this PR is
the seam through which later PRs may add further rules that the
schema cannot express.

Verification at PR close: `uv run pytest test/` green; harness
test reports both fixtures schema-accepted and
implementation-rejected.

#### tst/conformance-consumer-lenient

Add the one consumer-lenient fixture (lowercase Crockford in
hash).
Drives the case-normalization-on-read code into existence.

The harness extends here once more: add a consumer-normalize
function that runs after layer-2 validation when reading a
consumer-lenient fixture, returning the normalized form for
downstream comparison.

Files touched: `test/fixture/conformance/consumer-lenient/`,
`test/unit/test_conformance.py`, harness module, and the hash
module (or a thin normalizer near it) for the case-folding logic.

Commits:

- `Ft: conformance fixture, lowercase Crockford hash with
  normalize`.
  One TDD cycle.
  Test asserts the schema rejects the lowercase form (per the
  schema pattern, which is uppercase-only), and the
  consumer-normalize path accepts after case-folding to canonical
  uppercase.
  Implementation adds a hash-case normalizer the consumer side
  calls on read.
  Fixture: `consumer-lenient/hash-lowercase-crockford.json`.
- `Doc: PR close per discipline preamble`.

This PR completes the conformance fixture inventory.
After it lands, every case in `architecture/conformance.md` has at
least one fixture and the harness exercises all three categories
(valid, invalid, consumer-lenient).

Verification at PR close: `uv run pytest test/` green; harness
test reports the full conformance inventory passing per layer
assignments.

#### ft/hash-blake2b-crockford

Replace SHA-256 with BLAKE2b-120 plus Crockford Base32 uppercase
canonical encoding plus the `b2b120:` prefix.
Producer-side hash format is established here.
Conformance fixtures from the earlier conformance PRs provide
ground-truth examples of the `b2b120:` string format the
implementation must agree with.

Files touched: the hash module (location surfaced during
ref/field-name-reconciliation), related tests in `test/unit/`,
producer call sites that compute pic hashes (likely the manifest
writer path).

##### Test vectors from depo

The depo project has a working BLAKE2b-120 + Crockford Base32
implementation with verified golden vectors.
Transfer these as contract inputs to the new function.
Each pair is `(input bytes, expected b2b120-prefixed output
string)`:

```
b""               -> b2b120:PZDRE6BC90T0BS0FGG0ZM7Y9
b"Hello, World!"  -> b2b120:D7GS0E632ZGYMQAVRXHYZ315
b"\xff"           -> b2b120:N07C0CD6R447SA6JT1CEVAWW
b"\x00" * 5       -> b2b120:DGGXXPQBAP0A56H3CJKG23P6
b"\x00" * 4099    -> b2b120:DCJF8WQMWPFWGA3ZTB62HJA2
b"\xaa" * 4099    -> b2b120:SXBV2Q0G5PZNCC60ED9AXGBZ
```

These cover empty (corner case), short ASCII, single byte
(boundary), repeated zero (internal state), large prime-length
input crossing BLAKE2b's 128-byte block boundary, and alternating
bit pattern.
Hash functions accept any byte input, so no negative cases are
needed.
Independent verification of the vectors uses depo's
`scripts/hash-b32.sh`.

Two additional vectors required for normpic, generated
independently via the same depo script:

```
b"abcdefghijklmno"  (exactly 15 bytes)  -> b2b120:<generated>
b"\x55"             (mid-value byte)     -> b2b120:<generated>
```

The depo encoder unit tests in
`depo/tests/util/test_shortcode.py::TestCrockfordEncode` are
available as a secondary reference if the dev chooses to extract
Crockford encoding as a separately testable helper function.
Optional, not required.

##### What is not transferable

depo's `canonicalize_code` solves a different problem (human-typed
shortcode UX with separator stripping and lookalike mapping).
Do NOT import its behavior into normpic; it would let
`O`/`I`/`L`/`U` map to digits, collapsing distinct contract-valid
strings.
normpic's consumer-side normalization is much narrower (case-fold
lowercase to uppercase only) and is built in
tst/conformance-consumer-lenient, not here.

##### Required prefix invariant test

depo does not use the `b2b120:` prefix; normpic adds an explicit
invariant test the depo suite does not have:

```python
def test_output_has_b2b120_prefix():
    """Every output begins with the literal 'b2b120:' prefix."""
    assert b2b120_hash(b"").startswith("b2b120:")
    assert b2b120_hash(b"any data").startswith("b2b120:")
```

##### Commits

- `Ft: BLAKE2b-120 hash with Crockford Base32 and b2b120: prefix`.
  One TDD cycle.
  Test set: the six depo vectors (prefix-adjusted) above, the two
  normpic-specific additional vectors, the prefix invariant test,
  and an alphabet-compliance assertion on the encoded suffix (no
  `I`, `L`, `O`, or `U`).
  Implementation: one function `b2b120_hash(data: bytes) -> str`
  wrapping `hashlib.blake2b(digest_size=15)`, an inline Crockford
  Base32 encoder (alphabet `0-9` plus `A-Z` minus
  `I`/`L`/`O`/`U`), and `b2b120:` prefix wrapping.
  No external Base32 library; Crockford is small enough to inline.
  Output length is always 31 chars (7-char prefix `b2b120:` plus
  24-char encoded 120-bit digest).
- `Ref: replace existing hash call sites with b2b120_hash`.
  Sweep call sites in `normpic/` that compute pic hashes.
  Update accompanying tests in lockstep so tests stay green:
  golden hashes in fixtures and test expectations move to the new
  format alongside the producing code.
  If the lockstep update is bloated across modules, split into
  multiple `Ref:` commits, one per module.
- `Doc: PR close per discipline preamble`.

Verification at PR close: `uv run pytest test/` green; conformance
fixtures containing `b2b120:` hashes validate end-to-end through
the implementation.

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
