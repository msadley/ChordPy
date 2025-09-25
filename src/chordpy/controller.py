import sys
import re
from typing import Dict, Any, Optional

from address import Address
from node.local import LocalNode
from node.remote import RemoteNode
from logger import logger


class ChordController:
    def __init__(self, port: Optional[int] = 8008) -> None:
        if port is not None:
            self._node = LocalNode(port=port)
        else:
            self._node = LocalNode()
        logger.info(
            f"Controller initialized with node ID: {self._node.id} at {self._node.address}"
        )

    def getNeighbors(self) -> Dict[str, Any]:
        try:
            prev = str(self._node.prev.address) if self._node.prev else None
            next = str(self._node.next.address) if self._node.next else None
            logger.info(f"Retrieved neighbors: prev={prev}, next={next}")
            return {"success": True, "prev": prev, "next": next}
        except Exception as e:
            logger.error(f"Failed to get neighbors: {e}")
            return {"success": False, "message": str(e)}

    def getLocalDict(self) -> Dict[str, Any]:
        try:
            data = self._node._data.copy()
            logger.info(f"Retrieved local dictionary with {len(data)} entries")
            return {"success": True, "data": data}
        except Exception as e:
            logger.error(f"Failed to get local dictionary: {e}")
            return {"success": False, "message": str(e)}

    def getFingerTable(self) -> dict[str, Any]:
        try:
            finger_table = {
                i: str(n.address) for i, n in self._node.finger_table.items()
            }
            logger.info(f"Retrieved finger table with {len(finger_table)} entries")
            return {"success": True, "finger_table": finger_table}
        except Exception as e:
            logger.error(f"Failed to get finger table: {e}")
            return {"success": False, "message": str(e)}

    def getId(self) -> int:
        logger.info(f"Retrieved node ID: {self._node.id}")
        return self._node.id

    def start_server(self) -> None:
        logger.info("Starting server...")
        self._node.server_start()
        logger.info(f"Server started at {self._node.address}")

    def get_address(self) -> str:
        address = str(self._node.address)
        logger.info(f"Retrieved node address: {address}")
        return address

    def stop(self) -> None:
        try:
            logger.info("Exiting network...")
            self._node.exit_network()
            logger.info("Stopping server...")
            self._node.server_stop()
            logger.info("Server stopped successfully")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error when stopping server: {e}")
            raise RuntimeError(f"Error caught when stopping program:\n{e}")

    def validate_address(self, address: str) -> Address:
        pattern = r"^(\d{1,3}(\.\d{1,3}){3}):(\d{1,5})$"
        if not re.match(pattern, address):
            logger.error(f"Invalid address format: {address}")
            raise ValueError("Endereço inválido. Use o formato IP:PORTA")

        ip, port_str = address.split(":")
        port = int(port_str)
        logger.info(f"Address validated: {ip}:{port}")
        return Address(ip, port)

    def start_network(self) -> None:
        logger.info("Starting new Chord network...")
        self._node.join()
        logger.info("New network started successfully")

    def join_network(self, address: str) -> Dict[str, Any]:
        try:
            logger.info(f"Attempting to join network at {address}")
            validated_address = self.validate_address(address)
            self._node.join(RemoteNode(validated_address))
            logger.info(f"Successfully joined network at {validated_address}")
            return {"success": True, "message": f"Conectado à rede {validated_address}"}
        except Exception as e:
            logger.error(f"Failed to join network at {address}: {e}")
            return {"success": False, "message": str(e)}

    def put(self, key: str, value: str) -> Dict[str, Any]:
        if not key or not value:
            logger.warning("Attempted to put with empty key or value")
            return {"success": False, "message": "Chave e valor não podem ser vazios"}

        try:
            logger.info(f"Putting key-value pair: '{key}' = '{value}'")
            self._node.put(key, value)
            logger.info(f"Successfully stored key '{key}'")
            return {"success": True, "message": f"Chave '{key}' armazenada com sucesso"}
        except TimeoutError as e:
            logger.error(f"Timeout error: {e}")
            return {"success": False, "message": str(e), "error_type": "timeout"}
        except Exception as e:
            logger.error(f"Failed to put key '{key}': {e}")
            return {"success": False, "message": str(e)}

    def get(self, key: str) -> Dict[str, Any]:
        if not key:
            logger.warning("Attempted to get with empty key")
            return {"success": False, "message": "A chave não pode ser vazia"}

        try:
            logger.info(f"Getting value for key: '{key}'")
            value, node_address, history = self._node.get(key)
            if value and value != "Key not found":
                logger.info(f"Key '{key}' found with value '{value}' at {node_address}")
                node_str = str(node_address) if node_address else "Unknown"
                return {"success": True, "key": key, "value": value, "node": node_str, "history": history}
            else:
                logger.warning(f"Key '{key}' not found")
                return {"success": False, "message": f"Chave '{key}' não encontrada", "history": history}
        except Exception as e:
            logger.error(f"Error retrieving key '{key}': {e}")
            return {"success": False, "message": str(e)}

    def get_node_inf(self) -> Dict[str, Any]:
        try:
            logger.info("Retrieving complete node information")
            node = self._node
            info = {
                "id": node.id,
                "ip": node.address.ip,
                "port": node.address.port,
                "address": str(node.address),
                "prev": str(node.prev.address) if node.prev else None,
                "next": str(node.next.address) if node.next else None,
                "finger_table": {
                    i: str(n.address) for i, n in node.finger_table.items()
                },
                "data": node._data.copy(),
            }
            logger.info("Node information retrieved successfully")
            return {"success": True, "node_info": info}
        except Exception as e:
            logger.error(f"Failed to retrieve node information: {e}")
            return {"success": False, "message": str(e)}
