import pytest

from test.helpers.conformance import CONFORMANCE_DIR, load_fixture, schema_validate


@pytest.mark.parametrize(
    "path", sorted((CONFORMANCE_DIR / "valid").glob("*.json"))
)
def test_valid_fixture_passes_schema(path):
    manifest = load_fixture(path)
    errors = schema_validate(manifest)
    assert not errors, f"{path.name}: expected valid, got {errors}"
