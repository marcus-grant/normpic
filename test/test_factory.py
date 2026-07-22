"""Tests for the Pic test factory."""

from dataclasses import fields

from normpic.model.pic import Pic, MISSING
from test.factory import DEFAULT_PIC, make_pic


class TestPicFactory:
    """Test DEFAULT_PIC and make_pic behavior."""

    def test_pic_field_set_is_known(self):
        """Pins the Pic field set. If this reds, the model gained or
        lost a field; update DEFAULT_PIC, make_pic coverage, and the
        expected set here to reflect the new contract."""
        expected = {
            "hash",
            "size_bytes",
            "mtime",
            "relative_path",
            "timestamp",
            "timestamp_source",
            "camera",
            "gps",
            "original_filename",
            "tag",
        }
        actual = {f.name for f in fields(Pic)}
        assert actual == expected, (
            f"Pic fields changed: added {actual - expected}, "
            f"removed {expected - actual}"
        )

    def test_default_pic_is_contract_valid(self):
        """DEFAULT_PIC constructs and carries required fields."""
        assert DEFAULT_PIC.hash.startswith("b2b120:")
        assert DEFAULT_PIC.size_bytes > 0
        assert DEFAULT_PIC.mtime
        assert DEFAULT_PIC.relative_path

    def test_make_pic_no_overrides_equals_default(self):
        """make_pic() with no args reproduces DEFAULT_PIC."""
        assert make_pic() == DEFAULT_PIC

    def test_make_pic_overrides_only_named_field(self):
        """An override changes its field and leaves all others intact."""
        pic = make_pic(size_bytes=99)
        assert pic.size_bytes == 99
        for f in fields(Pic):
            if f.name == "size_bytes":
                continue
            assert getattr(pic, f.name) == getattr(DEFAULT_PIC, f.name), (
                f"{f.name} changed unexpectedly"
            )

    def test_make_pic_does_not_mutate_default(self):
        """Overriding calls never mutate DEFAULT_PIC, by value or
        by shared reference to a mutable field."""
        # DEFAULT_PIC is scalar-only today so aliasing can't occur;
        # this guards against a future mutable default slipping in.
        snapshot = {f.name: getattr(DEFAULT_PIC, f.name) for f in fields(Pic)}
        make_pic(size_bytes=1)
        make_pic(relative_path="other/path.jpg")
        make_pic(tag=["x"], gps={"lat": 1.0, "lon": 2.0})
        for name, original in snapshot.items():
            current = getattr(DEFAULT_PIC, name)
            assert current is original, f"{name} reference changed"
            assert current == original, f"{name} value changed"

    def test_make_pic_preserves_missing_sentinel(self):
        """original_filename stays MISSING when not overridden."""
        assert make_pic().original_filename is MISSING

    def test_make_pic_can_override_missing_field(self):
        """original_filename can be set via override."""
        pic = make_pic(original_filename="photo.jpg")
        assert pic.original_filename == "photo.jpg"

    def test_missing_sentinel_is_singleton(self):
        """MISSING compares equal to itself; the field-equality
        loop in this suite depends on it."""
        assert MISSING == MISSING
        assert make_pic().original_filename == DEFAULT_PIC.original_filename
