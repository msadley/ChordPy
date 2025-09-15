import socket
import json

from typing import Tuple, Dict, Any
from message import message
from node.interface import Node


class RemoteNode(Node):
    def __init__(self, address: Tuple[str, int]) -> None:
        self._id: int = hash(f"{address[0]}:{address[1]}")
        self._address: Tuple[str, int] = address

    @property
    def next(self) -> "RemoteNode":
        next_address: Tuple[str, int] = self._request("GET_NEXT", self.address)["next"]
        return RemoteNode(next_address)

    @next.setter
    def next(self, new_next: Node | Tuple[str, int]) -> None:
        if isinstance(new_next, Node):
            address: Tuple[str, int] = new_next.address
        else:
            address: Tuple[str, int] = new_next

        self._request("SET_NEXT", self.address, new_next=address)

    @property
    def prev(self) -> "RemoteNode":
        prev_address: Tuple[str, int] = self._request("GET_PREV", self.address)["prev"]
        return RemoteNode(prev_address)

    @prev.setter
    def prev(self, new_prev: Node | Tuple[str, int]) -> None:
        if isinstance(new_prev, Node):
            address: Tuple[str, int] = new_prev.address
        else:
            address: Tuple[str, int] = new_prev

        self._request("SET_PREV", self.address, new_prev=address)

    @property
    def address(self) -> Tuple[str, int]:
        return self._address

    @property
    def id(self) -> int:
        return self._id

    def _request(self, type: str, address: Tuple[str, int], **params) -> Dict[str, Any]:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((address))

            data: str = message(type, **params).to_json()

            client_socket.send(data.encode())

            response = client_socket.recv(1024).decode()

            client_socket.close()

            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON message: {e}")

        except Exception as e:
            raise RuntimeError(f"Error when requesting {address}: {e}")

    def get(self, key: str) -> str:
        return self._request("LOOKUP", self.address, key=key)["result"]

    def put(self, key: str, value: str) -> None:
        self._request("PUT", self.address, key=key, value=value)

    def find_successor(self, key: int) -> "RemoteNode":
        successor_address: Tuple[str, int] = self._request(
            "FIND_SUCCESSOR", self.address, key=key
        )["result"]
        return RemoteNode(successor_address)

    def notify(self, potential_prev: Node) -> None:
        self._request("NOTIFY", self.address, notifier=potential_prev.address)

    def join(self, existing_node: "RemoteNode") -> None:
        self._request("JOIN", self.address, potential_prev=existing_node.address)

    def pass_data(self, receiver: Node) -> Dict[str, str]:
        return self._request("PASS_DATA", self.address, receiver=receiver.address)
