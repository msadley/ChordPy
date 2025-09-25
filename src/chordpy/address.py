from __future__ import annotations
from typing import Tuple

class Address:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    @property
    def as_tuple(self) -> Tuple[str, int]:
        return (self.ip, self.port)

    def __str__(self) -> str:
        return f"{self.ip}:{self.port}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Address):
            return NotImplemented
        return self.ip == other.ip and self.port == other.port

    def __hash__(self) -> int:
        return hash((self.ip, self.port))
