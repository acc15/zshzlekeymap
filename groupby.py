
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")
K = TypeVar("K")

def groupby(values: Iterable[T], key: Callable[[T], K]):
    return grouptodict(values, key).items()

def grouptodict(values: Iterable[T], key: Callable[[T], K]) -> dict[K, list[T]]:
    r: dict[K, list[T]] = {}
    for v in values:
        k: K = key(v)
        l = r.get(k, None)
        if l:
            l.append(v)
        else:
            r[k] = [v]
    return r
