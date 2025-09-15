import hashlib
import socket

from typing import Tuple, Final

KEY_SPACE: Final[int] = 16


def hash(key: str) -> int:
    return int(hashlib.sha1(key.encode()).hexdigest(), 16) % (2**KEY_SPACE)


def in_interval(key: int, start: int, end: int) -> bool:
    if start < end:
        return start <= key < end
    else:
        return key >= start or key < end


def ip() -> str:
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 1))
        ip_local = s.getsockname()[0]
    except Exception as e:
        print(f"Não foi possível obter o IP: {e}")
        ip_local = socket.gethostbyname(socket.gethostname())
    finally:
        if s:
            s.close()
    return ip_local


def addr_to_str(address: Tuple[str, int]) -> str:
    return f"{address[0]}:{address[1]}"
