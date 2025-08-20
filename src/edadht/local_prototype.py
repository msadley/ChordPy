import hashlib
from typing import Final, List, Dict

KEY_SPACE: Final[int] = 2


class ChordDHT:
    def __init__(self) -> None:
        pass


class ChordNode:
    def __init__(self, key) -> None:
        self.id = hash(key)
        self.peers: List[str]
        self.data: Dict[str, str]
        self.next: ChordNode
        self.finger_table: Dict[int, ChordNode]

    def hash(self, key: str) -> int:
        return int(hashlib  .sha1(key.encode()).hexdigest(), 16) % (2**KEY_SPACE)

    def generate_finger_table(self) -> None:
        for i in range(KEY_SPACE):
            target = (self.id + 2**i) % (2**KEY_SPACE)
            self.finger_table[i] = self.find_assigned_node(target)

    def find_assigned_node(self, key) -> "ChordNode":
        if self.hash(key) == self.id:
            return self

        if self.hash(key) in range(self.id, self.next.id):
            return self.next

        return self.finger_table[hash(key)]

    def get(self, key) -> str:
        responsible_node = self.find_assigned_node(key)
        if responsible_node == self:
            return self.data[key]

        return responsible_node.get(key)
