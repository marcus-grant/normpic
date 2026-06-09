# NormPic Documentation

## Overview

NormPic normalizes photo collections by:

- Extracting temporal and camera metadata from photos
- Generating standardized filenames based on timestamps
- Creating symlinks with consistent naming patterns
- Producing JSON manifests for integration with other tools

## Architecture Principles

- **Manifest-Centric Design**: all decisions flow through JSON
  Schema-validated manifests, with the durable contract defined in
  [architecture/manifest-contract.md](architecture/manifest-contract.md).
- **Protocol-Based Integration**: parent projects provide
  implementations for external concerns.
- **TDD Approach**: integration tests first, then unit tests
  following RED-GREEN-REFACTOR.
- **Lazy Processing**: skip unchanged photos based on timestamps and
  hashes.

## Documentation Structure

This documentation follows a hierarchical linking structure:

- All documents link from project root `README.md` to
  `doc/README.md`.
- Each `doc/` subdirectory has its own `README.md` serving as an
  index.
- Follow links: topic to subtopic to specific document, no direct
  deep linking.
- This ensures the entire documentation tree is discoverable
  systematically.

## Documentation Index

### Project Management

- [TODO.md](TODO.md): v0.1 contract alignment tasks with sequenced
  phases and triggers.
- [ROADMAP.md](ROADMAP.md): post-v0.1 planning (contract extensions,
  Rust rewrite, remote adapters, long-term direction).
- [CONTRIBUTE.md](CONTRIBUTE.md): contribution guidelines (MUST READ
  for developers).
- [CHANGELOG.md](CHANGELOG.md): daily development log.

### Architecture

- [Architecture Overview](architecture/README.md): system design and
  key decisions, including the manifest contract.

### Modules

- [Module Documentation](modules/README.md): technical documentation
  for each module.

### Testing

- [Testing Overview](test/README.md): TDD approach, fixtures, and
  patterns.

### Guides

- [User and Developer Guides](guides/README.md): CLI usage,
  configuration, and basic workflows.

### Integration

- [Parent Project Integration](guides/integration.md): complete
  workflow for integrating NormPic into static site projects.
- [Parent Project Setup](guides/parent-project-setup.md): setup
  instructions for uv integration with parent projects.
- [Manifest Integration](guides/manifest-integration.md): working
  with NormPic manifest data in custom applications.
- [Gallery Builder Integration](guides/gallery-builder-integration.md):
  building custom gallery generators that consume NormPic output.

### Analysis

- [Performance and Timestamp Analysis](analysis/README.md):
  real-world performance benchmarks, timestamp accuracy analysis,
  and systematic offset documentation.

## Project Status

**v0.1 Contract Redesign In Progress**

The manifest contract has been redesigned post-hiatus.
The existing Python implementation (200+ tests passing against the
pre-hiatus contract) is being aligned to the new contract.

See
[architecture/manifest-contract.md](architecture/manifest-contract.md)
for the durable v0.1 contract, [TODO.md](TODO.md) for the sequenced
alignment work, [ROADMAP.md](ROADMAP.md) for post-v0.1 planning, and
[CHANGELOG.md](CHANGELOG.md) for detailed development progress.

## Related Projects

- **Galleria**: static gallery builder that consumes NormPic
  manifests.
  Primary downstream consumer.
- **personal-site**: site stack integrating Galleria output at a
  subdomain.
- **composer / marcustack**: shell orchestration layer running the
  NormPic-then-Galleria pipeline.

See the [Related projects](architecture/manifest-contract.md#related-projects)
section of the manifest contract for the full ecosystem map with
current statuses.