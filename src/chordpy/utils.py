import hashlib

from typing import Tuple, Final

KEY_SPACE: Final[int] = 16


def hash(key: str) -> int:
    return int(hashlib.sha1(key.encode()).hexdigest(), 16) % (2**KEY_SPACE)


def in_interval(key: int, start: int, end: int, include_start: bool = False, include_end: bool = True) -> bool:
    if start == end:
        return key == start if include_start or include_end else False
    
    if start < end:
        start_check = key >= start if include_start else key > start
        end_check = key <= end if include_end else key < end
        return start_check and end_check
    else:
        start_check = key >= start if include_start else key > start
        end_check = key <= end if include_end else key < end
        return start_check or end_check


def addr_to_str(address: Tuple[str, int]) -> str:
    return f"{address[0]}:{address[1]}"
