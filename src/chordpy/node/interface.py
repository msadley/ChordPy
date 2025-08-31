from abc import ABC, abstractmethod
from typing import Dict, Tuple, Final
from node.remote import RemoteNode

KEY_SPACE: Final[int] = 16


class Node(ABC):
    @property
    @abstractmethod
    def next(self) -> "Node":
        pass

    @next.setter
    @abstractmethod
    def next(self, new_next: "Node | Tuple[str, int]") -> None:
        pass

    @property
    @abstractmethod
    def prev(self) -> "Node":
        pass

    @prev.setter
    @abstractmethod
    def prev(self, new_prev: "Node | Tuple[str, int]") -> None:
        pass

    @property
    @abstractmethod
    def id(self) -> int:
        pass

    @property
    @abstractmethod
    def address(self) -> Tuple[str, int]:
        pass

    @abstractmethod
    def find_successor(self, key: int) -> "Node":
        pass

    @abstractmethod
    def get(self, key: str) -> str:
        pass

    @abstractmethod
    def put(self, key: str, value: str) -> None:
        pass

    @abstractmethod
    def join(self, existing_node: RemoteNode) -> None:
        pass

    @abstractmethod
    def pass_data(self, receiver: "Node") -> Dict[str, str]:
        pass

    @abstractmethod
    def notify(self, potential_prev: "Node") -> None:
        pass
