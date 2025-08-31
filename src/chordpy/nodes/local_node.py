import json
import socket
import threading

from typing import Dict, List, Optional, Tuple
from utils import hash, in_interval
from chordpy.nodes.node import Node, KEY_SPACE
from chordpy.nodes.remote_node import RemoteNode


class LocalNode(Node):
    """
    Classe representando os nós do anel da DHT

    Cada nó possui conexão com seu sucessor imediato e com seu antecessor
    para facilitar as operações.

    Cada nó guarda a chave contida no intervalo [p, n),
    onde p é seu predecessor e n é o próprio nó.
    """

    def __init__(self, host: str = "localhost", port: int = 8080) -> None:
        self._address: Tuple[str, int] = (host, port)
        self._server_socket: Optional[socket.socket] = None
        self._running: bool = True

        self._id = hash(f"{self._address[0]}:{self._address[1]}")
        self._data: Dict[str, str] = {}
        self._prev: Node = self
        self._next: Node = self
        self._finger_table: Dict[int, Node] = {}
        self._update_finger_table(self)

    @property
    def next(self) -> Node:
        return self._finger_table[0]

    @next.setter
    def next(self, new_next: Tuple[str, int] | Node) -> None:
        if isinstance(new_next, Node):
            self._next = new_next
        else:
            self._next = RemoteNode(new_next)
        self._finger_table[0] = self._next

    @property
    def prev(self) -> Node:
        return self._prev

    @prev.setter
    def prev(self, new_prev: Tuple[str, int] | Node) -> None:
        if isinstance(new_prev, Node):
            self._prev = new_prev
        else:
            self._prev = RemoteNode(new_prev)

    @property
    def address(self) -> Tuple[str, int]:
        return self._address

    @property
    def id(self) -> int:
        return self._id

    @property
    def finger_table(self) -> Dict[int, Node]:
        return self._finger_table

    def _update_finger_table(self, existingNode=None) -> None:
        for i in range(KEY_SPACE):
            target = (self.id + 2**i) % (2**KEY_SPACE)

            if not existingNode:
                existingNode = self

            self.finger_table[i] = existingNode.find_successor(target)

    def find_successor(self, key: int) -> Node:
        if self.prev and in_interval(key, self.prev.id, self.id):
            return self

        if not self.prev:
            return self

        if self.next and in_interval(key, self.id, self.next.id):
            return self.next

        closest_preceding = self._closest_preceding_node(key)

        if closest_preceding == self:
            if self.next:
                return self.next.find_successor(key)
            return self

        return closest_preceding.find_successor(key)

    def _closest_preceding_node(self, key: int) -> Node:
        for i in range(KEY_SPACE - 1, -1, -1):
            finger_node = self.finger_table.get(i)

            if finger_node and finger_node != self:
                if in_interval(finger_node.id, self.id, key):
                    return finger_node

        return self

    def get(self, key: str) -> str:
        key_hash = hash(key)
        responsible_node = self.find_successor(key_hash)

        if responsible_node == self:
            return self.data.get(key, "Key not found")

        return responsible_node.get(key)

    def put(self, key: str, value: str) -> None:
        key_hash = hash(key)
        responsible_node = self.find_successor(key_hash)

        if responsible_node == self:
            self.data[key] = value
        else:
            responsible_node.put(key, value)

    def join(self, existing_node: RemoteNode) -> None:
        self.next = existing_node.find_successor(self.id)
        self.prev = self.next.prev
        self.data = self.next.pass_data(self)

        self._update_finger_table(existing_node)

        self.next.prev.next = self
        self.next.prev = self

    def pass_data(self, receiver: Node) -> Dict[str, str]:
        data_to_transfer: Dict[str, str] = {}
        keys_to_remove: List = []

        if self.prev != self:
            start: int = self.prev.id
        else:
            start: int = self.id

        for key, value in self.data.items():
            if in_interval(hash(key), start, receiver.id):
                data_to_transfer[key] = value
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.data[key]

        return data_to_transfer

    def _stabilize(self) -> None:
        if self.next != self and self.next.prev != self:
            x = self.next.prev

            if x and in_interval(x.id, self.id, self.next.id):
                self.next = x
                x.prev = self

        if self.next != self:
            self.next.notify(self)

        self._update_finger_table()

    def notify(self, potential_predecessor: Node) -> None:
        if not self.prev or in_interval(
            potential_predecessor.id, self.prev.id, self.id
        ):
            self.prev = potential_predecessor

    def server_start(self) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(self.address)
        self._server_socket.listen(5)

        self._running = True

        try:
            while self._running:
                client_socket, addr = self._server_socket.accept()

                client_thread = threading.Thread(
                    target=self._server_handle_client,
                    args=(client_socket, addr),
                )

                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            self.server_stop()

    def server_stop(self) -> None:
        self._running = False
        if self._server_socket:
            self._server_socket.close()

    def _server_handle_client(self, client_socket: socket.socket, addr: str) -> None:
        try:
            while True:
                data = client_socket.recv(1024).decode()

                if not data:
                    break

                response = self._process_request(json.loads(data))

                client_socket.send(response.encode())

        except Exception as e:
            print(f"Error handling client {addr}: {e}")

        finally:
            client_socket.close()
            print(f"Connection with {addr} closed")

    def _process_request(self, data: str) -> str:
        try:
            request: Dict = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON message: {e}")

        if request["type"] != "REQUEST":
            raise RuntimeError(f"Expected request but got '{request['type']}'")

        match request["header"]:
            case "GET_NEXT":
                response = {"next": self.next.address}
                return json.dumps(response)

            case "SET_NEXT":
                self.next = RemoteNode(request["parameters"]["new_next"])

            case "GET_PREV":
                response = {"prev": self.prev.address}
                return json.dumps(response)

            case "SET_PREV":
                self.prev = RemoteNode(request["parameters"]["new_prev"])

            case "LOOKUP":
                response = {"value": self.get(request["parameters"]["key"])}

            case "PUT":
                self.put(request["parameters"]["key"], request["parameters"]["value"])

            case "FIND_SUCCESSOR":
                response = {
                    "successor": self.find_successor(request["parameters"]["key"])
                }
                return json.dumps(response)

            case "NOTIFY":
                self.notify(request["parameters"]["potential_predecessor"])

            case "JOIN":
                self.join(request["parameters"]["potential_predecessor"])

            case "PASS_DATA":
                response = self.pass_data(request["parameters"]["receiver"])
                return json.dumps(response)

        return ""
