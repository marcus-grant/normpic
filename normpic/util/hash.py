# normpic/util/hash.py
"""
NormPic content-id wrapper over b3c32.

b3c32 owns hashing and Crockford encoding.
This module adds only the NormPic-boundary concern: the b3-120: prefix
on the content id.

Author: Marcus Grant
Created: 2026-07-21
License: Apache-2.0
"""

import b3c32

PREFIX = "b3c32:"
_BITS = 120


def content_id(data: bytes) -> str:
    """Return the prefixed 120-bit content id for data."""
    return f"{PREFIX}{b3c32.hash_b32(data, _BITS)}"
