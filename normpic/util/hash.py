import hashlib

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _encode(digest: bytes) -> str:
    n = int.from_bytes(digest, "big")
    chars = (len(digest) * 8 + 4) // 5
    result = []
    for _ in range(chars):
        result.append(_CROCKFORD[n & 0x1F])
        n >>= 5
    return "".join(reversed(result))


def b2b120_encode_digest(digest: bytes) -> str:
    return _encode(digest)


def b2b120_hash(data: bytes) -> str:
    return "b2b120:" + _encode(hashlib.blake2b(data, digest_size=15).digest())
