# test/unit/test_hash.py
"""
Tests for the NormPic content-id wrapper over b3c32.

The wrapper's only job is the b3-120: prefix; hashing and encoding are
b3c32's, certified in b3c32.
These cover the wrapper surface (the prefix and basic shape) and the
verify_conformance tripwire that fails the suite if b3c32's certified
120-bit surface moves under us.

Author: Marcus Grant
Created: 2026-07-21
License: Apache-2.0
"""

import b3c32

from normpic.util.hash import content_id, PREFIX


def test_content_id_has_prefix():
    """The wrapper prepends the b3-120: prefix to the bare code."""
    assert content_id(b"").startswith(PREFIX)
    assert content_id(b"any data").startswith(PREFIX)


def test_content_id_prefixes_the_bare_b3c32_code():
    """content_id is exactly the prefix on b3c32's bare 120-bit code."""
    data = b"any data"
    assert content_id(data) == PREFIX + b3c32.hash_b32(data, 120)


def test_verify_conformance_passes():
    """b3c32's certified 120-bit surface has not drifted under us."""
    b3c32.verify_conformance()

