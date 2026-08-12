import json
from pathlib import Path

from b3c32 import CROCKFORD32_ALPHABET
from jsonschema import Draft202012Validator

from normpic.util.hash import PREFIX
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


def assert_valid_content_id(value: str) -> None:
    """Assert value is a well-formed NormPic content id.

    Checks the format contract only, never a specific digest: the
    b3-120: prefix, a 24-symbol payload, all symbols in b3c32's
    Crockford alphabet.
    Digest correctness is b3c32's to certify, not normpic's.
    """
    assert value.startswith(PREFIX), f"missing {PREFIX} prefix: {value!r}"
    payload = value[len(PREFIX) :]
    assert len(payload) == 24, f"payload not 24 chars: {payload!r}"
    for ch in payload:
        assert ch in CROCKFORD32_ALPHABET, f"non-Crockford char {ch!r}"
