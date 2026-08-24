# NormPic Development Changelog

Entries for post-v0.1.0 development.
Each entry filed under a date header with the branch that produced it.

## 2026-08-24

### Planning

- Consolidated the dry-run side effects and source-manifest EXIF
  gaps into one TODO item, placed first.
  They compound: a stray source manifest lacking the optional fields
  reads as a copy manifest produced by a broken producer, and a
  consumer reported exactly that.
  Verified against the wedding collection: copy manifests carry
  `timestamp`, `timestamp_source` and `camera` on 645 of 645
  records, all `timestamp_source: exif`; source manifests carry
  none.
- Added a regression guard to that item asserting the copy path
  populates those fields, since the gap was found by inspecting a
  manifest by hand rather than by a failing test.
- Dropped the `original_filename` TODO item.
  The field is unpopulated because relating renditions to originals
  is an open scope question, not because the implementation is
  missing.
- Recorded identity, provenance and collection-level claims as one
  ROADMAP entry under contract extensions.

## 2026-08-14

### fix/cli-entry

- Moved `cli/main.py` to `normpic/cli.py`, inside the package.
  The CLI was excluded from the distribution by `packages.find`,
  so `uv tool install` exposed no executable.
- Added `normpic/__main__.py` for `python -m normpic`.
- Declared the `normpic` console script in `[project.scripts]`.
- Deleted the root `main.py` shim and repointed
  `script/performance_test.py` at `python -m normpic`.
- Corrected `doc/architecture/package-structure.md` and documented
  installation and all invocation forms in `doc/guides/cli.md`.
- Moved `schema/` to `normpic/schema/` so it ships with the package.
  The installed CLI crashed on a missing schema file, since the root
  `schema/` directory was never part of the distribution.
- Repointed all schema path resolution at the package location:
  the serializer, the test helper's exported `SCHEMA_PATH`, and
  `script/check_schema.py`.
- Verified from a real `uv tool install`: the `normpic` executable
  runs and loads the schema from the installed package.

## Archive

- [changelog-v0.1.0.md](changelog-v0.1.0.md): development through v0.1.0 release.
