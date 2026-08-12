"""Test factories for constructing valid model instances."""

from dataclasses import replace
from normpic.model.pic import Pic
from normpic.util.hash import PREFIX

DEFAULT_PIC = Pic(
    hash=f"{PREFIX}AAAAAAAAAAAAAAAAAAAAAAAA",
    size_bytes=1024,
    mtime="2023-11-04T22:04:16Z",
    relative_path="subdir/photo.jpg",
)


def make_pic(**overrides) -> Pic:
    """Return a copy of DEFAULT_PIC with fields overridden."""
    return replace(DEFAULT_PIC, **overrides)
