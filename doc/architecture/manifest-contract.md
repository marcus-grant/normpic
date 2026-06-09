# Manifest contract

## Overview

This document defines the v0.1.0 NormPic manifest contract: the durable
artifact that consumers and reimplementations depend on.

The audience is twofold.
First, implementers writing producers in any language (currently
Python, anticipated Rust, possibly others) who need to know what a
conformant manifest looks like.
Second, consumers (Galleria, future Static Site Generator plugins, and
other downstream tools) who need to know what they can rely on when
reading a manifest.

This document IS the source of truth for the manifest's fields,
semantics, expectations, and canonical forms.

This document is NOT Python-implementation guidance (see
`data-models.md` for the Python implementation's internal structure)
and is NOT implementation-side schema migration mechanics (see
`schema-versioning.md` for how the Python implementation handles
reading older schema-versioned modules).

The contract has two artifact layers, intentionally split:

- This document (`manifest-contract.md`): semantic equivalence rules,
  producer and consumer behavior, rationale, and forward-compatibility
  intent.
- The JSON Schema artifact at `schema/v0.1.0.json`: mechanically
  enforced validation rules.

Where the two overlap (field types, required-or-not, value ranges),
the JSON Schema is the operational source.
Where they do not overlap (semantic equivalence of absent and null,
producer style preferences, rationale), this document is the only
source.

Implementation-agnosticism is a primary design goal.
The contract is described in language that a developer working in any
modern language can implement without translation through Python
idioms.
The Rust port, hypothetical Go SSG plugins, and any future
implementations all read the same source.

## Status and versioning policy

v0.1.0 is pre-stable.
The contract is under active development through the v0.x line.

Versioning is semver-shaped (MAJOR.MINOR.PATCH) but interpreted at the
schema level, not at the implementation level.

### v0.x rules

Breaking changes are permitted at minor-version bumps (for example
0.1 to 0.2).
Patch bumps within a minor line (for example 0.1.0 to 0.1.1) are spec
clarifications only, with no behavioral change.

### v1.0 rules

v1.0 marks a locked stable contract.
Only additive changes are permitted within the v1.x line.
Backward compatibility is guaranteed within the v1 major line.

### The version field

The top-level `version` field is the discriminator for the contract
version a manifest was produced against.
Its semantics are fixed across all versions, even when other fields
change.

### Parse-time behavior

Consumer parsing rules:

- A consumer MUST refuse a manifest whose `version` major.minor it
  does not recognize.
- Within a recognized major.minor, a consumer MUST accept patch-level
  differences without behavioral change.
- Within a recognized major.minor, a consumer MUST accept manifests
  containing unknown optional fields.
  This is the forward-compatibility seam within a version line.

Producer parsing rules:

- A producer MUST emit a `version` matching the schema version it
  implements.

### Bump triggers

The following changes to the contract require a minor-version bump
within v0.x or a major-version bump within v1.x:

- Renaming any field.
- Removing any field.
- Changing the type of any field.
- Tightening any constraint such that previously valid manifests would
  become invalid.

Additive changes (introducing new optional fields, relaxing a
constraint, adding new enum values to existing enum-typed fields) are
patch-level within v0.x and minor-level within v1.x.

## Manifest schema

This section defines the manifest's shape: what fields exist, their
types, and their presence rules.
Semantics live in dedicated sections cross-referenced below.

The JSON Schema artifact at `schema/v0.1.0.json` is the mechanical
encoding of this schema.

### Top-level fields

- `version` (string, required): the schema version this manifest was
  produced against, for example `"0.1.0"`.
  Semantics in
  [Status and versioning policy](#status-and-versioning-policy).
- `collection_name` (string, required): human-readable name of the
  collection.
- `collection_description` (string, optional + nullable): free-text
  description of the collection.
  Null and absent rules in
  [Optional, nullable, absent semantics](#optional-nullable-absent-semantics).
- `generated_at` (string, required): timestamp the manifest was
  produced, in RFC 3339 UTC.
  Format in [Canonical forms](#canonical-forms).
- `config` (object, optional + nullable): producer invocation
  configuration.
  Shape intentionally loose in v0.x; consumers MUST NOT depend on its
  contents.
- `collection_root` (string, optional, default `"."`): location of the
  collection root relative to the manifest file's directory.
  The default value is emitted explicitly rather than omitted.
  See [Collection root resolution](#collection-root-resolution).
- `pic` (array, required): the photos in this collection.
  Singular per the ecosystem schema convention despite being
  array-typed.
  Order semantics in [Ordering](#ordering).

### Pic object fields

- `hash` (string, required): content-addressed identity of the source
  file.
  Format in [Hash identity](#hash-identity).
- `relative_path` (string, required): path to the photo relative to
  the collection root.
  Format in [Canonical forms](#canonical-forms).
- `original_filename` (string, optional): filename as found in the
  source, with no path component.
- `size_bytes` (integer, required): source file size in bytes.
- `mtime` (string, required): filesystem mtime of the source file in
  RFC 3339 UTC.
  Format in [Canonical forms](#canonical-forms).
- `timestamp` (string, optional + nullable): best-effort capture
  timestamp in RFC 3339 UTC.
- `timestamp_source` (string, optional + nullable): identifies how
  `timestamp` was derived.
  One of `"exif"`, `"filename"`, `"filesystem"`, or `"unknown"`.
- `camera` (string, optional + nullable): camera model from EXIF.
- `gps` (object, optional + nullable): GPS coordinates with shape
  `{lat: number, lon: number}`.
  Range constraints enforced by the JSON Schema:
  `-90 <= lat <= 90`, `-180 <= lon <= 180`.
- `tag` (array of strings, optional): flat tag strings.
  NormPic does not populate this field in v0.1.0; it is reserved for
  future use.
  Singular per the ecosystem schema convention.
  Absent and `[]` rules in
  [Optional, nullable, absent semantics](#optional-nullable-absent-semantics).

## Hash identity

The `hash` field on each pic is a content-addressed identifier
derived from the source file's bytes.

### Algorithm

BLAKE2b with a 120-bit (15-byte) digest, produced via `digest_size=15`
directly.
Not truncation of a longer digest.
BLAKE2b at `digest_size=15` is a cryptographically distinct value
from any prefix of `digest_size=32` or other sizes.

### Encoding

Crockford Base32, uppercase canonical, no check digit, no padding.
The 120-bit digest encodes to exactly 24 characters.
Crockford is intrinsically case-insensitive on read; uppercase is the
canonical emit form.

### Field format

A literal prefix `b2b120:` followed by the 24-character encoded
digest.

Example: `b2b120:0D7N3MKQ5Y8VBHRX2J4FWTAE`

### Prefix semantics

The literal `b2b120` is the algorithm-and-size discriminator.
Encoding (Crockford Base32) is implied by the schema version, not by
the prefix.

Future schema versions may introduce additional algorithms behind
different prefixes (for example `b2b256:` for a longer BLAKE2b
variant) without changing the field's shape.
The prefix is the forward-compatibility seam that lets the hash field
evolve without a breaking schema bump.

### What is hashed

The original source file's bytes as found on disk, before any
NormPic processing.

NormPic v0.1.0 does not modify source bytes regardless, but this
contract pins the semantic so that future producer implementations
cannot drift.

### Identity, not integrity

A re-encoded or EXIF-edited image produces different bytes and
therefore a different hash, even when it depicts the same scene.

A pixel-content hash is deferred for v0.1.0; see
[Out of scope and deferred for v0.1.0](#out-of-scope-and-deferred-for-v010).

### Producer and consumer obligations

- Producer MUST emit uppercase canonical Crockford Base32.
- Producer MUST emit the literal `b2b120:` prefix exactly.
- Consumer SHOULD accept lowercase Crockford on read.
- Consumer MUST verify the algorithm prefix matches a recognized
  scheme before assuming digest length or algorithm.

## Collection root resolution

This section answers "where is the collection?".
It is distinct from [Canonical forms](#canonical-forms), which
answers "what does a path inside the collection look like?".

### The collection_root field

`collection_root` is an optional top-level string field with default
value `"."`.
The default case (the manifest file sits at the collection root) is
emitted explicitly as `"."` rather than omitted.
This makes manifests self-documenting: a reader can see where the
collection lives without needing to consult contract documentation.

### Format rules

In v0.1.0, the value MUST be one of the following:

- The literal string `"."` (the default case).
- Zero or more `..` segments at the start, followed by zero or more
  non-special path segments.

Where:

- Path segments are separated by single forward slashes (`/`).
- Non-special segments contain no `/` and are neither `.` nor `..`.
- No trailing slash, no embedded `.` or `..`, no empty segments
  (`//`), no empty string.
- UTF-8 encoded, NFC Unicode normalized.
- No leading URI scheme (`s3://`, `https://`, etc.) in v0.1.0.
  URI schemes are reserved for future versions.

Valid examples: `.`, `..`, `../..`, `../photos`,
`../../shared/wedding`, `subdir`, `subdir/more`.

Invalid examples: `./foo`, `foo/./bar`, `foo/../bar`, `foo/`,
`foo//bar`, and the empty string.

### Resolution algorithm

Consumers MUST follow this algorithm to locate pic files:

1. Locate the manifest file at some path M.
2. Read `collection_root` from the manifest, defaulting to `"."` if
   absent.
3. Collection root directory = directory_of(M) joined with
   `collection_root`, normalized.
4. For each pic, full file location = collection root directory
   joined with `pic.relative_path`.

### Forward extension

Future v0.x versions are anticipated to support remote and
non-filesystem collections by introducing leading URI schemes:

- `s3://bucket/prefix`
- `https://host/path`
- `ssh://host/path`

The leading-scheme prefix is the discriminator (the same pattern as
the hash prefix).
A bare string is interpreted as a relative filesystem path; a string
starting with `scheme://...` is interpreted as a URI.

A v0.1.x consumer encountering an unrecognized URI scheme MUST refuse
the manifest, per the forward-compatibility rule in
[Status and versioning policy](#status-and-versioning-policy).

### Variant collections

Variant collections (thumbnails, web-optimized versions, RAW
companions) are deferred for v0.1.0.

Future versions are anticipated to add sibling fields like
`thumbnail_root`, `web_root`, and `raw_root`.
Each would carry its own location string under the same format and
discriminator rules as `collection_root`.

Pic-level `relative_path` entries are designed to be reusable across
roots: the same relative path can resolve against whichever root the
consumer is currently reading, allowing originals and variants to
share filename structure without duplication in the manifest.

### Producer and consumer obligations

- Producer MUST emit `collection_root`, including the literal `"."`
  in the default case.
- Consumer MUST treat absent `collection_root` as equivalent to `"."`
  (defensive forward-compatibility against non-conformant producers
  that omit the default).
- Consumer MUST reject manifests whose `collection_root` contains an
  unrecognized leading URI scheme.

## Canonical forms

This section defines the exact byte-level forms that emit and read
operations must produce and accept.
Two implementations disagreeing on canonical forms will produce
manifests that appear compatible but break consumers silently.

### Path strings

Applies to `relative_path` on each pic.
`collection_root` has its own format rules; see
[Collection root resolution](#collection-root-resolution).

The following rules apply to `relative_path`:

- UTF-8 encoded.
- Forward slash (`/`) as the only path separator; no backslashes or
  platform-specific separators.
- No leading `./`, no trailing slash, no empty segments (no `//`).
- No `.` or `..` segments anywhere in the path.
- No absolute paths (no leading `/`, no drive letter).
- Unicode normalization form C (NFC) for cross-platform stability.
- Case preserved exactly; comparisons are byte-equal, not case-folded,
  even when the underlying filesystem is case-insensitive.

Rationale: every rule above guarantees one canonical string per
logical path.
Aliasing constructs (`./`, `..`, `.`, empty segments) would force
every consumer to perform path normalization, and path normalization
across languages is famously inconsistent.
Python's `os.path.normpath`, Rust's `Path::canonicalize`, and Node's
`path.normalize` all have edge cases that disagree on things like
trailing-slash handling and symbolic-link resolution.

`..` is additionally disallowed in `relative_path` because it can
reference outside the collection root, violating the relative-to-root
semantic and creating a path-traversal hazard for consumers reading
untrusted manifests.

Absolute paths are disallowed because they are machine-local and
defeat the portability the contract exists to provide.

### Hash encoding

Crockford Base32, uppercase canonical on emit, lowercase tolerated on
read.
Full rules in [Hash identity](#hash-identity).

### Timestamps

Applies to `generated_at` (top-level), and `mtime` and `timestamp`
(each pic).

- RFC 3339, a strict subset of ISO 8601.
- Mandatory `Z` suffix to denote UTC.
- Offset variants like `+00:00` MUST NOT be emitted and MUST be
  rejected on read.
- Fractional seconds optional; if present, any precision is
  acceptable.

Examples: `2025-11-24T15:30:45Z` or `2025-11-24T15:30:45.123Z`.

### JSON encoding

- UTF-8 only.
- No byte-order mark (BOM).
- Key order in objects is not significant; consumers MUST NOT depend
  on it.
- Whitespace and pretty-printing MAY be applied freely by the
  producer; consumers MUST accept any well-formed JSON.

### Producer and consumer obligations

- Producer MUST honor all canonical-form rules on emit.
- Consumer MUST reject malformed inputs.
  Tolerant-on-read rules are explicitly enumerated above (lowercase
  Crockford, key order) and MUST NOT be extended silently by
  individual implementations.

## Optional, nullable, absent semantics

This section defines the behavioral rules that fall outside JSON
Schema validation.
The JSON Schema artifact at `schema/v0.1.0.json` encodes which
fields are required, which accept null, and the type of each.
This section covers what schema validation cannot enforce: how
consumers should treat the distinction (or non-distinction) between
absence, null, and empty values.

### Categories

Each field in the schema falls into one of four categories.

Required, non-nullable (the default category).

- Must be present.
- Must not be `null`.
- Wrong type or absence makes the manifest invalid.

Optional, non-nullable.

- May be absent.
- If present, must have the declared type.
- `null` is not permitted.

Optional, nullable.

- May be absent, OR present with value `null`, OR present with the
  declared type.
- Consumers MUST treat absence and `null` as semantically equivalent.
- Producers SHOULD prefer absence over explicit `null` for cleaner
  output, but MAY emit `null`.

Optional array.

- May be absent, OR present as `[]`, OR present with items.
- Consumers MUST treat absence and `[]` as semantically equivalent.
- Producers SHOULD prefer absence over `[]` for unset fields, but MAY
  emit `[]`.

Per-field categorization lives in the field annotations in
[Manifest schema](#manifest-schema).

### Rationale

Two-state representation (absence versus `null`) for optional fields
is a known source of cross-implementation drift.
JSON Schema validators differ on whether they require `null` to be
explicitly allowed in the schema, whether they accept missing keys
for optional+nullable, and how they report errors.

Pinning the equivalence at the contract level means consumers in any
language never have to disambiguate these states downstream of
validation.

For arrays, `[]` is a perfectly valid JSON value, but for "no tags"
the choice between `[]` and absence is arbitrary.
Pinning equivalence prevents alias bugs the same way path canonical
forms do.

## Ordering

### Semantics

The `pic` array order reflects the producer's best-effort temporal
reconstruction.
Real-world photo collections have imperfect temporal signals (camera
clock skew, undated files, burst sequences), so "best-effort" is
intentional language.

The producer determines the exact strategy (EXIF timestamp, filename
heuristics, filesystem mtime, etc.) and tiebreaking (burst-sequence
preservation, camera-identity grouping, etc.).
The contract does NOT pin the strategy in v0.1.0; different producer
implementations MAY produce different orderings for the same input.

A future ordering-provenance field is anticipated.
Once added, consumers will be able to know which strategy was used
and rely on cross-implementation reproducibility.
See
[Out of scope and deferred for v0.1.0](#out-of-scope-and-deferred-for-v010).

### Determinism

Determinism MUST hold within a single producer implementation: the
same producer running over the same input MUST produce a
byte-identical manifest, including pic order.

Cross-implementation byte-identical ordering is NOT guaranteed in
v0.1.0.
This is acknowledged here rather than hidden, so consumers depending
on cross-implementation stability know to re-sort explicitly.

### Producer and consumer obligations

Consumer behavior:

- MAY rely on `pic` order as a default chronological display.
- MAY re-sort or filter using any combination of fields (for example
  by `timestamp`, `camera`, or `relative_path`).
- SHOULD NOT depend on cross-implementation byte-identical pic order
  until ordering provenance lands in a future version.

Producer behavior:

- MUST produce deterministic output for repeated runs over the same
  input.
- SHOULD document the temporal-reconstruction strategy in
  implementation-side documentation (out of contract scope).

### Rationale

A single locked algorithm in the contract would force every
implementation to perfectly reproduce edge-case behaviors of one
reference producer.
That is brittle, hard to test across languages, and forecloses
legitimate improvements to heuristics.

Deferring strategy to the producer and recording it via a future
provenance field lets implementations evolve their heuristics
without breaking the contract.

Per-implementation determinism is still required so that manifest
re-runs are byte-stable, enabling manifest content addressing and CI
regression checks.

## Producer contract

This is a quick-reference summary of producer obligations.
Authoritative rules and rationale live in the sections
cross-referenced.
When this summary conflicts with a detailed section, the detailed
section wins.

### MUST

- Emit `version` matching the schema implemented.
  See [Status and versioning policy](#status-and-versioning-policy).
- Emit all required fields per the schema.
  See [Manifest schema](#manifest-schema).
- Emit hashes with the literal `b2b120:` prefix and uppercase
  canonical Crockford Base32 encoding.
  See [Hash identity](#hash-identity).
- Honor canonical forms on emit: UTF-8, forward-slash paths only, RFC
  3339 UTC timestamps with mandatory `Z` suffix, NFC normalization,
  no BOM, no aliasing path constructs.
  See [Canonical forms](#canonical-forms).
- Emit `collection_root` explicitly, including the literal `"."` in
  the default case.
  See [Collection root resolution](#collection-root-resolution).
- Produce deterministic output for repeated runs over the same input:
  same input, same byte-identical manifest including pic ordering.
  See [Ordering](#ordering).

### SHOULD

- Prefer absence over explicit `null` for unset optional+nullable
  fields.
- Prefer absence over `[]` for unset optional arrays.
  See
  [Optional, nullable, absent semantics](#optional-nullable-absent-semantics).
- Document the temporal-reconstruction strategy in implementation
  docs, outside contract scope.
  See [Ordering](#ordering).

### MAY

- Emit fields beyond those in the schema for experimentation or
  forward-compatibility probing.
  Consumers MUST tolerate these per the forward-compatibility rule.
  See [Status and versioning policy](#status-and-versioning-policy).

## Consumer contract

This is a quick-reference summary of consumer obligations.
Authoritative rules and rationale live in the sections
cross-referenced.
When this summary conflicts with a detailed section, the detailed
section wins.

### MUST

- Refuse manifests with an unrecognized major.minor `version`.
  See [Status and versioning policy](#status-and-versioning-policy).
- Accept manifests containing unknown optional fields at a recognized
  major.minor.
- Verify the hash algorithm prefix matches a recognized scheme before
  assuming digest length or algorithm.
  See [Hash identity](#hash-identity).
- Treat absent `collection_root` as equivalent to the value `"."`.
- Reject manifests whose `collection_root` contains an unrecognized
  leading URI scheme.
- Follow the collection root resolution algorithm to locate pics.
  See [Collection root resolution](#collection-root-resolution).
- Treat absence and `null` as semantically equivalent for
  optional+nullable fields.
- Treat absence and `[]` as semantically equivalent for optional
  arrays.
  See
  [Optional, nullable, absent semantics](#optional-nullable-absent-semantics).
- Reject inputs that violate canonical-form rules on read (for
  example a timestamp using `+00:00` instead of `Z`, or a path with
  `..` segments).
  See [Canonical forms](#canonical-forms).

### SHOULD

- Validate manifests against the JSON Schema artifact
  (`schema/v0.1.0.json`) before relying on contents.
- Accept lowercase Crockford Base32 encoding on hash reads.
  See [Hash identity](#hash-identity).

### SHOULD NOT

- Depend on cross-implementation byte-identical pic ordering until
  ordering provenance lands in a future version.
  See [Ordering](#ordering).

### MAY

- Rely on `pic` array order as a default chronological display.
- Re-sort or filter using any combination of pic fields (for example
  by `timestamp`, `camera`, or `relative_path`).
  See [Ordering](#ordering).

## Decide before v0.1 ships

This section tracks contract-level decisions that remain to be
resolved before v0.1.0 is published as a stable release.
Items here block the v0.1.0 version stamp from going stable.
The list shrinks to zero as decisions land.

At v0.1.0 publication, this section can either remain as a record of
what was settled, or be archived to the changelog and removed from
the contract document.

### Open decisions

- Pre-hiatus field-name reconciliation.
  The existing Python implementation may use field names from the
  pre-hiatus contract that are not in this draft.
  A code-level audit is needed to identify any survivors.
  Lean: align all names to this contract; the implementation tracks
  the contract, not vice versa.
  Resolve via an early-PR task in the v0.1 sequenced TODO.

### Decisions resolved during drafting

Items resolved during the drafting of this document have been folded
into the relevant sections rather than left here.
For the record, the resolved decisions include:

- BLAKE2b with `digest_size=15` for the hash algorithm.
- Crockford Base32, uppercase canonical, no padding, no check digit.
- `b2b120:` (no hyphen) as the hash field prefix.
- `relative_path` strictly canonical: no leading `./`, no `..`, no
  embedded `.`, no absolute paths.
- `collection_root` allows `..` segments at the start; emitted
  explicitly even in the default case (`"."`).
- `size_bytes` (plural) kept as the field name.
- Empty string rejected for required string fields (`minLength: 1`
  in the JSON Schema).
- `null` rejected for non-nullable optional fields (only
  `original_filename` in v0.1.0).
- GPS coordinates validated in the JSON Schema:
  `-90 <= lat <= 90`, `-180 <= lon <= 180`.
- Determinism is MUST not SHOULD for per-implementation byte-stable
  output.
- Cross-implementation byte-identical pic ordering not guaranteed in
  v0.1.0; resolution deferred to a future ordering-provenance field.

## Related projects

Each entry has its current status (exists, planned, or deferred) and
its relationship to NormPic's manifest contract.

- Galleria (planned): static gallery generator that consumes NormPic
  manifests.
  Primary downstream consumer.
  May become a Static Site Generator plugin (11ty first, others
  later) rather than a standalone tool over time.

- personal-site (planned): the marcusgrant.me site stack.
  Integrates Galleria's static-gallery output at a subdomain
  (`gallery.<domain>.tld`).
  Indirect consumer; manifests reach personal-site through Galleria,
  not directly.

- composer / marcustack (planned): shell orchestration layer that
  runs the NormPic-then-Galleria pipeline as a unit.
  Triggered by git hooks; workstation-first, container-ready.
  Does not interact with the manifest contract directly; orchestrates
  the tools that do.

- zk-notes (planned): wiki and knowledge base, separate project.
  May share tag taxonomy with NormPic long-term (the tag-hierarchy
  question is deferred for both projects until real usage demands
  it).
  Not a direct consumer of NormPic manifests.

- retro-theme (planned, parked): shared CSS design system, currently
  documented only.
  Consumed by Galleria's static output, not by NormPic directly.

- 11ty plugin (planned, post-Rust-port): NormPic as a Static Site
  Generator integration via WASM-compiled Rust core.
  Future direct consumer at the manifest contract level.
  The contract's implementation-agnostic design is the seam that
  makes this plugin path viable.

- Hugo plugin (planned, post-Rust-port): same pattern as the 11ty
  plugin, different SSG.

Status labels follow the ecosystem convention.
This section is updated as projects move between states or as new
consumers join the ecosystem.

## Out of scope and deferred for v0.1.0

This section enumerates what is not in the v0.1.0 contract, so
consumers and implementers do not need to guess what is intentional
versus omitted by oversight.

### Anticipated for future v0.x or v1.0

These are additive extensions expected to land in a future version
of the contract.

- Ordering provenance field.
  Records the temporal-reconstruction strategy and tiebreaking chain
  used to produce the pic order.
  Anticipated to resolve the current cross-implementation pic-order
  caveat.
  See [Ordering](#ordering).

- URI schemes for `collection_root` (remote sources).
  Future schemes like `s3://`, `https://`, `ssh://` to allow
  manifests to reference non-filesystem-local collections.
  See [Collection root resolution](#collection-root-resolution).

- Variant collection root fields (for example `thumbnail_root`,
  `web_root`, `raw_root`).
  Sibling fields to `collection_root`, each carrying a location for
  a different photo variant.
  Pic-level `relative_path` resolves against whichever variant root
  the consumer is reading.
  See [Collection root resolution](#collection-root-resolution).

- Diagnostics sidecar.
  A separate file (working name `manifest.report.json`) capturing
  warnings, errors, and processing context.
  Anticipated if log-only diagnostics prove insufficient for archival
  or audit.

- Pixel-content hash.
  An alternative or supplementary hash computed over decoded pixel
  data, useful for detecting "same image, different EXIF" cases.
  See [Hash identity](#hash-identity).

- Output-bytes integrity hash for the destination tree.
  Distinct from the pic-identity hash; verifies the integrity of the
  produced destination, not the source identity.

- Sub-grouping within a collection.
  Explicit group structure beyond what flat tags can express.
  Reconsider if tag-based grouping proves insufficient for real
  collections.

- Tag hierarchy and external taxonomy.
  Open questions on taxonomy-file location, single-parent versus DAG,
  and namespacing for disambiguation.
  Likely coordinated with zk-notes long-term; see
  [Related projects](#related-projects).

- Provenance file mapping hash to source location.
  Not warranted for current use cases; reconsider if remote sources
  or multi-source merging make it valuable.

### Permanently out of scope for the manifest contract

These are not part of the contract by design and are unlikely to be
added in any version.

- Operational state (where the manifest lives on disk, source-archive
  locations, sync state across runs).
  Belongs to producer implementations; the contract describes the
  emitted artifact, not the tool's internals.

- Implementation-side schema migration mechanics (how a tool handles
  reading an older schema-versioned manifest module).
  Covered by `schema-versioning.md`, which addresses Python-side
  module evolution.
  This contract addresses the durable shape of the artifact, not how
  an implementation evolves its parsers.

- Photo editing, transcoding, or pixel-data semantics.
  NormPic does not modify pixel data; this contract describes a
  manifest about photos, not a transformation pipeline.

- Gallery rendering and presentation semantics.
  Galleria's concern, not this contract's.

- Operational error-logging format.
  Diagnostics go to producer-local logs at runtime; a structured
  sidecar may eventually be added (see anticipated list above), but
  the live-log format is implementation-defined and out of contract.