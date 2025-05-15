from functools import singledispatchmethod
from typing import List, NoReturn, Set, Union


class Indexer:
    def __init__(self, start: int = 1, idxs: List[Union[int, range]] = []) -> None:
        self._start = start
        self._counter = start
        self._reserveds = list(idxs)

    @singledispatchmethod
    def reserve(self, idx: Union[int, range]) -> NoReturn:
        raise TypeError(f"Unsupported type for reserve: {type(idx)}")

    @reserve.register
    def _(self, idx: int) -> None:
        if idx > self._start:
            self._reserveds.append(idx)

    @reserve.register
    def _(self, idx: range) -> None:
        if idx.stop > self._start:
            filtered = range(max(self._start + 1, idx.start), idx.stop)
            if filtered:
                self._reserveds.append(filtered)

    @property
    def next(self) -> int:
        flat = self._flatten_reserveds()
        i = self._counter
        while i in flat:
            i += 1
        self._counter = i + 1
        return i

    def _flatten_reserveds(self) -> Set[int]:
        return {
            i
            for x in self._reserveds
            for i in (x if isinstance(x, range) else [x])
            if i >= self._start
        }

    def _merge_ranges(self, items: List[Union[int, range]]) -> List[Union[int, range]]:
        # Flatten into ints
        ints = sorted(
            {
                i
                for x in items
                for i in (x if isinstance(x, range) else [x])
                if i >= self._start
            }
        )
        if not ints:
            return []

        # Merge into ranges
        result: List[Union[int, range]] = []
        start = prev = ints[0]
        for i in ints[1:]:
            if i == prev + 1:
                prev = i
            else:
                if start == prev:
                    result.append(start)
                else:
                    result.append(range(start, prev + 1))
                start = prev = i
        # Add last
        if start == prev:
            result.append(start)
        else:
            result.append(range(start, prev + 1))
        return result

    def _overlaps(self, a: Union[int, range], b: Union[int, range]) -> bool:
        a_range = range(a, a + 1) if isinstance(a, int) else a
        b_range = range(b, b + 1) if isinstance(b, int) else b
        return a_range.stop > b_range.start and b_range.stop > a_range.start

    def __str__(self) -> str:
        merged = self._merge_ranges(self._reserveds)
        parts: List[str] = []
        for item in merged:
            if isinstance(item, int):
                parts.append(str(item))
            elif item.stop - item.start == 2:
                # small range of 2 values, e.g., range(1, 3) => 1,2
                parts.append(f"{item.start}")
                parts.append(f"{item.start + 1}")
            else:
                parts.append(f"{item.start} to {item.stop - 1}")
        return ",".join(parts)
