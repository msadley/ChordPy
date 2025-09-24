import hashlib
import socket

from typing import Tuple, Final

KEY_SPACE: Final[int] = 16


def hash(key: str) -> int:
    return int(hashlib.sha1(key.encode()).hexdigest(), 16) % (2**KEY_SPACE)


def in_interval(key: int, start: int, end: int) -> bool:
    if start == end:
        return key != start
    if start < end:
        return start < key <= end
    else:
        return key > start or key <= end


def addr_to_str(address: Tuple[str, int]) -> str:
    return f"{address[0]}:{address[1]}"
