# NormPic Roadmap

## Overview

This document captures post-v0.1 planning: features, extensions, and
strategic directions that are intentionally out of scope for the v0.1
contract alignment work tracked in [TODO.md](TODO.md).

Items move between this document and `TODO.md` as scope is decided:

- Items here are anticipated but not yet scheduled.
- When an item is scoped for an upcoming release, it moves to
  `TODO.md` with concrete sequencing and triggers.
- Completed items are recorded in `CHANGELOG.md`.

Status labels mirror the convention used in the Related projects
section of `architecture/manifest-contract.md`:

- exists: live and shipping.
- planned: scoped or foreseen, not yet implemented.
- deferred: acknowledged, postponed.
- anticipated: foreseen as a likely future direction, not formally
  scoped.

The ordering within each section below is not prioritized; treat the
content as a catalog of intent, not a sequence.

## v0.x Contract Extensions

Additive changes to the manifest contract beyond v0.1.0.
Each is described more fully in the deferred section of
`architecture/manifest-contract.md`.

- Ordering provenance field.
  Records the temporal-reconstruction strategy and tiebreaking chain
  used to produce pic order; resolves cross-implementation ordering
  reproducibility.
- URI schemes in `collection_root` (for example `s3://`, `https://`,
  `ssh://`).
  Lets manifests reference non-filesystem-local collections.
- Variant collection roots (for example `thumbnail_root`,
  `web_root`, `raw_root`).
  Sibling fields to `collection_root`, each carrying its own
  location.
- Diagnostics sidecar (working name `manifest.report.json`).
  Structured archive for warnings, errors, and processing context.
- Pixel-content hash.
  Alternative or supplementary hash computed over decoded pixel
  data, useful for detecting EXIF-edit cases.
- Cross-variant collection matching (full vs. web, etc.).
  A source shot and its compressed mirror are separate collections
  with separate manifests; their content hashes differ by design, so
  b3c32 identity cannot link them.
  - v0.1 stopgap (consumer-side, no contract change): galleria maps a
    web pic to its full counterpart by timestamp across the two
    manifests.
    This holds only while EXIF timestamp and sub-second precision
    survive the pipeline unchanged into both manifests; verify that
    invariant when relying on it.
  - Robust replacement: the pixel-content hash above gives a
    variant-stable identity that does not depend on timestamp
    coincidence.
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

## Implementation-Side Enhancements

No contract impact; producer-internal improvements to NormPic.

- Rich CLI with Textual TUI.
- Multithreading with speedup documentation in `analysis/`.
- EXIF caching with speedup documentation.
- Configurable symlink versus copy behavior.
- Streaming file hashing via a b3c32 streaming API.
  The v0.1 content-id cutover made compute_file_hash read the whole
  file into memory and delegate to b3c32's one-shot hash_b32, because
  b3c32 exposes no incremental hasher.
  This is fine at wedding-gallery scale but loads large originals
  (RAW files can be tens of MB) entirely into memory.
  - Depends on b3c32 gaining a streaming or update-style entry point;
    coordinate with the b3c32 maintainer, this is a library request
    first and a normpic change second.
  - When available, restore compute_file_hash's chunked read loop and
    its progress_callback, delegating chunks to the streaming hasher
    instead of reading all bytes.
  - Re-enable the two skipped tests in test_filesystem_utils:
    test_compute_file_hash_custom_chunk_size and
    test_compute_file_hash_progress_callback.
  - The compute_file_hash signature already carries chunk_size and
    progress_callback as accepted-but-unused params, reserved for this
    work, so restoring streaming is not a signature change.
  - Distinct from the collection-level "streaming processing for very
    large collections" under Long-Term; this is per-file hash
    streaming, that is whole-collection.
- UTC offset support (EXIF, GPS, config).
- Timestamp systematic correction via config.
- RAW format support.
- Mirror variant handling (web-optimized versions).
- EXIF modification and copy creation.
- Camera name mapping configuration.
- Multiple error tracking per pic.
- Resume capability for failed builds.
- Webhook notifications on completion.
- Subdirectory handling with tagging.
- Deletion detection and safe cleanup.
- Ignore file for excluding pics.
- Progress reporting.
- Dry-run preview mode.
- Configurable filename counter.
  - Counter base, digit count, and lexical-ordering option.
    - Useful for high-frequency burst capture.
    - Exceeding the current default of 32 photos per time-stamp per camera.
- Enhanced sub-second-ordering refinements.
  - Camera sequence tag parsing, automatic burst detection, multi-camera sync
  - Clock-drift correction, and manual reordering of problem sequences.
- Re-hash heuristic (hash-reuse on stat match).
  Deterministic stat-skip is implemented in v0.1: when a source
  file's name, mtime, and size match its prior manifest entry, the
  stored hash is reused instead of re-reading and re-hashing the
  file; `--force` bypasses it.
  - Measured motivation: a full re-hash of the wedding collection is
    about 22 seconds for the full-size originals and 2.6 seconds for
    the web-compressed set; the stat-skip removes that cost on
    unchanged files.
  - Future refinement: a probabilistic audit that re-hashes a
    stat-matched file with some probability, catching in-place edits
    that preserve mtime and size.
    A flat per-run probability is stateless and contract-free.
    A bounded variant (guarantee a re-hash within N runs) needs a
    per-pic last-verified field, which is a v0.x contract extension,
    not an implementation-only change.

## Rust Rewrite and Multi-Implementation Distribution

Anticipated reimplementation of NormPic in Rust, motivated by
multi-context distribution and performance.
The manifest contract's implementation-agnostic design exists to make
this transition mechanical rather than a redesign.

- Rust core implementing the current manifest contract.
- WASM module for browser and Node consumers.
- Native binary for static distribution (`curl | install` style).
- PyO3 Python module to replace or supplement the current
  implementation.
- C-ABI library for other integrations.
- Cross-compilation to `linux/amd64` and `linux/arm64`.

### First Rust module: Pic and Pic collections

The chosen entry point for Rust, ahead of a full port.
Pic (the deserialized manifest record) and collections of Pic are the
low-hanging fruit: self-contained, memory-heavy at scale, and the
natural home for the manifest validators.

Rationale:

- Memory is the primary expected win: Rust structs for large Pic
  collections instead of Python objects.
  Compute gains are likely secondary but real.
- The win compounds if the Rust collection type carries its own CRUD
  plus map/filter/reduce/sort, so a single Python-to-Rust call
  operates over many Pics at once rather than crossing the FFI
  boundary per element.
  Design the module around bulk operations, not per-Pic calls.
- This is the best experimental testbed across the active projects for
  measuring Rust-versus-Python compute and memory, because a full
  pure-Python baseline already exists to compare against.

Practice for every Rust addition (standing requirement):

- Each Rust module or function that goes into use ships with a
  compute-and-memory benchmark against the pure-Python baseline it
  replaces or supplements.
- Record the methodology and results in `analysis/`, versioned, so the
  comparison is reproducible and accumulates over time.
- These measurements are intended for external writeup (blog, social);
  capture them at the point of each addition rather than
  reconstructing later.

### SSG Integrations (post-Rust-port)

These ride on top of the Rust core via WASM or native integration.

- 11ty plugin (npm package wrapping WASM core).
- Hugo plugin (WASM or native Go integration).
- Astro plugin.
- Zola plugin.
- Galleria as an SSG plugin rather than a separate Python program.

## Remote and Adapter Integrations

Producer-side adapters letting NormPic read from and write to
non-local sources.
At the contract level, these surface through the future
`collection_root` URI schemes; at the implementation level, they are
new producer code paths.

- S3-compatible source and destination adapter.
- SSH/SFTP adapter.
- Proton Drive integration.
- Direct upload from source to object storage with no local intermediate.
- Streaming processing for very large collections.
- Operation entirely from remote storage.
  Originals live in a remote archive, are downloaded for processing
  only as needed, and are uploaded to the public destination without
  keeping local copies.
- Automated archive upload command for originals.
  Preserves source directory structure and filenames, idempotent
  (skips already-uploaded), resumable, with checksum verification.
- Async processing pipeline.
  Per pic: download, process, upload.
  Parallel across pics so the next download runs while the current
  one processes and uploads.
  Handles collections that exceed local storage.
- Backblaze B2 integration.
- Cloudflare R2 integration.

## Long-Term and Speculative

Interesting directions without clear scoping yet.

- Additional metadata tagging systems beyond flat tags.
- Popularity tracking from CDN stats.
- Progressive loading variant generation.
- Automated CI/CD integration.
- Git hooks for automatic processing.
- Manifest content addressing (treating the manifest itself as a
  content-addressed artifact for reproducible deploys).
