from dave_data.core import compute


def test_compute():
    assert compute([b"a", b"bc", b"abc"]) == b"abc"
