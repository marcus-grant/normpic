# Field-Name Reconciliation Audit

Working document for `ref/field-name-reconciliation`.
Dropped by `Chr: drop field-rename-audit.md` at PR close.

## Grep Commands

```bash
DIRS="normpic/model normpic/serializer normpic/manager"
TEST="test/unit test/integration"

grep -rn '"pics"'               $DIRS $TEST
grep -rn '\.pics\b'            $DIRS $TEST
grep -rn '"latitude"'          $DIRS $TEST
grep -rn '"longitude"'         $DIRS $TEST
grep -rn '\.latitude\b\|\.longitude\b' $DIRS $TEST
grep -rn '"source_path"'       $DIRS $TEST
grep -rn '"dest_path"'         $DIRS $TEST
grep -rn '"errors"'            $DIRS $TEST
grep -rn '"warnings"'          $DIRS $TEST
grep -rn '"processing_status"' $DIRS $TEST
grep -rn '"size_bytes"'        $DIRS $TEST   # control: plural intentional
```

Post-rename verification (expect 0 hits):

```bash
# After R1
grep -rn '"pics"\|\.pics\b' $DIRS $TEST
# After R2
grep -rn '"latitude"\|"longitude"\|\.latitude\b\|\.longitude\b' $DIRS $TEST
```

---

## Renames

### R1: pics -> pic (Manifest array)

`pics -> pic, files: [normpic/model/manifest.py, normpic/model/schema_v0.py,
normpic/serializer/manifest.py, normpic/util/error_handling.py,
test/unit/test_error_handling.py, test/unit/test_manifest_manager.py,
test/unit/test_models.py, test/unit/test_schema.py,
test/unit/test_serializer.py,
test/integration/test_exif_filename_workflow.py,
test/integration/test_manifest_loading_workflow.py,
test/integration/test_photo_organization_workflow.py]`

Specific hits:

- `normpic/model/manifest.py:18` -- dataclass field `pics: List[Pic]`
- `normpic/model/manifest.py:33` -- `to_dict()` key `"pics"` and
  attribute `self.pics`
- `normpic/model/schema_v0.py:109` -- MANIFEST_SCHEMA required list
- `normpic/model/schema_v0.py:133` -- MANIFEST_SCHEMA properties key
- `normpic/serializer/manifest.py:55` -- `data["pics"]` in deserialize
- `normpic/manager/photo_manager.py:47` -- `existing_manifest.pics`
  attribute access
- `normpic/util/error_handling.py:132,134,137` -- `"pics"` key checks
- `test/unit/test_error_handling.py:63,73` -- `"pics"` in test dict
- `test/unit/test_manifest_manager.py:22,73,101` -- `"pics"` in
  fixture dicts; `result.pics` at line 37
- `test/unit/test_models.py:117` -- `manifest.pics`; `result["pics"]`
  at lines 147-148
- `test/unit/test_schema.py:18,48` -- `"pics"` in test dicts
- `test/unit/test_serializer.py:46,54` -- `parsed["pics"]`,
  `"pics"` in dict; `.pics` attribute at lines 78-79, 111-114
- `test/integration/test_exif_filename_workflow.py:127,130` --
  `manifest.pics`
- `test/integration/test_manifest_loading_workflow.py:49` --
  `"pics"` in fixture dict; `.pics` attribute at lines 75, 86,
  119, 122, 137, 140, 153, 163
- `test/integration/test_photo_organization_workflow.py:69,87,99,113,
  167,170,171,214,224` -- `manifest.pics`, `deserialized.pics`

### R2: latitude/longitude -> lat/lon (GPS dict keys)

`latitude -> lat, files: [normpic/manager/photo_manager.py]`
`longitude -> lon, files: [normpic/manager/photo_manager.py]`

Specific hits:

- `normpic/manager/photo_manager.py:359` -- `"latitude": exif_data.gps_latitude`
- `normpic/manager/photo_manager.py:360` -- `"longitude": exif_data.gps_longitude`

No test files construct GPS dicts with these keys.
Note: this is also a latent bug fix.
Both `normpic/model/schema_v0.py` and `schema/v0.1.0.json` already
require `lat`/`lon`; the current producer would fail schema validation
on any manifest containing GPS data.

---

## Drops

### D1: Manifest.errors

`errors, concept: global error list attached to the manifest, files:
[normpic/model/manifest.py, normpic/model/schema_v0.py,
normpic/serializer/manifest.py, normpic/util/error_handling.py,
test/unit/test_error_handling.py, test/unit/test_schema.py,
test/unit/test_serializer.py,
test/integration/test_manifest_loading_workflow.py]`

Specific hits (out-of-scope; for follow-on PR reference):

- `normpic/util/error_handling.py:143` -- reads `manifest_data["errors"]`
  to validate it is a list; dangling read if D1 is dropped without
  updating this site

Defer: `ref/manifest-model-v01-contract`.

### D2: Manifest.warnings

`warnings, concept: global warning list attached to the manifest, files:
[normpic/model/manifest.py, normpic/model/schema_v0.py,
normpic/serializer/manifest.py]`

Defer: `ref/manifest-model-v01-contract`.

### D3: Manifest.processing_status

`processing_status, concept: aggregate processing stats (total_files,
processed_successfully, etc.), files: [normpic/model/manifest.py,
normpic/model/schema_v0.py, normpic/serializer/manifest.py,
normpic/manager/photo_manager.py]`

Defer: `ref/manifest-model-v01-contract`.

### D4: Pic.errors

`errors, concept: per-pic error list, files: [normpic/model/pic.py,
normpic/model/schema_v0.py, normpic/serializer/manifest.py,
test/unit/test_models.py, test/unit/test_schema.py,
test/unit/test_serializer.py, test/unit/test_error_handling.py,
test/integration/test_manifest_loading_workflow.py]`

Defer: `ref/pic-model-v01-contract`.

### D5: Pic.source_path

`source_path, concept: absolute filesystem path to source photo
(operational state; excluded from v0.1 artifact per contract
"Permanently out of scope" list), files: [normpic/model/pic.py,
normpic/model/schema_v0.py, normpic/serializer/manifest.py,
test/unit/test_models.py, test/unit/test_schema.py,
test/unit/test_serializer.py, test/integration/test_manifest_loading_workflow.py]`

Not a rename target: relative_path is computed from source_path by
stripping collection_root, not renamed from it.
Defer: `ref/pic-model-v01-contract`.

### D6: Pic.dest_path

`dest_path, concept: generated normalized destination filename
(operational state; no v0.1 Pic field maps to this concept), files:
[normpic/model/pic.py, normpic/model/schema_v0.py,
normpic/serializer/manifest.py, test/unit/test_models.py,
test/unit/test_schema.py, test/unit/test_serializer.py,
test/integration/test_manifest_loading_workflow.py,
test/integration/test_exif_filename_workflow.py,
test/integration/test_photo_organization_workflow.py]`

Defer: `ref/pic-model-v01-contract`.

---

## Commit Body Notes

### R2 GPS rename

Include this bullet in the `Ref: rename latitude/longitude to lat/lon`
commit body:

- Fixes latent producer bug: both schema_v0.py and schema/v0.1.0.json
  already require lat/lon; the pre-rename code path would produce a
  schema-invalid manifest for any pic carrying GPS metadata.
