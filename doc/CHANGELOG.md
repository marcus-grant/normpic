# NormPic Development Changelog

## 2026-07-20

### chr/v01-housekeeping

pyright brought to green across the tree and wired into the enforced
quality gate as a blocking check, machine-checked not convention-only.
Fixed a deserialize round-trip dropping original_filename, required
Pic.relative_path per the v0.1 contract, migrated model and serializer
tests to a verified Pic factory.
Extraction residue removed: deleteme-normpic-modules/ was untracked and
gitignored; deleted off-tree and its *deleteme* ignore rules removed
from .gitignore. Full gate green after removal.

## 2026-07-10

### ref/serializer-v01-contract

Serializer finalized to the v0.1 contract. Optional pic fields
(timestamp, timestamp_source, camera, gps) now omitted when unset
rather than emitted as null, per the contract's prefer-absence rule;
deserialize reads them via .get() so absence-form manifests round-trip.
Serialize output pinned deterministic with sort_keys. Obligations for
always-emit required fields, collection_root default, and canonical
b2b120 hash were already satisfied by prior arc work. Test count
285 -> 289.

## 2026-07-07

### ref/drop-source-dest-cutover

Copy manifest is now contract-pure: source_path, dest_path, and errors
removed from Pic model and serialization; hash-keyed reprocessing wired
as the only path in organize_photos (stat-skip and --force included);
serializer validation cut to schema/v0.1.0.json loaded from disk;
schema_v0.py deleted; cutover acceptance gate unskipped and green.
Manual wedding-archive result: 645 pics, 0 dangling symlinks, manifest
carries no source_path/dest_path/errors, validates canonical, photos
open through the symlinks. Phase B complete. Test count 280 -> 285.

- hash-keyed reprocessing: organize_photos replaced source_path-keyed
  lookup with build_hash_keyed_source_index + needs_reprocessing_by_hash;
  stat-skip (mtime+size match reuses stored hash) and --force flag wired
  in the same commit.
- needs_reprocessing_by_hash dest-existence check: resolved via
  matched.relative_path, not matched.dest_path.
- deserialize: .get() used for legacy keys so manifests lacking
  source_path/dest_path/errors load without error.
- Pic model: source_path, dest_path, errors field definitions and all
  to_dict() emission removed; build_source_manifest and
  _create_ordered_pics construction sites cleaned.
- schema_v0.py deleted; serializer now loads schema/v0.1.0.json from
  disk at import time (_MANIFEST_SCHEMA module-level constant);
  test_schema.py retargeted at canonical schema; inline PIC_SCHEMA
  import in test_manifest_manager.py removed.
- Cutover acceptance gate (test_cutover_complete_relative_path_only):
  skip decorator removed; gate passes green on first run, proving the
  full end state holds across the commit sequence.

### Phase B: Implementation Alignment -- Summary

18 PRs delivered from 2026-06-10 through 2026-07-07 (see per-PR entries
in this CHANGELOG). v0.1 contract implemented end-to-end: b2b120 hash,
relative_path only, hash-keyed reconciliation with stat-skip and --force,
canonical schema enforced at the serializer boundary, schema_v0.py
deleted. Manual wedding-archive acceptance: 645 pics, 0 dangling
symlinks, manifest validates canonical.

Note: ft/source-manifest-read (source manifest read/create path) was
absorbed into ref/symlink-reconcile-by-hash and has no standalone entry.

Two Phase B items remain open: ref/serializer-v01-contract and
chr/pyright-clean.

## 2026-07-04

### ref/symlink-reconcile-by-hash

Symlinks created from runtime hash reconciliation of both manifests;
source manifest pics carry relative_path; burst-counter dead loop
removed; producer now emits generated_at and timestamp in canonical
UTC-Z form. Manual wedding-archive run: 645 symlinks, zero dangling,
manifest validates canonical. Test count 275 -> 280.

- build_source_manifest: sets relative_path=f.name on each Pic;
  bare filename is the path relative to collection_root ".".
- resolve_symlink_pairs_by_hash: new helper in photo_manager;
  resolves (source, dest) pairs via the contract algorithm on both
  manifests; no source-hash match raises RuntimeError explicitly.
- organize_photos symlink loop replaced with helper call; no
  stored source_path or dest_path consumed for linking.
- Equivalence tests: hand-built fixture and producer-generated
  both confirm hash-reconciled pairs equal stored-field pairs.
- test_source_manifest_read_when_present: real file hash used so
  hash-keyed reconciliation resolves correctly.
- _create_ordered_pics: dead inner burst-counter loop deleted;
  Pic-creation loop already recomputed dest_filename identically.
- Fix (surfaced by manual archive run, not in original plan):
  photo_manager emitted naive generated_at; Manifest.to_dict and
  Pic.to_dict used isoformat() which produces +00:00 for UTC-aware
  datetimes -- the canonical schema explicitly rejects +00:00.
  Fixed to datetime.now(tz=timezone.utc) and strftime Z suffix.
  Two producer-conformance tests added: generated_at Z suffix and
  full schema/v0.1.0.json validation via organize_photos output.
- manifest-contract.md: added co-location precondition section
  documenting the v0.1 limitation that collection_root resolution
  is positional and depends on the manifest's physical location.

## 2026-06-30

### ref/copy-manifest-contract-fields

Copy manifest now carries relative_path in canonical form;
source_path and dest_path still emitted; parked hash index
relocated. Test count 270 -> 275.

- pic.py: add relative_path: Optional[str] = None; to_dict()
  emits it when not None (absent on old records).
- schema_v0 PIC_SCHEMA: add relative_path property with
  type-guarded if/then structure copied verbatim from
  schema/v0.1.0.json; save-time validation catches non-canonical
  values before the cutover PR.
- _create_ordered_pics: assign relative_path=dest_filename at Pic
  construction; same bare organized name as dest_path.
- ManifestSerializer.deserialize: pass relative_path through from
  JSON so the field survives round-trips.
- Remove premature hash_keyed_index build from photo_manager
  (import and call site); definition stays in manifest_manager;
  call site lands in ref/symlink-reconcile-by-hash where consumed.
- TestCopyManifestRelativePath: 4 unit tests (emitted when set,
  absent when None, canonical form, schema rejects non-canonical).
- test_copy_manifest_pics_carry_relative_path: integration test
  asserts relative_path equals dest_path on all pics and survives
  JSON round-trip.

## 2026-06-29

### ft/hash-keyed-reprocessing

Add hash-keyed change detection and fix mtime precision. Test
count 230 -> 270.

- manifest_manager: add build_hash_keyed_source_index; returns
  {hash: Pic} from any Manifest pic list; first entry wins on
  duplicate hash.
- ManifestManager: add needs_reprocessing_by_hash; mirrors
  needs_reprocessing but keyed on content hash; checks dest
  existence via matched_pic.dest_path resolved against dest_dir.
- photo_manager: import build_hash_keyed_source_index and build
  hash_keyed_index from existing_manifest; no production consumer
  yet, index available for the next PR.
- TestHashKeyedChangeDetection: 9 tests; unit coverage for index
  building and per-photo detection; equivalence test asserts
  hash-keyed and path-keyed partition a shared 4-photo fixture
  identically (NEW, CHANGED-mtime, CHANGED-dest-missing,
  UNCHANGED).
- needs_reprocessing and needs_reprocessing_by_hash: replace
  abs(delta)>0.001 tolerance with ISO strftime comparison on both
  sides; sub-microsecond float drift no longer causes false-CHANGED.
- Remove test_mtime_tolerance; add test_mtime_roundtrip_no_false_changed.

## 2026-06-24

### ref/manifest-model-v01-contract

Align Manifest model with v0.1 contract. Test count 250 -> 253.

- manifest.py: add collection_root: str = "."; always emitted in
  to_dict() per contract; drop errors, warnings, processing_status
  fields and their to_dict() branches.
- MANIFEST_SCHEMA: add collection_root property; drop the three
  diagnostics entries. ERROR_SCHEMA stays (used by PIC_SCHEMA).
- serializer deserialize(): add collection_root kwarg; drop three
  diagnostics kwargs.
- photo_manager.py: delete 22-line dead block that built the dropped
  kwargs; error_handler construction and handle_* calls stay.
- error_handling.py: delete get_errors_for_manifest and
  get_warnings_for_manifest; no remaining callers.
- test_models.py: 3 new TestManifest cases (default, explicit,
  round-trip); existing tests updated in lockstep.
- test_error_handling_workflow.py: replace stale TDD comment.

## 2026-06-23

### ref/pic-model-v01-contract

Align Pic model with v0.1 contract pic-object fields. Test count
250 -> 250 (no net change; existing tests updated in lockstep).

- pic.py: MISSING sentinel for absent original_filename;
  __post_init__ rejects None, empty string, and path separators;
  _TS_VALUES frozenset; timestamp_source enum validated at
  construction; tag Optional[List[str]] omitted from to_dict when
  None; errors field retained (drop deferred to
  ref/serializer-v01-contract, guard triggered at manifest.py:71).
- schema_v0.py: PIC_SCHEMA gains original_filename (string, no
  separator pattern) and tag (optional array of strings).
- test_models.py: 11 new cases; all_fields and to_dict updated.
- test_serializer.py: invalid-data fixture switched to size_bytes=-1;
  invalid timestamp_source now caught at construction, not schema.

## 2026-06-22

### ft/hash-blake2b-crockford

Replace SHA-256 with BLAKE2b-120 + Crockford Base32 as the canonical
producer-side hash format. Test count 226 -> 239 (13 new). All call
sites updated in lockstep.

- normpic/util/hash.py: b2b120_hash and b2b120_encode_digest;
  inline Crockford encoder; fixed-width via len*8/5 not bit_length.
- filesystem.py compute_file_hash: blake2b streaming, b2b120: return.
- manifest_manager.py compute_file_hash: b2b120_hash one-shot.
- photo_manager.py: replace built-in hash() with b2b120_hash.
- test/unit/test_hash.py: encoder boundaries, 256-input length
  invariant, six depo vectors, two normpic vectors via hash-b32.sh,
  prefix invariant, alphabet compliance.

## 2026-06-18

### fix/schema-not-pattern-typeguard

Type-guard the string-content constraints in schema/v0.1.0.json so
non-string values (null, integer) are rejected with a clean type error
instead of spurious path-separator misattributions. Test count 225 → 226.

- original_filename: replace two not:{pattern} entries with a single
  positive pattern ^[^/\\]*$ — positive patterns are absent (not
  vacuously false) for non-strings; star not plus so minLength owns
  emptiness and pattern owns separators.
- relative_path: wrap existing allOf in if:{type:string}/then guard;
  regexes unchanged.
- collection_root: same guard on inner allOf inside anyOf; regexes
  unchanged.
- Add test_null_for_non_nullable_optional_single_type_error: null
  fixture must yield exactly 1 error whose message contains
  "is not of type"; RED before schema change, GREEN after.
- Append schema authoring note to manifest-contract.md §Format rules:
  string-content constraints must be type-guarded; canonical forms are
  positive pattern (simple) or if/then wrapper (multi-constraint).

### tst/conformance-invalid-misc-rules

Seven schema-layer invalid fixtures completing the invalid category.
With the consumer-lenient fixture already landed, the full conformance
fixture inventory is now complete: 6 valid, 14 schema-invalid, 2
impl-invalid, 1 consumer-lenient. Test count rises to 225.

- Adds invalid/hash-bad-prefix.json: hash with b2b256: prefix instead
  of b2b120:; schema rejects at $.pic[0].hash (1 error).
- Adds invalid/hash-wrong-length.json: b2b120: prefix with 23-char
  payload; schema rejects at $.pic[0].hash (1 error).
- Adds invalid/timestamp-offset-form.json: generated_at uses +00:00
  instead of Z; schema rejects at $.generated_at (1 error).
- Adds invalid/gps-lat-out-of-range.json: gps.lat 91.0, lon valid;
  schema rejects at $.pic[0].gps (1 error).
- Adds invalid/empty-required-string.json: collection_name set to "";
  schema rejects at $.collection_name (1 error).
- Adds invalid/null-for-non-nullable-optional.json: original_filename
  null; schema rejects at $.pic[0].original_filename (3 errors, all
  same field and root cause: type + vacuous-truth not-pattern).
- Adds invalid/missing-required-field.json: pic.mtime omitted; schema
  rejects at $.pic[0] (1 error).
- Updates test/fixture/conformance/README.md: 7 rows added to invalid
  table; stale "not yet implemented" caveat removed.

## 2026-06-17

### tst/conformance-consumer-lenient

Consumer-lenient fixture and hash normalizer. All three harness
categories (valid, invalid, consumer-lenient) are now active.
The invalid category is still missing 7 required schema-layer cases;
those are deferred to tst/conformance-invalid-misc-rules.
Test count rises to 18.

- Adds consumer-lenient/hash-lowercase-crockford.json: valid manifest
  with all-lowercase Crockford hash payload. collection_name is present
  so lowercase hash is the sole violation; schema rejects the raw form.
- Adds consumer_normalize() to normpic/util/manifest_validate.
  Deep-copies the manifest, walks pic[].hash, and for any b2b120: hash
  applies Crockford lenient read to the 24-char payload: case-folds to
  uppercase, alias-folds i/I and l/L to 1, o/O to 0. No depo import.
- Re-exports consumer_normalize from test/helpers/conformance.
- Adds test_consumer_lenient_fixture_schema_rejects_raw: raw form fails.
- Adds test_consumer_lenient_fixture_accepted_after_normalize: normalize
  then schema-validate passes.
- Adds test_consumer_normalize_crockford_alias_fold: direct unit test of
  alias branch, input i/I/l/L/o/O maps to 1/1/1/1/0/0.
- Reconciles test/fixture/conformance/README.md:
  - 7 invalid entries deferred to tst/conformance-invalid-misc-rules
    removed from the README table; required inventory in conformance.md.
  - Consumer-lenient filename corrected (lowercase-crockford-hash.json
    -> hash-lowercase-crockford.json).
  - Usage pattern updated to actual harness API.
  - Reference link to conformance.md added.

### tst/conformance-invalid-impl-layer

Two impl-layer invalid fixtures and the validator module they drive.
Test count rises to 15 (6 valid + 7 schema-invalid + 2 impl-invalid).

- Adds normpic/util/manifest_validate.py with impl_validate().
- impl_validate checks collection_root: .. segment after the leading
  run is a violation; returns a descriptive error string.
- impl_validate checks timestamps: generated_at, pic.mtime, and
  pic.timestamp are parsed via datetime.fromisoformat; ValueError
  surfaces as an error string (catches impossible calendar values).
- Re-exports impl_validate from test/helpers/conformance.py.
- Adds test_impl_layer_fixture_rejected_by_impl to test_conformance.py;
  globs invalid/impl/*.json; asserts schema-accept and impl-reject.
- Adds invalid/impl/collection-root-nonleading-dotdot.json:
  collection_root "photos/../more" passes schema, fails impl check.
- Adds invalid/impl/timestamp-bad-calendar.json:
  timestamp "2025-13-01T00:00:00Z" passes schema regex, fails
  datetime parse (month 13).
- Fixtures placed in invalid/impl/ subdirectory to keep the
  schema-only test glob (invalid/*.json) unchanged.

### tst/conformance-invalid-path-rules

Seven schema-layer invalid fixtures covering path-canonical-form
violations, plus the parametrized rejection test that exercises them.
Test count rises to 13 (6 valid + 7 invalid); all pass.

- Adds test_invalid_fixture_rejected_by_schema to test_conformance.py:
  parametrized over invalid/*.json, asserts schema rejects each.
- Adds invalid/relative-path-absolute.json: leading / in relative_path.
- Adds invalid/relative-path-dot-segment.json: . segment in relative_path.
- Adds invalid/relative-path-dotdot-segment.json: .. segment in relative_path.
- Adds invalid/relative-path-backslash.json: backslash in relative_path.
- Adds invalid/collection-root-leading-dotslash.json: ./ prefix in
  collection_root.
- Adds invalid/collection-root-uri-scheme.json: s3:// scheme in
  collection_root; URI schemes reserved for future versions.
- Adds invalid/original-filename-path-separator.json: / in
  original_filename.
- Updates test/fixture/conformance/README.md invalid table to reflect
  actual fixture filenames and add missing entries.

### tst/conformance-valid-fixtures

Five valid fixtures completing the required conformance inventory.
Test count rises from one to six parametrized valid cases; all pass.

- Adds valid/full.json: every top-level and per-pic field populated,
  including collection_description, config, original_filename,
  timestamp, timestamp_source (exif), camera, gps, tag.
- Adds valid/collection-root-default.json: collection_root "." with
  one pic; verifies the most common producer output shape.
- Adds valid/collection-root-traversal.json: collection_root "../.."
  (leading ".." only, no segments after); verifies traversal case.
- Adds valid/empty-collection.json: zero pics with top-level optional
  fields populated; verifies empty pic array alongside metadata.
- Adds valid/optional-fields-as-null.json: all nullable optional
  fields set to explicit null at top-level and per-pic; verifies
  consumers treat null and absence as equivalent.

### tst/conformance-harness

Conformance fixture directory structure, schema-layer harness, and
first valid fixture.

- Created test/fixture/conformance/{valid,invalid,consumer-lenient}/
  subdirectories.
- Added valid/minimal.json: required fields only, empty pic array,
  collection_root "." (always-emit contract rule).
- Added test/helpers/conformance.py: load_schema, load_fixture,
  schema_validate using Draft202012Validator.
  Extension points for impl_validate and consumer_normalize noted for
  later conformance PRs.
- Added test/unit/test_conformance.py: parametrized
  test_valid_fixture_passes_schema; one case passes (minimal.json).
- Added doc/test/conformance.md: harness purpose, two-layer model,
  fixture categories, API reference, how to add fixtures.
- Updated doc/test/README.md with conformance.md entry.

### ref/field-name-reconciliation

Pre-hiatus field names aligned to the v0.1 contract.
Pure rename refactor; no behavior change; 200 tests green throughout.

- Manifest array field renamed from `"pics"` to `"pic"` across
  `normpic/model/manifest.py`, `normpic/model/schema_v0.py`,
  `normpic/serializer/manifest.py`, `normpic/manager/photo_manager.py`,
  `normpic/util/error_handling.py`, `normpic/cli/main.py`,
  and all nine affected unit and integration test files.
- GPS dict keys in `normpic/manager/photo_manager.py` renamed from
  `"latitude"`/`"longitude"` to `"lat"`/`"lon"`.
  Fixes a latent producer bug: both `schema_v0.py` and
  `schema/v0.1.0.json` already required `lat`/`lon`; the pre-rename
  code would produce schema-invalid manifests for any pic with GPS
  data.
- Pre-hiatus diagnostic fields on Manifest and Pic (error lists,
  warnings, processing_status) identified but not removed; removal
  is behavior change, deferred to `ref/manifest-model-v01-contract`
  and `ref/pic-model-v01-contract`.

## 2026-06-10

### Fix/contract-schema-reconciliation

Pre-ship tightening of the v0.1.0 schema artifact, manifest contract
doc, and conformance inventory.
No version bump; all changes are intra-draft corrections.

- __Schema__ (`schema/v0.1.0.json`): added backslash prohibition to
  `relative_path`; added `minLength:1` and path-separator
  prohibitions to `original_filename`; added `minLength:1` to
  `collection_description`, `camera`, and `tag` items; added
  explicit URI-scheme `not` pattern and `"default": "."` annotation
  to `collection_root`.
- __Contract doc__ (`manifest-contract.md`): `size_bytes` described
  as non-negative integer; backslash ban in `relative_path` is now
  an explicit MUST; `original_filename` has an explicit MUST
  prohibiting path separators; empty-string rejection note added at
  the `Categories` section level for all string fields; `collection_root`
  URI rejection corrects to cite the explicit `not` pattern.
- __Conformance inventory__ (`conformance.md`): four new invalid
  cases added: `relative_path` with backslash (schema), `original_filename`
  with path separator (schema), timestamp with invalid calendar value
  (implementation), `collection_root` with URI scheme (schema).

## 2026-06-09

### Phase A Planning Completes

Completes the Phase A planning artifacts tracked in
`doc/TODO.md`; v0.1 implementation work (Phase B) is now unblocked.

- __Conformance Requirement Defined__: new planning artifact at
  `doc/architecture/conformance.md` specifies what any normpic
  implementation must demonstrate to claim v0.1 conformance.
  Documents the two-layer validation model (schema-mechanical
  versus implementation-semantic), three fixture categories
  (valid, invalid, consumer-lenient), the full fixture inventory by
  case with the catching layer for each invalid case, producer and
  consumer responsibilities, and v0.1.0 acceptance criteria.
  Peer to `manifest-contract.md`, references it as source of truth.
- __Architecture README Updated__: `doc/architecture/README.md` now
  references the conformance requirement alongside the manifest
  contract.
- __Schema Versioning Rewritten__: `doc/architecture/schema-versioning.md`
  reframed as implementation-side mechanics.
  Contract-side versioning policy stays in `manifest-contract.md`,
  referenced not duplicated.
  Updated to current `normpic/` layout (was `src/`), aligned to
  v0.1.0 schema (was v1), documents the deferred decision on how
  `schema/v0.1.0.json` relates to the Python schema module, and
  retains the serializer-separation and future-migration sections.
- __TODO Restructured for Conformance Discipline__: `doc/TODO.md`
  gains a "Conformance Fixture Discipline" section near the top
  pointing at `architecture/conformance.md` as the fixture spec.
  Fixtures are now explicitly Phase B implementation work, built
  one fixture at a time per project TDD discipline, with full
  inventory coverage required before Phase D verification.
  Phase A items updated to reflect completion of
  `conformance.md`, `schema/v0.1.0.json`, and the schema-versioning
  rewrite.
- __MVP Scope Decision Documented__: new section in `doc/TODO.md`
  parks compressed-variant collections as a v0.1 open question
  rather than a roadmap item.
  The ongoing wedding gallery work will inform whether this lands
  in v0.1 or rolls to v0.2; design constraints (ergonomic handling,
  minimal schema impact) documented for the in-v0.1 case.
- __Roadmap Gaps Filled__: `doc/ROADMAP.md` gains entries migrated
  from an obsolete Galleria FUTURE document covering progress
  reporting, dry-run mode, configurable filename counter, enhanced
  subsecond-ordering refinements, direct upload from source,
  streaming for large collections, fully remote operation,
  automated archive upload, and async processing pipeline.
- __Data Model Layer Rewritten__: `doc/architecture/data-models.md`
  rewritten as the Python-implementation companion to the manifest
  contract.
  Updated to `normpic/` paths (was `src/`), refreshed dataclass
  shapes to v0.1.0 (relative_path, collection_root,
  original_filename, tag, b2b120: hash, removed errors), kept
  serializer/migration design via cross-reference to
  schema-versioning.md, removed stale test counts, added Related
  projects section.

## 2026-06-08

### v0.1 Contract Redesign Begins

Marks the end of the project hiatus and the start of v0.1 contract
alignment work.

- __Manifest Contract Defined__: new foundational planning artifact
  at `doc/architecture/manifest-contract.md` captures the durable
  v0.1 manifest contract that consumers and reimplementations depend
  on.
  Implementation-agnostic, designed to survive the anticipated Rust
  rewrite and any future Static Site Generator plugin adapters.
- __Contract Changes from Pre-Hiatus State__:
  - Hash: SHA-256 hex replaced with BLAKE2b-120 (15-byte digest)
    encoded as Crockford Base32 uppercase, prefixed with `b2b120:`.
  - Paths: absolute `source_path` and `dest_path` removed from the
    public schema; replaced with `relative_path`
    (collection-relative).
    Source location moves to producer operational state, out of
    contract.
  - Added: `collection_root` top-level field for collection location
    resolution; allows `..` segments at the start for navigating
    from manifest location to collection root.
  - Added: `original_filename` per-pic optional field.
  - Added: `tag` per-pic optional array (reserved, not populated in
    v0.1.0).
  - Removed: `errors`, `warnings`, `processing_status` from the
    manifest.
    Diagnostics now logs-only at runtime; a structured sidecar is
    deferred for a future version.
- __Two-Layer Contract Architecture__: the contract is now split
  into a prose document (`manifest-contract.md`) for semantics and
  rationale, and a JSON Schema artifact (`schema/v0.1.0.json`,
  pending) for mechanical validation.
- __Defensive Decisions Locked__: forward-compatibility seams,
  canonical forms (paths, Crockford case, RFC 3339 timestamps),
  parse-time version semantics, optional/nullable/absent matrix, and
  deterministic-per-implementation ordering are all pinned in the
  contract.
- __Pre-Hiatus MVP Status Reframed__: the pre-hiatus "MVP complete
  with 200 tests" claim is subsumed by the larger v0.1 contract
  alignment work.
  Existing tests still pass against the old contract; alignment to
  the new contract is the Phase B implementation work tracked in
  `doc/TODO.md`.
- __Planning Documents Restructured__:
  - `doc/TODO.md` rewritten to track v0.1 contract alignment with
    sequenced phases and explicit upstream triggers per task.
  - `doc/ROADMAP.md` created to hold post-v0.1 work; TODO no longer
    carries the feature wishlist.
  - `doc/architecture/README.md` updated to index
    `manifest-contract.md` as the first entry under Schema and Data
    Management.
  - `doc/README.md` status block updated to reflect the contract
    redesign in progress.
  - Top `README.md` adjusted: S3 dropped from advertised features
    (deferred post-v0.1, tracked in `ROADMAP.md`).
- __Pre-Hiatus Field-Name Reconciliation Pending__: the existing
  Python implementation may use field names from the pre-hiatus
  contract.
  An audit and alignment PR is the first task in Phase B of the
  sequenced TODO.

## 2025-11-21

### Major Package Restructuring for Parent Project Integration

- __Critical MVP Fix__: Resolved packaging issues blocking parent project integration
  - Restructured from `src/` to conventional `normpic/` package layout  
  - Fixed all 26 files with import issues (`from src.X` → relative/package imports)
  - Created clean API entry point in `normpic/__init__.py` with main exports
  - Updated all test imports from `src.` to `normpic.` package imports
  - __Package Integration Now Working__: `from normpic import organize_photos` functional
- __Package Configuration__: Simplified pyproject.toml with conventional setuptools discovery
- __Quality Assurance__: All 200 tests pass, ruff linting clean, CLI functional with `uv run`
- __Implementation__: 6 systematic commits on `fix/packaging` branch for easy review
- __Documentation__: Updated TODO.md with completion status and success criteria
- __Ready for Parent Projects__: Package can now be installed and imported by gallery builders

## 2025-11-13

### Integration Documentation Completion

- __Documentation Updates__: Completed integration guide organization and indexing
  - Added Integration section to `doc/README.md` with direct links to all 4 integration guides
  - Updated `doc/guides/README.md` to include Integration Guides section
  - Fixed 9 f-string linting issues in performance script
  - All 200 tests passing, MVP integration documentation complete

## 2025-11-12

### Performance Documentation and Real-World Analysis

- __Performance Measurement Script__: Created comprehensive benchmarking system
  - Added `script/performance_test.py` with system resource monitoring (psutil)
  - Automated subprocess execution with memory, CPU, and timing metrics
  - Image size analysis with distribution statistics across size ranges
  - Support for multiple collections (full vs web-optimized) comparison
  - Generates detailed JSON results and human-readable summaries
- __Performance Documentation__: Baseline measurements for real-world wedding collection
  - Added `doc/analysis/performance.md` with hardware specs and benchmark results
  - 645 photos, 21.17GB full resolution vs 2.19GB web-optimized comparison
  - Demonstrated 5.9× speed improvement for smaller files (38.9 vs 229.5 photos/sec)
  - Documented AMD Ryzen 7040U + FireCuda NVMe performance characteristics
- __Timestamp Analysis__: Camera-specific EXIF accuracy documentation
  - Added `doc/analysis/timestamps.md` with timeline verification using reference photos
  - Canon EOS R5 timezone EXIF issue analysis (correct local time, wrong timezone marker)
  - Wedding event timeline validation: 16:10 ceremony vs 16:00 start time
  - Future enhancement plans for EXIF modification and timezone correction
- __Analysis Documentation Structure__: Organized analysis section with hierarchical links
  - Added `doc/analysis/README.md` as analysis section index
  - Updated `doc/README.md` to link analysis section for performance and timestamp documentation
  - Maintains discoverable documentation hierarchy standards
- __Status__: Performance testing infrastructure complete, commit 11 documentation ready

### Enhanced Filesystem Operations and Environment Variable Support

- __Enhanced Symlink Detection__: Added performance optimizations for large directory trees
  - Recursive directory scanning with progress reporting callbacks
  - Added `scan_directory_symlinks()` for comprehensive file type analysis
  - Added `batch_validate_symlinks()` for efficient bulk validation
  - Graceful handling of permission errors and inaccessible files
  - Added 9 comprehensive tests for new enhanced functionality
- __Secure Environment Variable Support__: Implemented NORMPIC_* environment variable parsing
  - Whitelisted approach: only reads specific NORMPIC_SOURCE_DIR, NORMPIC_DEST_DIR, NORMPIC_COLLECTION_NAME, NORMPIC_CONFIG_PATH
  - Environment variables override file configuration (precedence system)
  - All environment variables fully mocked during testing for security
  - Added integration test for config precedence workflow
  - Added 21 unit tests with comprehensive mocking coverage
- __Config Precedence System__: Implemented complete configuration precedence hierarchy
  - Added `load_config_with_full_precedence()` with defaults < file < env < CLI precedence
  - Extended CLI with --source-dir, --dest-dir, --collection-name options
  - CLI arguments now override all other configuration sources
  - Added 2 integration tests for CLI override scenarios
  - Added 3 unit tests for full precedence edge cases
- __Status__: All 200 tests passing, ruff checks passing, commits 8-10 complete

## 2025-11-11

### Error Handling Documentation and Mock Filesystem Testing

- __Comprehensive Error Documentation__: Created user-friendly error handling guides
  - Added `doc/guides/errors.md` with error interpretation and troubleshooting
  - Updated `doc/guides/README.md` to include error handling guide
  - Enhanced `doc/modules/schema.md` with new error schema structure
  - Documented error types, severity levels, and processing status
- __Mock Filesystem Testing__: Added deterministic testing utilities
  - Created comprehensive mock filesystem implementation (MockPath, MockFilesystem)
  - Added 11 tests covering all filesystem operations
  - Enabled testing without real filesystem dependencies
- __Filesystem Utilities__: Completed core filesystem operations
  - Symlink creation and validation with atomic operations
  - Broken symlink detection with recursive scanning
  - File hash computation (SHA-256) with progress callbacks
- __Status__: All 164 tests passing, ruff checks passing, commits 6-7 complete

## 2025-11-10

### Error Handling Refactor and Test Suite Corrections

- __Error Handling Optimization__: Streamlined error handling implementation
  - Replaced complex `ErrorResult` objects with simple `ErrorEntry` dataclass
  - Removed redundant severity field (intrinsic to error type)
  - Simplified manifest schema, ~60% memory reduction
- __Test Suite Filename Format Corrections__: Fixed filename generation tests
- __Removed Handoff Section__: Cleaned up TODO.md after reviewing handoff instructions
- __Fixed Test Expectations__: Updated 7 failing tests to match corrected filename format
  - Single photos with unique timestamps: No `-0` counter (e.g., `ceremony-20241005T163000-i15.heic`)
  - Mixed cameras with different timestamps: No counters needed
  - Burst sequences (same timestamp + same camera): All get counters starting with `-0`
- __Burst Collision Detection Enhancement__: Implemented proper burst sequence handling
  - Modified `_create_ordered_pics()` in photo_manager.py to group by timestamp+camera
  - Photos with same timestamp to the second AND same camera get sequential counters
  - Different cameras at same timestamp remain separate (no counters)
- __File Extension Fix__: Corrected filename generation to preserve original extensions (.heic, .jpg)
- __Test Restructuring__: Updated burst sequence test to use complete workflow instead of incremental filename generation
- __Status__: All 153 tests passing, ruff checks passing

## Previous Entry - 2025-11-10

### Error Handling Implementation Complete (TDD GREEN Phase)

- __Critical Filename Generation Bug Fix__: Discovered and fixed systematic issue with counter logic
  - __Issue__: Filename generation always added `-0` suffix even for unique timestamps
  - __Root Cause__: Logic always called counter function instead of checking if base filename was available
  - __Fix__: Modified `generate_filename()` to only add counters when actual filename conflicts occur
  - __Impact__: Eliminates unnecessary `-0` suffixes in real photo collections
- __Comprehensive Error Handling Implementation__: Full TDD GREEN phase completion
  - `src/util/error_handling.py`: Complete ErrorHandler with severity levels and processing status
  - `src/manager/photo_manager.py`: Integrated error handling throughout photo organization workflow
  - `src/model/manifest.py`: Enhanced with error/warning/processing_status fields
  - `src/serializer/manifest.py`: Updated deserializer to handle new optional fields
- __Error Processing Features__: Production-ready error handling capabilities
  - Graceful handling of unsupported formats (RAW/GIF/MP4) with INFO-level logging
  - Corrupted file detection with WARNING-level logging and continued processing
  - EXIF extraction failures with fallback to filesystem timestamps
  - Comprehensive processing status tracking in manifest output
  - Proper error categorization and summary statistics
- __Test Suite Updates__: Updated all tests to match corrected filename format
  - Fixed filename generation unit tests to expect no counters for unique timestamps
  - Updated integration tests to match corrected behavior
  - All error handling E2E tests passing with comprehensive coverage

## 2025-11-09

### Filesystem Utilities Implementation (Priority 3 TDD)

- __Filesystem Module__: Created `src/util/filesystem.py` with comprehensive utilities
  - `create_symlink()`: Atomic symlink creation with progress reporting
  - `validate_symlink_integrity()`: Symlink validation and target checking  
  - `detect_broken_symlinks()`: Recursive broken symlink detection
  - `compute_file_hash()`: Optimized SHA-256 computation with progress callbacks
- __Atomic Operations__: Symlinks use temporary file + rename for crash safety
- __Performance Optimizations__: 64KB chunk size for optimal hash computation
- __Progress Reporting__: Callback hooks for UI integration
- __Comprehensive Testing__: 23 unit tests + 2 integration tests
  - Full TDD RED-GREEN-REFACTOR cycle implementation
  - E2E workflow testing: symlink creation → validation → broken link detection
  - Error handling tests for edge cases and invalid inputs
- __Documentation Update__: Enhanced `doc/modules/filesystem.md` with usage examples
  - Added API documentation for all new functions
  - Performance optimization details and configuration options
  - Clear separation of concerns vs photo manager responsibilities

## 2025-11-07

### Manifest Loading Functionality (TDD Implementation)

- __Manifest Manager Enhancement__: Added `load_existing_manifest()` function
  - Implemented standalone function for loading manifests from any path
  - Added comprehensive unit tests with schema validation scenarios
  - Improved error handling with specific exception types (ValidationError, JSONDecodeError)
  - Enhanced `save_manifest()` with atomic write operations for data safety
  - Added UTF-8 encoding specification for better file handling
- __Integration Testing__: Created manifest loading workflow tests
  - Added `test/integration/test_manifest_loading_workflow.py`
  - E2E test validates manifest loading, validation, and reuse in photo organization
  - Verified compatibility with existing photo organization workflow
- __TDD Process__: Followed complete RED-GREEN-REFACTOR cycle
  - RED: Created failing E2E and unit tests
  - GREEN: Implemented minimal functionality to pass tests
  - REFACTOR: Added error handling, atomic writes, and better validation

### CLI Implementation (Complete MVP Feature)

- __CLI Implementation__: Full command-line interface for photo organization
  - Implemented `cli/main.py` using Click framework with all operational flags
  - Added `--dry-run`, `--verbose`, `--force`, `--config` flags  
  - Wire CLI to existing photo_manager workflow
  - Updated `main.py` to call CLI interface
- __Configuration Management__: JSON-based configuration system
  - Extended `src/model/config.py` with source_dir/dest_dir fields
  - Added JSON file loading with comprehensive validation
  - Implemented path validation and directory creation
  - Default config path: `./config.json`
- __Dry-run Support__: Added dry-run mode throughout photo workflow
  - Updated `src/manager/photo_manager.py` with dry_run parameter
  - Skip symlink creation in dry-run mode  
  - Generate `manifest.dryrun.json` instead of `manifest.json`
- __Comprehensive Testing__: Full TDD approach for new functionality
  - Added 12 unit tests for config JSON loading/validation (`test/unit/test_config.py`)
  - Added 11 CLI integration tests (`test/integration/test_cli.py`)  
  - All 101 tests passing, including existing photo workflow tests
- __Code Quality__: Clean implementation following project standards
  - Proper error handling and exit codes
  - Summary output: "Processed X pics, Y warnings, Z errors"
  - Ruff linting compliance

## 2025-11-06

### Documentation Update & Cleanup (Post-Feature)

- __Implementation Documentation__: Focused on actual code and complex tests
  - Created `doc/modules/photo-manager.md` - Documents photo_manager.py functions and orchestration
  - Created `doc/test/integration-tests.md` - Documents complex test scenarios and expected behaviors
  - Updated `doc/architecture/module-organization.md` with implemented modules list
- __Architecture Documentation__: Comprehensive updates for photo organization workflow
  - Updated `doc/architecture/README.md` with implemented photo_manager.py workflow
  - Added Manager Pattern documentation for `src/manager/photo_manager.py`
  - Documented temporal ordering, burst preservation, and workflow orchestration
  - Updated system structure diagram to reflect actual implementation
- __Organization Algorithm Documentation__: Created detailed ordering algorithm docs
  - Created `doc/modules/organization.md` with EXIF timestamp → filename → mtime precedence hierarchy
  - Document burst sequence preservation (no camera interleaving)
  - Explain subsecond precision handling and temporal ordering algorithms
- __Documentation Index Updates__: Linked all new documentation properly
  - Updated `doc/README.md` project status to reflect completed photo organization workflow
  - Updated `doc/modules/README.md` and `doc/test/README.md` with new documentation links
  - Document 78 passing tests and readiness for CLI implementation
- __Cleanup Superseded Content__: Removed obsolete ordering logic from deleteme directory
  - Deleted `test_file_processing_dual.py` (complex batch processing superseded)
  - Deleted `file_processing.py` (dual collection logic superseded by simple workflow)
  - Focused cleanup on organization/ordering content replaced by new implementation

### Photo Organization and Processing Workflow (TDD)

- __Architecture Decision__: Implemented proper module organization in `src/manager/`
  - `src/manager/photo_manager.py` - High-level photo organization workflow orchestration
  - Follows documented architecture patterns (manager for orchestration, not catch-all core)
- __Ordering Algorithm__: EXIF timestamp → filename → mtime precedence
  - Subsecond precision handling for fine-grained temporal ordering
  - Graceful fallback when EXIF data unavailable
- __Burst Sequence Preservation__: No camera interleaving on shared timestamps  
  - Same camera photos stay together: [A1,A3,A5,B2,B4,B6] not [A1,B2,A3,B4,A5,B6]
  - Critical for maintaining burst shot continuity
- __Complete Workflow__: Source photos → organized symlinks + manifest.json
  - Integrates EXIF extraction, filename generation, and manifest serialization
  - Schema-validated JSON manifest with full photo metadata
- __Test Coverage__: 78 tests passing (integration + unit tests)
  - Integration tests for complete workflows with burst preservation
  - Unit tests for ordering algorithms and filename generation
  - Mock-based testing for file I/O isolation

## 2025-11-06 (Earlier)

### EXIF Extraction and Filename Generation Implementation (TDD)

- __Architecture Decision__: Implemented template/util split pattern
  - `src/util/exif.py` - Generic EXIF extraction utilities (reusable)
  - `src/template/filename.py` - Domain-specific filename template application
- __Data Models__: Created structured EXIF data models
  - `CameraInfo` dataclass for camera make/model
  - `ExifData` dataclass for structured EXIF metadata
- __EXIF Utilities__: Comprehensive EXIF extraction
  - Extract timestamp, subsecond precision, camera info, timezone offset
  - Graceful handling of missing/corrupted EXIF data
  - Compatible with piexif library (existing project dependency)
- __Filename Templates__: Template-based filename generation
  - Format: `{collection-?}{YYYYMMDDTHHMMSS}{-camera?}{-counter?}.ext`
  - Camera code mapping (Canon R5→r5a, iPhone 15→i15, etc.)
  - Base32 counter system for burst sequences (0-V, 32 photos max)
- __TDD Implementation__: Integration-first approach
  - 5 integration tests for complete workflows
  - 48 unit tests for individual components
  - 68 total tests passing (100% success rate)
- __Test Infrastructure__: Shared fixtures and documentation
  - `create_photo_with_exif` fixture for ephemeral test photos
  - Comprehensive test documentation in `doc/test/`
  - Project-wide fixture availability via conftest.py
- __Specifications__: Adapted from deleteme-normpic-modules reference
  - Extracted specs from existing tests, not direct code copy
  - Modern implementation with structured data models
  - Clean separation of concerns (template vs utility functions)

### Earlier Today

- Project structure initialization with uv, Python 3.12+, ruff
- Added dependencies: click, Pillow, piexif, jsonschema, pytest  
- Created src/ directory structure with model/, core/, manager/, util/, serializer/
- Installed pre-commit hook for commit message validation
- Added deleteme folder cleanup rules to CONTRIBUTE.md
- Designed versioned schema architecture with schema_v1.py approach
- Planned serializer pattern as peer directory to models
- Updated TODO.md with 3-commit implementation plan and migration system design
- Established pre-commit documentation process in CONTRIBUTE.md
- Added JSON schema v0.1.0 and data models (TDD approach)
- Created Pic, Manifest, Config dataclasses with validation
- Implemented ManifestSerializer with JSON serialization and schema validation
- Added comprehensive unit tests (20 passing tests)
- Established versioned schema architecture (schema_v0.py approach)
- Implemented serializer separation pattern (src/serializer/ peer to src/model/)
- Documented data models architecture and schema design decisions
