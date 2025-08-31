import sys

from node.local import LocalNode
from node.remote import RemoteNode
from utils import addr_to_str, ip
from typing import Tuple


class Chord:
    def __init__(self) -> None:
        self._node = LocalNode()
        self._node.server_start()

    def get_ip(self) -> str:
        return ip()

    def join_network(self, node_address: Tuple[str, int]) -> None:
        try:
            self._node.join(RemoteNode(node_address))
        except Exception as e:
            raise RuntimeError(
                f"Error caught when joining {addr_to_str(node_address)}:\n{e}"
            )

    def put(self, key: str, value: str) -> None:
        try:
            self._node.put(key, value)
        except Exception as e:
            raise RuntimeError(f"Error caught when putting {key}:{value}\n{e}")

    def get(self, key: str) -> str:
        try:
            return self._node.get(key)
        except Exception as e:
            raise RuntimeError(f"Error caught when retrieving key '{key}':\n{e}")

    def stop(self) -> None:
        try:
            self._node.server_stop()
            sys.exit(0)
        except Exception as e:
            raise RuntimeError(f"Error caught when stopping program:\n{e}")
