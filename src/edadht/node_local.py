import hashlib
from typing import Final, Dict, List

KEY_SPACE: Final[int] = 3  # Inicialmente pequeno para testes


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

    def __init__(self, key: str) -> None:
        # Guarda o ID do nó no espaço de chaves da círculo
        self.id: int = self.hash(key)

        # O "banco de dados" responsável por guardar os valores pelos quais o nó é responsável,
        # que são os valores de chaves entre o id de seu predecessor (inclusivo) e o seu próprio ID
        self.data: Dict[str, str] = {}

        # Ponteiro para o nó anterior
        self.prev: ChordNode | None = None

        # Ponteiro para o próximo nó
        self._next: ChordNode | None = None

        # Guarda as referências para os nós com pulos log(n)
        self.finger_table: Dict[int, ChordNode] = {}

    @property
    def next(self):
        return self.finger_table[0]

    @next.setter
    def next(self, new_next: "ChordNode") -> None:
        self._next = new_next
        self.finger_table[0] = new_next

    def hash(self, key: str) -> int:
        return int(hashlib.sha1(key.encode()).hexdigest(), 16) % (2**KEY_SPACE)

    def update_finger_table(self, existingNode=None) -> None:
        for i in range(KEY_SPACE):
            # Retorna o valor int da posição que a seta aponta no círculo
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
        key_hash = self.hash(key)
        responsible_node = self.find_successor(key_hash)

        if responsible_node == self:
            return self.data.get(key, "Key not found")

        return responsible_node.get(key)

    def put(self, key: str, value: str) -> None:
        key_hash = self.hash(key)
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
            if in_interval(self.hash(key), start, new_node_id):
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

        if self.next:
            self.next.notify(self)

        self.update_finger_table()

    def notify(self, potential_predecessor: "ChordNode") -> None:
        if not self.prev or in_interval(
            potential_predecessor.id, self.prev.id, self.id
        ):
            self.prev = potential_predecessor

    def print_data(self) -> None:
        print(self.data)

    def print_finger_table(self) -> None:
        print(self.finger_table)

    def getId(self) -> int:
        return self.id

    def getNext(self) -> "ChordNode":
        return self.next

    def __repr__(self) -> str:
        return f"Node <{self.id}> | Data <{self.data}> | Next: <{self.next.id}>"
