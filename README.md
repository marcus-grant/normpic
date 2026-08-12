# NormPic

Organize and rename photo collections with a consistent schema and
durable manifest.

## Overview

NormPic helps you standardize disparate photo collections, whether
from multiple photographers, different cameras, or various sources,
into a unified naming schema and manifest file tracking it.
Organize wedding photos, vacation sets, or any collection of images
with chronological sorting and custom tagging.

v0.1 ships with local-filesystem support.
Remote storage adapters (S3, SSH, Proton Drive, etc.) are anticipated
post-v0.1; see [doc/ROADMAP.md](doc/ROADMAP.md).

## Status

v0.1 contract redesign in progress.
The manifest contract is the durable artifact consumers and
reimplementations depend on; see
[doc/architecture/manifest-contract.md](doc/architecture/manifest-contract.md)
for the full contract and
[doc/TODO.md](doc/TODO.md) for the sequenced alignment work.

## Features

- **Local filesystem support**: read from and write to the local
  filesystem.
- **Consistent naming schema**: apply customizable naming conventions
  across your collection.
- **Chronological sorting**: organize by EXIF timestamps or file
  metadata.
- **Content-addressed identity**: BLAKE3-120 hashes (via the `b3c32`
  library) give every photo a stable, portable identifier independent
  of filename or location.
- **Batch processing**: handle entire photo collections efficiently.

## Documentation

- [Contributing](doc/CONTRIBUTE.md): guidelines for contributing to
  the project (MUST READ to contribute).
- [Manifest Contract](doc/architecture/manifest-contract.md): the
  durable v0.1 manifest contract.
- [Documentation Overview](doc/README.md): project structure,
  architecture, and usage guide with links to each topic index.
- [TODO](doc/TODO.md): v0.1 contract alignment tasks.
- [ROADMAP](doc/ROADMAP.md): post-v0.1 planning.
- [CHANGELOG](doc/CHANGELOG.md): development history.

## License

GPLv3
