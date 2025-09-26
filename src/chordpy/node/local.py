import json
import random
import socket
import threading

from typing import Dict, List, Optional, Final, Tuple
from address import Address
from utils import hash, in_interval
from node.interface import Node
from node.remote import RemoteNode
from logger import logger


KEY_SPACE: Final[int] = 16


class LocalNode(Node):
    def __init__(self, host: str = "0.0.0.0", port: int = 8008) -> None:
        self._address: Address = Address(self.get_ip(), port)
        self._host: Address = Address(host, port)
        self._server_socket: Optional[socket.socket] = None
        self._running: bool = True

        self._id: Final[int] = hash(str(self._address))
        self._data: Dict[str, str] = {}
        self._prev: Optional[Node] = None
        self._next: Optional[Node]

        self._finger_table: Dict[int, Node] = {}
        self._lock: threading.Lock = threading.Lock()

        logger.info(f"LocalNode initialized with ID: {self._id} at {self._address}")

    @property
    def next(self) -> Node:
        if self._next is None:
            raise ValueError("Next node is not set.")
        return self._next

    @next.setter
    def next(self, new_next: Address | Node) -> None:
        with self._lock:
            if isinstance(new_next, Node):
                if new_next == self:
                    self._next = self
                else:
                    self._next = new_next
            else:
                self._next = RemoteNode(new_next)
            self._finger_table[0] = self._next

    @property
    def prev(self) -> Node:
        if self._prev is None:
            raise ValueError("Previous node is not set.")
        return self._prev

    @prev.setter
    def prev(self, new_prev: Address | Node) -> None:
        with self._lock:
            if isinstance(new_prev, Node):
                if new_prev == self:
                    self._prev = self
                else:
                    self._prev = new_prev
            else:
                self._prev = RemoteNode(new_prev)

    @property
    def address(self) -> Address:
        return self._address

    @property
    def id(self) -> int:
        return self._id

    @property
    def finger_table(self) -> Dict[int, Node]:
        return self._finger_table

    @property
    def data(self) -> Dict[str, str]:
        return self._data

    @data.setter
    def data(self, new_data: Dict[str, str]) -> None:
        with self._lock:
            self._data.update(new_data)

    def get_ip(self) -> str:
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
            logger.warning(f"Failed to determine IP, using {ip}")
        finally:
            if s:
                s.close()
        return ip

    def _update_finger_table(self, existingNode=None) -> None:
        logger.info(f"Updating finger table for node {self.address}")
        for i in range(KEY_SPACE):
            target = (self.id + 2**i) % (2**KEY_SPACE)

            if not existingNode:
                existingNode = self

            with self._lock:
                self.finger_table[i] = existingNode.find_successor(target)

    def find_successor(self, key: int, iterations: int = 0) -> Node:
        logger.debug(f"Finding successor for key: {key}")

        if iterations > KEY_SPACE:
            logger.error(f"Recursion error: Successor not found for key {key}")
            raise RecursionError("Successor not found")

        if self.prev and in_interval(
            key, self.prev.id, self.id, include_start=False, include_end=True
        ):
            return self

        if self.next and in_interval(
            key, self.id, self.next.id, include_start=False, include_end=True
        ):
            return self.next

        closest_preceding = self._closest_preceding_node(key)

        if closest_preceding == self:
            return self

        return closest_preceding.find_successor(key, iterations + 1)

    def _closest_preceding_node(self, key: int) -> Node:
        for i in range(KEY_SPACE - 1, -1, -1):
            finger_node = self.finger_table.get(i)

            if finger_node and finger_node != self:
                if in_interval(
                    finger_node.id, self.id, key, include_start=False, include_end=False
                ):
                    return finger_node

        return self

    def get(
        self, key: str, history: Optional[List[str]] = None
    ) -> Tuple[str, Optional[Address], List[str]]:
        logger.info(f"GET request - Key: {key}")
        if history and str(self.address) in history:
            logger.warning(f"Circular lookup detected for key {key}")
            return ("Key not found", None, history)

        if history is None:
            history = []

        key_hash = hash(key)
        responsible_node = self.find_successor(key_hash)

        if responsible_node == self:
            value = self.data.get(key, "Key not found")
            if value == "Key not found":
                logger.info(f"Key '{key}' not found locally")
                history.append(f"Key not found locally at {self.address}")
                return (value, None, history)
            else:
                logger.info(f"Key '{key}' found locally with value '{value}'")
                history.append(f"Key found locally at {self.address}")
                return (value, self.address, history)

        logger.info(f"Forwarding GET request to {responsible_node.address}")
        return responsible_node.get(key, history)

    def put(self, key: str, value: str) -> None:
        key_hash: int = hash(key)
        logger.info(f"PUT request - Key: {key} | Hash: {key_hash}")
        responsible_node: Node = self.find_successor(key_hash)

        if responsible_node == self:
            logger.info(f"Storing key '{key}' locally at {self.address}")
            with self._lock:
                self.data[key] = value
        else:
            logger.info(f"Forwarding key '{key}' to node {responsible_node.address}")
            responsible_node.put(key, value)

    def join(self, existing_node: Optional[RemoteNode] = None) -> None:
        if existing_node is None:
            logger.info(f"Starting new Chord network with node {self.address}")
            self.prev = self
            self.next = self
            self._update_finger_table(self)
        else:
            logger.info(f"Joining network through {existing_node.address}")
            self.next = existing_node.find_successor(self.id)
            self.prev = self.next.prev
            self.next.pass_data(self)
            self._update_finger_table(existing_node)
            self.next.prev.next = self
            self.next.prev = self
            logger.info(f"Node {self.address} joined the network")

    def fix_fingers(self) -> None:
        i = random.randrange(KEY_SPACE)
        target = (self.id + 2**i) % (2**KEY_SPACE)
        self.finger_table[i] = self.find_successor(target)

    def pass_data(self, receiver: Node) -> None:
        if receiver == self or (self.prev == self and self.next == self):
            logger.info("Receiver is self, no data transfer needed")
            return

        logger.info(f"Transferring data to node {receiver.address}")
        data_to_transfer: Dict[str, str] = {}
        keys = list(self.data.keys())

        if self.next.id != receiver.id:
            responsible_node = self.find_successor(receiver.id)

            if responsible_node != self:
                logger.info(f"Forwarding data transfer to {responsible_node.address}")
                responsible_node.pass_data(receiver)
                return

        interval_end = receiver.id
        if self.prev == receiver:
            interval_end = self.id

        with self._lock:
            for key in keys:
                if in_interval(hash(key), self.prev.id, interval_end):
                    data_to_transfer[key] = self.data.pop(key)

        receiver.update_data(data_to_transfer)
        logger.info(f"Transferred {len(data_to_transfer)} keys to {receiver.address}")

    def update_data(self, new_data: Dict[str, str]) -> None:
        with self._lock:
            self.data.update(new_data)
        logger.info(f"Node {self.address} updated data with {len(new_data)} new keys")

    def exit_network(self) -> None:
        logger.info(f"Node {self.address} is exiting the network")
        if self.prev and self.next and self.prev != self and self.next != self:
            self.prev.next = self.next
            self.next.prev = self.prev
            self.pass_data(self.next)

        self._prev = None
        self._next = None
        self._finger_table.clear()
        self._data.clear()
        logger.info(f"Node {self.address} has exited the network")

    def _stabilize(self) -> None:
        with self._lock:
            if self.next is self:
                self._update_finger_table()
                return

            x = self.next.prev

            if x and in_interval(x.id, self.id, self.next.id):
                self.next = x

            self.next.notify(self)

        self.fix_fingers()

    def notify(self, potential_prev: Node) -> None:
        with self._lock:
            if not self.prev or in_interval(potential_prev.id, self.prev.id, self.id):
                self.prev = potential_prev

    def server_start(self) -> None:
        logger.info(f"Starting server at {self._host}")
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(self._host.as_tuple)
        self._server_socket.listen(5)

        self._running = True
        logger.info(f"Server listening at {self._host}")

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
            logger.info("Server shutting down due to keyboard interrupt")
        finally:
            self.server_stop()

    def server_stop(self) -> None:
        logger.info("Stopping server")
        self._running = False
        if self._server_socket:
            self._server_socket.close()

    def _server_handle_client(self, client_socket: socket.socket, addr: str) -> None:
        try:
            while self._running:
                data = client_socket.recv(1024).decode()

                if not data:
                    break

                logger.debug(f"Received data from {addr}: {data}")
                response = self._process_request(json.loads(data))
                logger.debug(f"Sending response to {addr}: {response}")

                client_socket.send(json.dumps(response).encode())

        except Exception as e:
            logger.error(f"Error handling client {addr}: {e}")

        finally:
            logger.debug(f"Closing client socket {addr}")
            client_socket.close()

    def _process_request(self, request: Dict) -> Dict:
        logger.info(f"Processing request: {request.get('type')}")

        match request["type"]:
            case "GET_NEXT":
                return {"next": self.next.address.as_tuple}

            case "SET_NEXT":
                new_next_addr = request["parameters"]["new_next"]
                self.next = Address(new_next_addr[0], new_next_addr[1])
                return {"status": "success"}

            case "GET_PREV":
                return {"prev": self.prev.address.as_tuple}

            case "SET_PREV":
                new_prev_addr = request["parameters"]["new_prev"]
                self.prev = Address(new_prev_addr[0], new_prev_addr[1])
                return {"status": "success"}

            case "LOOKUP":
                key = request["parameters"]["key"]
                history = request["parameters"].get("history", [])
                logger.info(f"LOOKUP request - Key: {key}")
                value, node_address, _ = self.get(key, history=history)
                return {
                    "value": value,
                    "node_address": node_address.as_tuple if node_address else None,
                }

            case "PUT":
                key = request["parameters"]["key"]
                value = request["parameters"]["value"]
                logger.info(f"PUT request - Key: {key}, Value: {value}")
                self.put(key, value)
                return {"status": "success"}

            case "FIND_SUCCESSOR":
                successor = self.find_successor(
                    request["parameters"]["key"],
                    request["parameters"].get("iterations", 0),
                )
                return {"successor": successor.address.as_tuple}

            case "NOTIFY":
                potential_prev_addr = request["parameters"]["potential_prev"]
                self.notify(
                    RemoteNode(Address(potential_prev_addr[0], potential_prev_addr[1]))
                )
                return {"status": "success"}

            case "JOIN":
                potential_prev_addr = request["parameters"]["potential_prev"]
                self.join(
                    RemoteNode(Address(potential_prev_addr[0], potential_prev_addr[1]))
                )
                return {"status": "success"}

            case "PASS_DATA":
                receiver_addr = request["parameters"]["receiver"]
                self.pass_data(RemoteNode(Address(receiver_addr[0], receiver_addr[1])))

            case "UPDATE_DATA":
                new_data = request["parameters"]["new_data"]
                self.update_data(new_data)
                return {"status": "success"}

            case "GET_ID":
                return {"id": self.id}

        return {"error": "Unknown request type"}

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Node):
            return False
        return self.address == value.address
