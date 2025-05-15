import pytest

from makeproto.indexer import Indexer


@pytest.fixture
def indexer():
    return Indexer(start=10, idxs=[])


def test_reserve_int_greater_than_or_equal_to_start(indexer):
    indexer.reserve(10)
    indexer.reserve(11)
    assert 10 in indexer._flatten_reserveds()
    assert 11 in indexer._flatten_reserveds()


def test_reserve_int_less_than_start(indexer):
    indexer.reserve(9)
    assert 9 not in indexer._flatten_reserveds()


def test_reserve_range_fully_above_start(indexer):
    indexer.reserve(range(12, 14))  # deve incluir 12,13,14
    flat = indexer._flatten_reserveds()
    assert {12, 13, 14}.issubset(flat)


def test_reserve_range_partially_below_start(indexer):
    indexer.reserve(range(8, 14))  # inclusivo → 8..14, mas só reserva >= start (10)
    flat = indexer._flatten_reserveds()
    # Esperado: 10,11,12,13,14
    assert {10, 11, 12, 13, 14}.issubset(flat)


def test_reserve_range_fully_below_start(indexer):
    indexer.reserve(range(5, 9))  # inclusivo → 5..9
    flat = indexer._flatten_reserveds()
    assert not any(i >= 10 for i in flat)


def test_overlap_ranges_and_ints(indexer):
    indexer.reserve(range(15, 19))  # inclui 15..19
    indexer.reserve(range(18, 21))  # inclui 18..21
    indexer.reserve(19)
    indexer.reserve(21)
    s = str(indexer)
    assert "15 to 21" in s


def test_str_formatting():
    idx = Indexer(start=1, idxs=[1, 2, range(5, 8), 12])  # range(5,8) → 5..8
    assert str(idx) == "1,2,5 to 8,12"


def test_next_skips_reserved():
    idx = Indexer(start=1, idxs=[1, 2, range(5, 8), 12])  # reservas: 1,2,5,6,7,8,12
    assert idx.next == 3


def test_next_with_reserved_empty():
    idx = Indexer(start=1, idxs=[])
    assert idx.next == 1


def test_next_with_reserved_continuous():
    idx = Indexer(start=1, idxs=[1, 2, 3, 4])
    assert idx.next == 5


def test_reserve_does_not_mutate_input_range(indexer):
    r = range(7, 15)
    before = (r.start, r.stop)
    indexer.reserve(r)
    after = (r.start, r.stop)
    assert before == after
