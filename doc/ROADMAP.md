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

