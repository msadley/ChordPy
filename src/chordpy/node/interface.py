from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Tuple

from address import Address


class Node(ABC):
    @property
    @abstractmethod
    def next(self) -> "Node":
        pass

    @next.setter
    @abstractmethod
    def next(self, new_next: "Node | Address") -> None:
        pass

    @property
    @abstractmethod
    def prev(self) -> "Node":
        pass

    @prev.setter
    @abstractmethod
    def prev(self, new_prev: "Node | Address") -> None:
        pass

    @property
    @abstractmethod
    def id(self) -> int:
        pass

    @property
    @abstractmethod
    def address(self) -> Address:
        pass

    @abstractmethod
    def find_successor(self, key: int, iterations: int) -> "Node":
        pass

    @abstractmethod
    def get(self, key: str, history: Optional[List[str]]) -> Tuple[str, Optional[Address], List[str]]:
        pass

    @abstractmethod
    def put(self, key: str, value: str) -> None:
        pass

    @abstractmethod
    def join(self, existing_node: "RemoteNode") -> None:  # type: ignore  # noqa: F821
        pass

    @abstractmethod
    def pass_data(self, receiver: "Node") -> None:
        pass

    @abstractmethod
    def update_data(self, new_data: Dict[str, str]) -> None:
        pass

    @abstractmethod
    def notify(self, potential_prev: "Node") -> None:
        pass
