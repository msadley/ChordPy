import hashlib
from typing import Final, List, Dict

KEY_SPACE: Final[int] = 3  # Inicialmente pequeno para testes

def in_interval(key, start, end):
    # Evita problema no range com ciclo
    if start < end:
        return start < key <= end
    else:
        return key > start or key <= end

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
        print(self.id)

        # O "banco de dados" responsável por guardar os valores pelos quais o nó é responsável,
        # que são os valores de chaves entre o id de seu predecessor (inclusivo) e o seu próprio ID
        self.data: Dict[str, str] = {}

        # Ponteiro para o nó anterior
        self.prev: ChordNode

        # Ponteiro para o próximo nó
        self._next: ChordNode

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
        """Preenche/atualiza a finger table do nó"""

        for i in range(KEY_SPACE):
            # Retorna o valor int da posição que a seta aponta no círculo
            target = (self.id + 2**i) % (2**KEY_SPACE)

            if not existingNode:
                existingNode = self

            self.finger_table[i] = existingNode.find_successor(target)

    def find_successor(self, key: int) -> "ChordNode":
        # Se o intervalo entre o predecessor e ele (não-inclusivo) conter a chave, retornar ele mesmo.
        if in_interval(key, self.prev.id, self.id):
            return self
        
        # Se o intervalo entre ele e o sucessor (não-inclusivo) conter a chave, retornar o sucessor.
        if in_interval(key, self.id, self.next.id):
            return self.next

        """
        Aqui é onde a lógica de otimização para O(logn) entra:
        Caminhando ao contrário, o loop pula sempre metade do arco 
        até encontrar um nó que seja menor que a chave em questão,
        e então delega a busca recursivamente para este nó.
        """
        for i in range(KEY_SPACE - 1, -1, -1):
            preceding_node = self.finger_table[i]
            if preceding_node.id < key:
                break
        else:
            preceding_node = self

        return preceding_node.find_successor(key)

    def get(self, key: str) -> str:
        key_hash = self.hash(key)
        responsible_node = self.find_successor(key_hash)

        if responsible_node == self:
            return self.data[key]

        return responsible_node.get(key)

    def put(self, key: str, value: str) -> None:
        key_hash = self.hash(key)
        responsible_node = self.find_successor(key_hash)

        if responsible_node == self:
            self.data[key] = value
        responsible_node.put(key, value)

    def join(self, existingNode=None) -> None:
        if existingNode:
            self.successor = existingNode.find_successor(self.id)
            self.prev = self.successor.prev
            self.data = self.successor.pass_data(self.id)
            self.update_finger_table(existingNode)

            self.successor.prev.successor = self
            self.successor.prev = self

        else:
            self.prev = self
            self.next = self
            self.update_finger_table(self)

    def pass_data(self, stop: int) -> Dict[str, str]:
        data_given: Dict[str, str] = {}

        for key in self.data.keys():
            if self.prev.id <= self.hash(key) < stop:
                data_given[key] = self.data.pop(key)

        return data_given

    def stabilize(self) -> None:
        self.update_finger_table(self.find_successor(self.id))

    def print_data(self):
        print(self.data)

    def print_finger_table(self) -> None:
        print(self.finger_table)

    def __repr__(self) -> str:
        return f"Node {self.id}:\nData:{self.data}\nFinger table: {self.finger_table}"
