import pytest

from test.helpers.conformance import (
    CONFORMANCE_DIR,
    impl_validate,
    load_fixture,
    schema_validate,
)


@pytest.mark.parametrize(
    "path", sorted((CONFORMANCE_DIR / "valid").glob("*.json"))
)
def test_valid_fixture_passes_schema(path):
    manifest = load_fixture(path)
    errors = schema_validate(manifest)
    assert not errors, f"{path.name}: expected valid, got {errors}"


@pytest.mark.parametrize(
    "path",
    sorted((CONFORMANCE_DIR / "invalid").glob("*.json"))
)
def test_invalid_fixture_rejected_by_schema(path):
    manifest = load_fixture(path)
    errors = schema_validate(manifest)
    assert errors, f"{path.name}: expected invalid, schema accepted"


@pytest.mark.parametrize(
    "path",
    sorted((CONFORMANCE_DIR / "invalid" / "impl").glob("*.json"))
)
def test_impl_layer_fixture_rejected_by_impl(path):
    manifest = load_fixture(path)
    schema_errors = schema_validate(manifest)
    assert not schema_errors, (
        f"{path.name}: expected schema-accept, got {schema_errors}"
    )
    errors = impl_validate(manifest)
    assert errors, f"{path.name}: expected impl rejection, got none"
