import json
from pathlib import Path

from jsonschema import Draft202012Validator

from normpic.util.manifest_validate import consumer_normalize as consumer_normalize
from normpic.util.manifest_validate import impl_validate as impl_validate

_TEST_DIR = Path(__file__).parent.parent
CONFORMANCE_DIR = _TEST_DIR / "fixture" / "conformance"
SCHEMA_PATH = _TEST_DIR.parent / "schema" / "v0.1.0.json"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def load_fixture(path: Path) -> dict:
    return json.loads(path.read_text())


def schema_validate(manifest: dict) -> list:
    validator = Draft202012Validator(load_schema())
    return list(validator.iter_errors(manifest))
