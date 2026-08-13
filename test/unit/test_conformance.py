import pytest

from test.helpers.conformance import (
    CONFORMANCE_DIR,
    consumer_normalize,
    impl_validate,
    load_fixture,
    schema_validate,
)
from normpic.util.hash import PREFIX


@pytest.mark.parametrize(
    "subdir",
    ["valid", "invalid", "invalid/impl", "consumer-lenient"],
)
def test_fixture_discovery_matches_disk(subdir):
    """Guard that parametrized discovery sees every fixture on disk.

    The suite discovers fixtures with a non-recursive glob, so an empty
    directory yields zero cases and passes vacuously, and a fixture in
    the wrong directory disappears from its intended check.
    Counting with iterdir keeps this derivation independent of the
    glob the other tests use.
    """
    directory = CONFORMANCE_DIR / subdir
    assert directory.is_dir(), f"{subdir}: fixture directory is missing"
    on_disk = [p for p in directory.iterdir() if p.is_file() and p.suffix == ".json"]
    assert on_disk, f"{subdir}: no fixtures, dependent tests pass vacuously"
    discovered = sorted(directory.glob("*.json"))
    assert sorted(on_disk) == discovered, f"{subdir}: discovery and disk disagree"


@pytest.mark.parametrize("path", sorted((CONFORMANCE_DIR / "valid").glob("*.json")))
def test_valid_fixture_passes_schema(path):
    manifest = load_fixture(path)
    errors = schema_validate(manifest)
    assert not errors, f"{path.name}: expected valid, got {errors}"


@pytest.mark.parametrize("path", sorted((CONFORMANCE_DIR / "invalid").glob("*.json")))
def test_invalid_fixture_rejected_by_schema(path):
    manifest = load_fixture(path)
    errors = schema_validate(manifest)
    assert errors, f"{path.name}: expected invalid, schema accepted"


@pytest.mark.parametrize(
    "path", sorted((CONFORMANCE_DIR / "invalid" / "impl").glob("*.json"))
)
def test_impl_layer_fixture_rejected_by_impl(path):
    manifest = load_fixture(path)
    schema_errors = schema_validate(manifest)
    assert not schema_errors, (
        f"{path.name}: expected schema-accept, got {schema_errors}"
    )
    errors = impl_validate(manifest)
    assert errors, f"{path.name}: expected impl rejection, got none"


@pytest.mark.parametrize(
    "path", sorted((CONFORMANCE_DIR / "consumer-lenient").glob("*.json"))
)
def test_consumer_lenient_fixture_schema_rejects_raw(path):
    manifest = load_fixture(path)
    errors = schema_validate(manifest)
    assert errors, f"{path.name}: expected schema rejection of raw form"


@pytest.mark.parametrize(
    "path", sorted((CONFORMANCE_DIR / "consumer-lenient").glob("*.json"))
)
def test_consumer_lenient_fixture_accepted_after_normalize(path):
    manifest = load_fixture(path)
    normalized = consumer_normalize(manifest)
    errors = schema_validate(normalized)
    assert not errors, f"{path.name}: expected valid after normalize, got {errors}"


def test_null_for_non_nullable_optional_single_type_error():
    path = CONFORMANCE_DIR / "invalid" / "null-for-non-nullable-optional.json"
    manifest = load_fixture(path)
    errors = schema_validate(manifest)
    type_errors = [e for e in errors if "is not of type" in e.message]
    assert len(errors) == 1, (
        f"expected exactly 1 error, got {len(errors)}: {[e.message for e in errors]}"
    )
    assert type_errors, f"expected a type error, got: {[e.message for e in errors]}"


def test_consumer_normalize_crockford_alias_fold():
    manifest = {
        "version": "0.1.0",
        "collection_name": "Alias Test",
        "generated_at": "2025-06-15T12:00:00Z",
        "collection_root": ".",
        "pic": [
            {
                "hash": f"{PREFIX}iIlLoO000000000000000000",
                "relative_path": "img.jpg",
                "original_filename": "img.jpg",
                "size_bytes": 1,
                "mtime": "2024-01-01T00:00:00Z",
            }
        ],
    }
    result = consumer_normalize(manifest)
    assert result["pic"][0]["hash"] == f"{PREFIX}111100000000000000000000"
