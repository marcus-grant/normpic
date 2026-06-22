import pytest
from normpic.util.hash import b2b120_hash, b2b120_encode_digest


def test_encoder_all_zeros_fixed_width():
    assert b2b120_encode_digest(b"\x00" * 15) == "0" * 24


def test_encoder_all_ones_fixed_width():
    assert b2b120_encode_digest(b"\xff" * 15) == "Z" * 24


def test_output_length_invariant():
    for i in range(256):
        assert len(b2b120_hash(bytes([i]))) == 31


@pytest.mark.parametrize(
    "data,expected",
    [
        (b"", "b2b120:PZDRE6BC90T0BS0FGG0ZM7Y9"),
        (b"Hello, World!", "b2b120:D7GS0E632ZGYMQAVRXHYZ315"),
        (b"\xff", "b2b120:N07C0CD6R447SA6JT1CEVAWW"),
        (b"\x00" * 5, "b2b120:DGGXXPQBAP0A56H3CJKG23P6"),
        (b"\x00" * 4099, "b2b120:DCJF8WQMWPFWGA3ZTB62HJA2"),
        (b"\xaa" * 4099, "b2b120:SXBV2Q0G5PZNCC60ED9AXGBZ"),
        (b"abcdefghijklmno", "b2b120:BDK03DC3KTTBN8T7FJSYQS38"),
        (b"\x55", "b2b120:Q7G303N6ZTD10Y24XE57PJJB"),
    ],
)
def test_hash_vectors(data, expected):
    assert b2b120_hash(data) == expected


def test_output_has_b2b120_prefix():
    assert b2b120_hash(b"").startswith("b2b120:")
    assert b2b120_hash(b"any data").startswith("b2b120:")


def test_suffix_has_no_lookalike_chars():
    for data in [b"", b"Hello, World!", b"\x55", b"\xaa" * 4099]:
        suffix = b2b120_hash(data)[7:]
        for ch in "ILOU":
            assert ch not in suffix
