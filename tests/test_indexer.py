import pytest

from makeproto.indexer import Indexer


@pytest.fixture
def indexer():
    return Indexer(start=10, idxs=[])


def test_reserve_int_greater_than_start(indexer):
    indexer.reserve(11)
    assert 11 in indexer._reserveds


def test_reserve_int_equal_or_less_than_start(indexer):
    indexer.reserve(10)
    indexer.reserve(9)
    assert 10 not in indexer._reserveds
    assert 9 not in indexer._reserveds


def test_reserve_range_fully_above_start(indexer):
    r = range(12, 15)
    indexer.reserve(r)
    assert any(x == r for x in indexer._reserveds)


def test_reserve_range_partially_below_start(indexer):
    indexer.reserve(range(8, 14))
    # Should add truncated range starting at 11 (start=10 +1)
    assert any(
        isinstance(x, range) and x.start == 11 and x.stop == 14
        for x in indexer._reserveds
    )


def test_reserve_range_fully_below_start(indexer):
    indexer.reserve(range(5, 9))
    assert not any(isinstance(x, range) for x in indexer._reserveds)


def test_overlap_ranges_and_ints(indexer):
    indexer.reserve(range(15, 20))
    indexer.reserve(range(18, 22))
    indexer.reserve(19)
    indexer.reserve(21)

    s = str(indexer)
    assert "15 to 21" in s  # range end is exclusive


def test_str_formatting():
    idx = Indexer(start=1, idxs=[1, 2, range(5, 9), 12])
    assert str(idx) == "1,2,5 to 8,12"


def test_next_skips_reserved():
    idx = Indexer(start=1, idxs=[1, 2, range(5, 9), 12])
    assert idx.next == 3


def test_next_with_reserved_empty():
    idx = Indexer(start=1, idxs=[])
    assert idx.next == 1


def test_next_with_reserved_continuous():
    idx = Indexer(start=1, idxs=[1, 2, 3, 4])
    assert idx.next == 5


def test_reserve_does_not_mutate_input_range(indexer):
    r = range(7, 15)
    indexer.reserve(r)
    assert r.start == 7
    assert r.stop == 15
