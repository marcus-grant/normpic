# NormPic TODO

## Current Status: v0.2 planning

Post-v0.1 is contract-free and opportunistic: see ROADMAP.md.
We will be picking out good next items that are more self contained.
Eventually a picture of v0.2 will form.
Then we will pick out a sequence and remove ROADMAP items.
Those items will be given mechanistic details and
added to this TODO list.
Any contract change lands in
[architecture/manifest-contract.md](architecture/manifest-contract.md),
which holds the frozen v0.1 contract.

## Critical Reference Documents

Authoritative planning artifacts for v0.1:

- [Manifest Contract](architecture/manifest-contract.md): the durable
  v0.1 contract.
- [Conformance Requirement](architecture/conformance.md): defines the
  fixture spec all implementations must satisfy to claim v0.1
  conformance.
- `normpic/schema/v0.1.0.json`: machine-readable schema artifact.
- `test/fixture/conformance/`: fixtures implementing the conformance
  spec.
  Built per Phase B.
- [Schema Versioning](architecture/schema-versioning.md):
  implementation-side migration mechanics (distinct from the
  contract).
- [ROADMAP.md](ROADMAP.md): future planning.
- [CHANGELOG.md](CHANGELOG.md): development history;
  earlier releases archived alongside.

## Development rules

See [CONTRIBUTE.md](CONTRIBUTE.md) for TDD, the quality gate, commits,
QA, and documentation discipline.
Domain rules specific to normpic, not covered there:

- Lazy processing by default: skip unchanged pics.
- Warnings continue; errors stop.

## Tasks

### Fix the source manifest: side effects and missing fields

Two defects that compound.
`--dry-run` writes `manifest.json` into the source directory, because
the source manifest write in `normpic/manager/photo_manager.py` happens
before the dry-run branch is taken.
A dry run creates no symlinks but is not side-effect free.
Separately, `build_source_manifest` in
`normpic/manager/manifest_manager.py` constructs each `Pic` with only
the four required fields.
It never calls `extract_exif_data`, so `timestamp`, `timestamp_source`,
`camera` and `gps` are absent from every source manifest record even
when the file carries EXIF.
The copy path already populates all four.

Together these produced a false producer-bug report.
A stray source manifest in a collection directory is indistinguishable
from a copy manifest until its contents are read closely, and lacking
the optional fields it reads as a producer that discards EXIF.
The tell was `relative_path` holding a raw camera filename rather than
a generated name.
Verified against the wedding collection: copy manifests carry the
fields on 645 of 645 records, all `timestamp_source: exif`; the source
manifest carries none.

This is first in the list because it is the only item with a
demonstrated downstream cost.

- [ ] Branch `fix/source-manifest` from main.
- [ ] Add a suite assertion that a copy manifest built from
      EXIF-bearing photos carries `timestamp`, `timestamp_source` and
      `camera` on every record.
      This passes on the current tree; it is a regression guard, not a
      red test.
      It exists because this gap was found by inspecting a manifest by
      hand rather than by a failing test.
- [ ] Failing test: a dry run against a source directory with no
      manifest leaves no `manifest.json` behind.
- [ ] Move the source manifest write inside the non-dry-run path, or
      guard it.
- [ ] Failing test: a dry run against a source directory with an
      existing manifest leaves it unmodified.
- [ ] Failing test: a source manifest built from an EXIF-bearing photo
      carries `timestamp`, `timestamp_source` and `camera`.
- [ ] Extract EXIF in `build_source_manifest` and pass the fields
      through, matching the copy path.
- [ ] Failing test: a photo without EXIF omits the fields rather than
      emitting nulls, per prefer-absence-over-null.
- [ ] Failing test: `gps` is populated when a photo carries both
      coordinates and omitted when it carries neither.
      Unverified on either path; the wedding collection has no GPS
      EXIF, so this is currently untested rather than known-correct.
- [ ] Document in `doc/architecture/manifest-contract.md` how a source
      manifest is distinguished from a copy manifest.
      A consumer needs a reliable check, not close reading of
      `relative_path`.
- [ ] Remove the dry-run caveat note from `doc/guides/cli.md`.
- [ ] Delete the ROADMAP entry.

### Isolate NORMPIC_ environment variables in the CLI tests

`test/integration/test_cli.py` does not clear the environment, so five
tests fail for any developer with `NORMPIC_SOURCE_DIR` or
`NORMPIC_DEST_DIR` set in their shell.
Env sits above config in the precedence chain, so a live variable
overrides the config the tests set up.

- [ ] Branch `tst/isolate-cli-env` from main.
- [ ] Failing test: confirm the five failures reproduce with the
      variables set, and pass without them.
- [ ] Clear all `NORMPIC_*` variables in a fixture applied to the
      module.
- [ ] Confirm the suite passes both with and without the variables set
      in the shell.

### Clean up the manager modules

`organize_photos` in `normpic/manager/photo_manager.py` is 162 lines
covering source manifest resolution, directory walking, change
detection, hashing, ordering, symlink creation, and manifest writing.
`ManifestManager` mixes manifest I/O with reprocessing decisions and
carries dead methods.
Pure refactor: no behavior change, suite green at every commit.

- [ ] Branch `ref/clean-manager-modules` from main.
- [ ] Delete `needs_reprocessing`, `config_affects_reprocessing`, and
      `destination_file_missing`; no production caller exists for any
      of them.
      Confirm each before deleting.
- [ ] Delete `ManifestManager.compute_file_hash`; it duplicates the
      function in `normpic/util/filesystem.py` and is called only from
      tests.
      Redirect those tests to the util function.
- [ ] Extract source photo discovery from `organize_photos` (walk plus
      extension filter).
- [ ] Extract change detection (stat-skip plus hash reuse).
- [ ] Extract symlink creation.
- [ ] Extract manifest writing.
- [ ] `organize_photos` reduces to orchestration over the extracted
      functions.
- [ ] Full gate green at each commit.

### Populate original_filename on both producer paths

`original_filename` is defined in the schema and validated on the
model, but no producer path sets it.
Consumers pair variant collections on `relative_path` because of this.

- [ ] Branch `ft/original-filename` from main.
- [ ] Failing test: a copy manifest record carries the source file's
      name in `original_filename`.
- [ ] Set it on the copy path, where the source name is in hand.
- [ ] Failing test: a source manifest record carries it too.
- [ ] Confirm the field is omitted, never null, when unavailable.

### Write the copy manifest atomically

The copy manifest is serialized and written directly in
`normpic/manager/photo_manager.py` rather than through
`ManifestManager.save_manifest`, so it misses the temp-file-then-rename
path the source manifest gets.
An interrupted write can leave a partial manifest on disk.
marcustack's stage contract requires output atomicity.

- [ ] Branch `fix/atomic-copy-manifest` from main.
- [ ] Failing test: an interrupted write leaves no partial manifest.
- [ ] Route the copy manifest write through `save_manifest`.
- [ ] Confirm the dry-run manifest filename is preserved.
- [ ] Delete the ROADMAP entry.

### Stabilize pic array ordering across runs

Reported by marcustack: two runs on identical input produce manifests
whose `pic` arrays differ in order.
Content is identical once sorted by `relative_path`, with the same 645
entries and the same hashes, so this is ordering only and no photo is
lost.
Manifests cannot be diffed or byte-compared between runs.

Isolated to the cache path.
Two cold runs into fresh destinations are byte-identical; a warm run
into a populated destination reorders.
The likely cause is the reassembly of stat-skipped and reprocessed
photos in `normpic/manager/photo_manager.py`, not the temporal sort
key, which is deterministic on both branches.
Observed on the copy manifest; the source manifest is untested.

Sorting by `relative_path` before serialization would fix it, but it
would also reorder cold runs, which are currently temporal.
Whether `pic` array order is semantically meaningful or incidental is
a contract question and must be settled first.

- [ ] Read `doc/architecture/manifest-contract.md` for whether `pic`
      order carries meaning. Settle it with the maintainer if the
      contract is silent.
- [ ] Branch `fix/stable-pic-ordering` from main.
- [ ] Failing test: a warm run over a populated destination emits the
      same `pic` order as a cold run over the same input.
- [ ] Fix the reassembly order, or sort before serialization if the
      contract permits reordering cold runs.
- [ ] Failing test: the source manifest holds the same ordering
      guarantee as the copy manifest.
- [ ] Record the ordering guarantee in the contract document if one
      is established.

### Streaming file hashing

`compute_file_hash` reads the whole file into memory and delegates to
b3c32's one-shot `hash_b32`, because b3c32 exposes no incremental
hasher.
Fine at wedding-gallery scale, but it loads large originals entirely
into memory and makes remote sources impossible: a NAS file cannot be
buffered whole to be hashed.
Blocked on b3c32 gaining a streaming or update-style entry point.

- [ ] Raise the streaming API request with the b3c32 maintainer.
- [ ] Branch `ft/streaming-file-hash` from main once it lands.
- [ ] Restore `compute_file_hash`'s chunked read loop, delegating
      chunks to the streaming hasher.
- [ ] Restore `progress_callback`.
      The signature already carries `chunk_size` and
      `progress_callback` as accepted-but-unused params, so this is
      not a signature change.
- [ ] Re-enable `test_compute_file_hash_custom_chunk_size` and
      `test_compute_file_hash_progress_callback`.
- [ ] Delete the ROADMAP entry.

### Detect config changes that affect output

Reprocessing decisions currently key on file identity alone.
A config change that alters output (filename pattern, collection name,
symlink versus copy) leaves existing output stale while every stat and
hash check still matches, so nothing regenerates.
`ManifestManager.config_affects_reprocessing` was written toward this
and never wired up.

- [ ] Branch `ft/config-change-detection` from main.
- [ ] Decide which config fields affect output; document the list.
- [ ] Failing test: changing an output-affecting field forces
      reprocessing; changing an unrelated field does not.
- [ ] Hash the output-affecting fields and store the digest.
- [ ] Compare on run and reprocess on mismatch.
