# NormPic Roadmap

## Overview

This document captures post-v0.1 planning: features, extensions, and
strategic directions not yet scheduled.
Scheduled work lives in [TODO.md](TODO.md).

Items move between this document and `TODO.md` as scope is decided:

- Items here are anticipated but not yet scheduled.
- When an item is scoped for an upcoming release, it moves to
  `TODO.md` with concrete sequencing and triggers.
- Completed items are recorded in `CHANGELOG.md` or its archives.

Status labels mirror the convention used in the Related projects
section of `architecture/manifest-contract.md`:

- exists: live and shipping.
- planned: scoped or foreseen, not yet implemented.
- deferred: acknowledged, postponed.
- anticipated: foreseen as a likely future direction, not formally
  scoped.

Ordering is weakly organized:
roughly nearer-term first,
but expect to pick and choose rather than work top to bottom.
Where a section is explicitly sequenced, it says so.

## v0.x Contract Extensions

Additive changes to the manifest contract beyond v0.1.0.
Each is described more fully in the deferred section of
`architecture/manifest-contract.md`.

- Ordering provenance field.
  Records the temporal-reconstruction strategy and tiebreaking chain
  used to produce pic order; resolves cross-implementation ordering
  reproducibility.
- URI schemes in `collection_root`:
  - *(for example `s3://`, `https://`, `ssh://`)*.
  - Lets manifests reference non-filesystem-local collections.
  - Depends on the remote origin record question below.
  - Lets manifests reference non-filesystem-local collections.
- Variant collection roots (for example `thumbnail_root`,
  `web_root`, `raw_root`).
  Sibling fields to `collection_root`, each carrying its own
  location.
  If progressive loading (see Long-Term) is ever pursued, it would
  build on this: a resolution ladder is variant roots with an implied
  order.
- Diagnostics sidecar (working name `manifest.report.json`).
  Structured archive for warnings, errors, and processing context.
- Pixel-content hash.
  Alternative or supplementary hash computed over decoded pixel
  data, useful for detecting EXIF-edit cases.
- Cross-variant collection matching (full vs. web, etc.).
  A source shot and its compressed mirror are separate collections
  with separate manifests; their content hashes differ by design, so
  b3c32 identity cannot link them.
  - v0.1 stopgap (consumer-side, no contract change): a consumer
    holding a mirrored pair matches on `relative_path`, which derives
    from EXIF timestamp and camera and so agrees across collections.
    Documented in `guides/manifest-integration.md`, including the
    same-second ordinal caveat that makes it reliable only while both
    collections hold the same set of files.
  - Robust replacement: the pixel-content hash above gives a
    variant-stable identity that does not depend on timestamp
    coincidence.
- Populate `original_filename` in emitted manifests.
  The field is specified in `architecture/manifest-contract.md` and
  validated in the Pic model, but no producer path ever sets it, so
  every v0.1.0 manifest omits it.
  Legal, since the field is optional, but it means the photographer's
  source filename is unrecoverable from a manifest.
- normpic operation config (needs a planning pass before scheduling).
  A persisted config describing a symlink-copy operation (source and
  copy manifest locations, the rename heuristic, the derivation link
  between source and copy) so the operation need not be re-specified
  via CLI or env each run.
  - Open question: the boundary between this and marcustack's
    invocation config, since marcustack owns operation composition for
    the ecosystem.
  - Resolved for now: the relationship lives in marcustack and normpic
    takes CLI/env per run; this item only revisits whether normpic
    should also own a local config later.
  - Decide where it belongs (normpic vs. marcustack) and at what
    version before promoting it from this note.
- Output-bytes integrity hash for the destination tree.
  Distinct from the pic-identity hash; verifies destination integrity
  rather than source identity.
- Sub-grouping within a collection.
  Explicit group structure beyond what flat tags can express.
- Tag hierarchy and external taxonomy.
  Open questions on taxonomy-file location, single-parent versus
  DAG, and namespacing.
  Likely coordinated with zk-notes long-term.
- Provenance file mapping hash to source location.
  Reconsider if remote sources or multi-source merging make it
  valuable.
- Remote origin record.
  Whether manifests record where remote collections live
  - And in what field.
  Origin is durable history; access details are environment-specific
  and go stale, so a manifest carrying them stops being portable.
  A third option is that neither belongs in the manifest and
  resolution is the pipeline's job.
  Unscheduled: revisit when a consumer needs it, not before.

## Implementation-Side Enhancements

No contract impact; producer-internal improvements to NormPic.
Good grab bag of fairly isolated PR-sized improvements.

### Correctness and robustness

- Deletion detection and safe cleanup.
- Multiple error tracking per pic.
- Readable errors for invalid configuration.
  A config that fails schema validation surfaces the raw
  `jsonschema` traceback to the user.
  An empty `collection_name`, for example, prints the failing
  schema fragment and the offending instance rather than saying
  what to fix.
  The fix is to catch validation errors at the CLI boundary and
  report the field and the constraint in plain language.
- Resume capability for failed builds.
- Re-hash heuristic refinement.
  Deterministic stat-skip is implemented: when name, mtime, and size
  match the prior manifest entry, the stored hash is reused; `--force`
  bypasses it.
  A full re-hash of the wedding collection is about 22 seconds for the
  originals and 2.6 for the web set, so the skip is worth real time.
  The refinement is a probabilistic audit that re-hashes a
  stat-matched file with some probability, catching in-place edits
  that preserve mtime and size.
  A flat per-run probability is stateless and contract-free; a bounded
  variant (guarantee a re-hash within N runs) needs a per-pic
  last-verified field, which is a contract extension.

### Timestamps and ordering

- UTC offset support (EXIF, GPS, config).
- Timestamp systematic correction via config.
- Sub-second ordering refinements: camera sequence tag parsing, burst
  detection, multi-camera sync, clock-drift correction, and manual
  reordering of problem sequences.
- Configurable filename counter: base, digit count, and
  lexical-ordering option, for burst capture exceeding the current
  default of 32 photos per timestamp per camera.

### Input handling

- RAW format support.
- Subdirectory handling with tagging.
- Ignore file for excluding pics.
- Camera name mapping configuration.
- EXIF modification and copy creation.

### Performance

- Multithreading, with speedup documentation in `analysis/`.
- EXIF caching, with speedup documentation.

### Interface

- Rich CLI with Textual TUI.
- Progress reporting.
- Webhook notifications on completion.

## Rust Rewrite and Multi-Implementation Distribution

Anticipated reimplementation in Rust, motivated by memory and
distribution.
The manifest contract's implementation-agnostic design exists to make
this transition mechanical rather than a redesign.

The approach is incremental: port the smallest pieces with the largest
memory win first, rather than attempting a full port.
Memory is the primary criterion, CPU time the secondary one.

Sequenced:

- Data models (Pic, Manifest).
  A Python object per pic is expensive at collection scale; Rust
  structs are the largest single win available.
  Self-contained, and the natural home for the manifest validators.
- Aggregation over collections.
  A collection type carrying its own CRUD plus map, filter, reduce,
  and sort, so one call operates over many pics rather than crossing
  the FFI boundary per element.
  Per-element crossing would erase the gain.
- Further hot paths as measurement identifies them.
- Content hashing, once b3c32 has a Rust implementation.
  Not an early target, so b3c32 has time; the data models and
  aggregation come first regardless.

Standing requirement for every Rust addition: ship a compute and memory
benchmark against the pure-Python baseline it replaces, with
methodology and results recorded in `analysis/` so comparisons are
reproducible and accumulate.
A full pure-Python baseline exists to measure against, which makes
normpic the best testbed across the active projects.
These are intended for external writeup; capture them at each addition
rather than reconstructing later.

Distribution targets, once a core exists:

- PyO3 module to replace or supplement the current implementation.
- WASM module for browser and Node consumers.
- Native binary for static distribution.
- C-ABI library for other integrations.
- Cross-compilation to `linux/amd64` and `linux/arm64`.
- SSG plugin adapters, once a WASM build exists.
  A JS-based generator could consume normpic as a package rather than
  shelling out to a binary.

## Remote and Adapter Integrations

Producer-side adapters letting NormPic read from non-local sources.
The motivation is running the pipeline against a collection that never
lives on the machine doing the work.
Credentials come from config, CLI, or environment, never a manifest.
Whether a manifest records a remote origin is an open contract
question, listed under v0.x Contract Extensions.

Sequenced; each step depends on the one above:

- Source abstraction.
  Extract the walk, stat, and file read behind an interface with the
  local filesystem as the only implementation.
  Pure refactor, fixes the shape before any network code exists.
- SSH source (SFTP), read-only.
  First remote: SFTP gives real mtime, so stat-skip works unchanged.
  Depends on streaming file hashing.
  The manifest lives in a local cache keyed by remote identity, since
  a read-only source cannot host one and a manifest is derived data.
- Symlink versus copy for remote sources.
  Nothing local to symlink to, so output is a local cache of pulled
  files or manifest-only.
- Direct source-to-destination transfer.
  One file at a time, so peak local storage is the largest file rather
  than the collection.
- Shared pull cache across pipeline stages.
  Each stage otherwise pulls every photo independently.
- Async pipeline: download, process, upload, overlapped across pics.
- S3-compatible sources (covers B2 and R2).
  No filesystem mtime, and ETag is unreliable as content identity, so
  stat-skip needs a different basis.
- WebDAV sources.
- Proton Drive.
- Archive upload command for originals: idempotent, resumable,
  checksum-verified.

## Long-Term and Speculative

Interesting directions without clear scoping yet.

- Additional metadata tagging systems beyond flat tags.
- Popularity tracking from CDN stats.
- Progressive loading variant generation.
- Automated CI/CD integration.
- Git hooks for automatic processing.
- Manifest content addressing (treating the manifest itself as a
  content-addressed artifact for reproducible deploys).
