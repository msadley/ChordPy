import sys
import re
from typing import Tuple, Dict, Any, Optional

from node.local import LocalNode
from node.remote import RemoteNode


class ChordController:
    def __init__(self, port: Optional[int] = 8008) -> None:
        if port is not None:
            self._node = LocalNode(port=port)
        else:
            self._node = LocalNode()

    def start_server(self) -> None:
        self._node.server_start()

    def get_address(self) -> str:
        return self._node.get_address()

    def stop(self) -> None:
        try:
            self._node.server_stop()
            sys.exit(0)
        except Exception as e:
            raise RuntimeError(f"Error caught when stopping program:\n{e}")

    def validate_address(self, address: str) -> Tuple[str, int]:
        pattern = r"^(\d{1,3}(\.\d{1,3}){3}):(\d{1,5})$"
        if not re.match(pattern, address):
            raise ValueError("Endereço inválido. Use o formato IP:PORTA")

        ip, port_str = address.split(":")
        port = int(port_str)

        return ip, port

    def join_network(self, address: str) -> Dict[str, Any]:
        try:
            ip, port = self.validate_address(address)
            self._node.join(RemoteNode((ip, port)))
            return {"success": True, "message": f"Conectado à rede {ip}:{port}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def put(self, key: str, value: str) -> Dict[str, Any]:
        if not key or not value:
            return {"success": False, "message": "Chave e valor não podem ser vazios"}

        try:
            self._node.put(key, value)
            return {"success": True, "message": f"Chave '{key}' armazenada com sucesso"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get(self, key: str) -> Dict[str, Any]:
        if not key:
            return {"success": False, "message": "A chave não pode ser vazia"}

        try:
            value = self._node.get(key)
            if value and value != "Key not found":
                return {"success": True, "key": key, "value": value}
            else:
                return {"success": False, "message": f"Chave '{key}' não encontrada"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_node_inf(self) -> Dict[str, Any]:
        try:
            node = self._node
            info = {
                "id": node.id,
                "ip": node.address[0],
                "port": node.address[1],
                "address": f"{node.address[0]}:{node.address[1]}",
                "prev": f"{node.prev.address[0]}:{node.prev.address[1]}"
                if node.prev
                else None,
                "next": f"{node.next.address[0]}:{node.next.address[1]}"
                if node.next
                else None,
                "finger_table": {
                    i: f"{n.address[0]}:{n.address[1]}"
                    for i, n in node.finger_table.items()
                },
                "data": node._data.copy(),
            }
            return {"success": True, "node_info": info}
        except Exception as e:
            return {"success": False, "message": str(e)}
