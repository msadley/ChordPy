import hashlib

from chordpy.nodes.node import KEY_SPACE


def hash(key: str) -> int:
    return int(hashlib.sha1(key.encode()).hexdigest(), 16) % (2**KEY_SPACE)


def in_interval(key, start, end) -> bool:
    if start < end:
        return start <= key < end
    else:
        return key >= start or key < end
