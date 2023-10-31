from itertools import islice
from typing import Iterable, Iterator, TypeVar

T = TypeVar('T')


def batched(iterable: Iterable[T], n: int) -> Iterator[tuple[T, ...]]:
    """
    >>> batched([1, 2, 3, 4, 5], 2)
    [1, 2] [3, 4] [5]
    """
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch
