# NormPic Development Changelog

Entries for post-v0.1.0 development.
Each entry filed under a date header with the branch that produced it.

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
