import json
from pstats import SortKey
import socket
import threading
import hashlib
import time

from typing import Dict, List, Optional

KEY_SPACE: int = 16


def hash(key: str) -> int:
    return int(hashlib.sha1(key.encode()).hexdigest(), 16) % (2**KEY_SPACE)


def in_interval(key, start, end) -> bool:
    if start < end:
        return start <= key < end
    else:
        return key >= start or key < end


class ChordNode:
    """
    Classe representando os nós do anel da DHT

    Cada nó possui conexão com seu sucessor imediato e com seu antecessor
    para facilitar as operações.

    Cada nó guarda a chave contida no intervalo [p, n),
    onde p é seu predecessor e n é o próprio nó.
    """

    def __init__(self, host: str = "localhost", port: int = 8080) -> None:
        self.host: str = host
        self.port: int = port
        self.address: str = f"{host}:{port}"

        self.id = hash(self.address)

        self.server_socket = None
        self.running: bool = True

        self.data: Dict[str, str] = {}
        self.prev: Optional["ChordNode"] = None
        self._next: Optional["ChordNode"] = None
        self.finger_table: Dict[int, ChordNode] = {}

    @property
    def next(self) -> "ChordNode":
        return self.finger_table[0]

    @next.setter
    def next(self, new_next: "ChordNode") -> None:
        self._next = new_next
        self.finger_table[0] = new_next

    def update_finger_table(self, existingNode=None) -> None:
        for i in range(KEY_SPACE):
            target = (self.id + 2**i) % (2**KEY_SPACE)

            if not existingNode:
                existingNode = self

            self.finger_table[i] = existingNode.find_successor(target)

    def find_successor(self, key: int) -> "ChordNode":
        if self.prev and in_interval(key, self.prev.id, self.id):
            return self

        if not self.prev:
            return self

        if self.next and in_interval(key, self.id, self.next.id):
            return self.next

        closest_preceding = self.closest_preceding_node(key)

        if closest_preceding == self:
            if self.next:
                return self.next.find_successor(key)
            return self

        return closest_preceding.find_successor(key)

    def closest_preceding_node(self, key: int) -> "ChordNode":
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

    def join(self, existingNode=None) -> None:
        if existingNode:
            self.next = existingNode.find_successor(self.id)
            self.prev = self.next.prev
            self.data = self.next.pass_data(self.id)

            self.update_finger_table(existingNode)

            self.next.prev.next = self
            self.next.prev = self

        else:
            self.prev = self
            self.next = self
            self.update_finger_table(self)

    def pass_data(self, new_node_id: int) -> Dict[str, str]:
        data_to_transfer: Dict[str, str] = {}
        keys_to_remove: List = []

        if self.prev:
            start: int = self.prev.id
        else:
            start: int = self.id

        for key, value in self.data.items():
            if in_interval(hash(key), start, new_node_id):
                data_to_transfer[key] = value
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.data[key]

        return data_to_transfer

    def stabilize(self) -> None:
        if self.next and self.next.prev != self:
            x = self.next.prev

            if x and in_interval(x.id, self.id, self.next.id):
                self.next = x
                x.prev = self

        if self.next:
            self.next.notify(self)

        self.update_finger_table()

    def notify(self, potential_predecessor: "ChordNode") -> None:
        if not self.prev or in_interval(
            potential_predecessor.id, self.prev.id, self.id
        ):
            self.prev = potential_predecessor

    def create_request(self, type: str, header: str, id, **params) -> dict:
        return {
            "type": type,
            "header": header,
            "sender_id": id,
            "params": params,
            "timestamp": time.time(),
        }

    def request(self, target: socket._Address, request: dict) -> Dict | None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((target))

            json_data: str = json.dumps(request)

            client_socket.send(json_data.encode("utf-8"))

            response = client_socket.recv(1024).decode()

            client_socket.close()

            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON message: {e}")

        except Exception as e:
            print(f"Error when requesting {target}: {e}")

    def tostr(self) -> str:
        return f"Node <{self.id}> | Data <{self.data}> | Next: <{self.next.id}>"

    def server_start(self) -> None:
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        self.running = True

        try:
            while self.running:
                client_socket, addr = self.server_socket.accept()

                client_thread = threading.Thread(
                    target=self.server_handle_client,
                    args=(client_socket, addr),
                )

                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            self.server_stop()

    def server_stop(self) -> None:
        self.running = False
        if self.server_socket:
            self.server_socket.close()

    def server_handle_client(
        self, client_socket: socket.socket, addr: socket._RetAddress
    ) -> None:
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break

                # TODO Processar a requesição recebida aqui
                response = "Something here"
                client_socket.send(response.encode())

        except Exception as e:
            print(f"Error handling client {addr}: {e}")

        finally:
            client_socket.close()
            print(f"Connection with {addr} closed")

    def process_request(self, data: str):
        try:
            request: Dict = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON message: {e}")

        match request["type"]:
            case "FIND_SUCCESSOR":
                response = {"result": self.find_successor(request["parameters"]["key"])}
                json.dumps(response)
                ...
