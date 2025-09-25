import socket
import json

from typing import Dict, Any, Optional, Tuple

from address import Address
from message import message
from node.interface import List, Node
from logger import logger


class RemoteNode(Node):
    def __init__(self, address: Address) -> None:
        self._address: Address = address
        logger.info(f"RemoteNode initialized at {address}")

    @property
    def next(self) -> "RemoteNode":
        next_address_tuple: list = self._request("GET_NEXT", self.address)["next"]
        return RemoteNode(Address(next_address_tuple[0], next_address_tuple[1]))

    @next.setter
    def next(self, new_next: Node | Address) -> None:
        if isinstance(new_next, Node):
            address: Address = new_next.address
        else:
            address: Address = new_next

        self._request("SET_NEXT", self.address, new_next=address.as_tuple)

    @property
    def prev(self) -> "RemoteNode":
        prev_address_tuple: list = self._request("GET_PREV", self.address)["prev"]
        return RemoteNode(Address(prev_address_tuple[0], prev_address_tuple[1]))

    @prev.setter
    def prev(self, new_prev: Node | Address) -> None:
        if isinstance(new_prev, Node):
            address: Address = new_prev.address
        else:
            address: Address = new_prev

        self._request("SET_PREV", self.address, new_prev=address.as_tuple)

    @property
    def address(self) -> Address:
        return self._address

    @property
    def id(self) -> int:
        node_id = self._request("GET_ID", self.address)["id"]
        return node_id

    def _request(self, type: str, address: Address | list, **params) -> Dict[str, Any]:
        try:
            if isinstance(address, list):
                address = Address(address[0], address[1])

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(address.as_tuple)

            data: str = message(type, **params).to_json()
            logger.debug(f"Sending {type} request to {address}")

            client_socket.send(data.encode())

            response = client_socket.recv(1024).decode()

            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response: {e}")
                raise ValueError(f"Invalid JSON message: {e}")

        except ConnectionRefusedError:
            logger.error(f"Connection refused by {address}")
            raise RuntimeError(f"Node at {address} is not reachable")
        except socket.timeout:
            logger.error(f"Connection to {address} timed out")
            raise TimeoutError(f"Connection to {address} timed out")
        except Exception as e:
            logger.error(f"Error when requesting {type} from {address}: {e}")
            raise RuntimeError(f"Error when requesting {address}: {e}")

    def put(self, key: str, value: str) -> None:
        logger.info(f"Storing key '{key}' at remote node {self.address}")
        try:
            self._request("PUT", self.address, key=key, value=value)
        except Exception as e:
            logger.error(f"Failed to store key '{key}': {e}")
            raise

    def get(
        self, key: str, history: Optional[list]
    ) -> Tuple[str, Optional[Address], List[str]]:
        logger.info(f"Retrieving key '{key}' from remote node {self.address}")
        self_log: str = f"Get designado para {self.address}"
        if history is not None:
            history.append(self_log)
        else:
            history = [self_log]

        try:
            result = self._request("LOOKUP", self.address, key=key, history=history)
            value = result["value"]
            node_address_tuple = result.get("node_address")
            node_address = (
                Address(node_address_tuple[0], node_address_tuple[1])
                if node_address_tuple
                else None
            )
            return value, node_address, history

        except Exception as e:
            logger.error(f"Failed to retrieve key '{key}': {e}")
            raise

    def find_successor(self, key: int, iterations: int = 0) -> "RemoteNode":
        logger.info(f"Finding successor for key {key} at node {self.address}")
        try:
            successor_address_tuple: list = self._request(
                "FIND_SUCCESSOR", self.address, key=key, iterations=iterations
            )["successor"]
            return RemoteNode(
                Address(successor_address_tuple[0], successor_address_tuple[1])
            )
        except Exception as e:
            logger.error(f"Failed to find successor: {e}")
            raise

    def notify(self, potential_prev: Node) -> None:
        logger.info(f"Notifying node {self.address}")
        try:
            self._request(
                "NOTIFY", self.address, potential_prev=potential_prev.address.as_tuple
            )
        except Exception as e:
            logger.error(f"Failed to notify node: {e}")
            raise

    def join(self, existing_node: "RemoteNode") -> None:
        logger.info(f"Joining network through {existing_node.address}")
        try:
            self._request(
                "JOIN", self.address, existing_node=existing_node.address.as_tuple
            )
        except Exception as e:
            logger.error(f"Failed to join network: {e}")
            raise

    def pass_data(self, receiver: Node) -> Dict[str, str]:
        logger.info(f"Requesting data transfer to {receiver.address}")
        try:
            result = self._request(
                "PASS_DATA", self.address, receiver=receiver.address.as_tuple
            )
            return result
        except Exception as e:
            logger.error(f"Failed to transfer data: {e}")
            raise
