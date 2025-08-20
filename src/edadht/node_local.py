import hashlib
from typing import Final, List, Dict

KEY_SPACE: Final[int] = 160

class ChordNode:
    """
    Classe representando os nós do anel da DHT

    Cada nó possui conexão com seu sucessor imediato e com seu antecessor
    para facilitar as operações.

    Cada nó guarda a chave contida no intervalo [p, n),
    onde p é seu predecessor e n é o próprio nó.
    """

    def __init__(self, key) -> None:
        # Guarda o ID do nó no espaço de chaves da círculo
        self.id = hash(key)

        self.peers: List[str]  # ???

        # O "banco de dados" responsável por guardar os valores pelos quais o nó é responsável,
        # que são os valores de chaves entre o id de seu predecessor (inclusivo) e o seu próprio ID
        self.data: Dict[str, str]

        # Identificação do nó antecessor
        self.prev: ChordNode = self

        # Identificação do nó posterior
        self._next: ChordNode = self

        # Guarda as referências para os nós com pulos log(n)
        self.finger_table: List[ChordNode]

    @property
    def next(self) -> "ChordNode":
        return self.finger_table[0]

    @next.setter
    def successor(self, new_next) -> None:
        self.finger_table[0] = new_next

    def hash(self, key: str) -> int:
        return int(hashlib.sha1(key.encode()).hexdigest(), 16) % (2**KEY_SPACE)

    def generate_finger_table(self) -> None:
        """Preenche/atualiza a finger table do nó"""

        for i in range(KEY_SPACE):
            # Retorna o valor int da posição que a seta aponta no círculo
            target = (self.id + 2**i) % (2**KEY_SPACE)

            # Corrige a seta da finger table para um nó inicializado
            self.finger_table[i] = self.find_sucessor(target)

    def find_sucessor(self, key: str) -> "ChordNode":
        key_hash = self.hash(key)

        # Se o intervalo entre o predecessor e ele (não-inclusivo) conter a chave, retornar ele mesmo.
        if key_hash in range(self.prev.id, self.id):
            return self

        # Se o intervalo entre ele e o sucessor (não-inclusivo) conter a chave, retornar o sucessor.
        if key_hash in range(self.id, self.next.id):
            return self.next

        """
        Aqui é onde a lógica de otimização para O(logn) entra:
        Caminhando ao contrário, o loop pula sempre metade do arco 
        até encontrar um nó que seja menor que a chave em questão,
        e então delega a busca recursivamente para este nó.
        """
        for i in range(KEY_SPACE-1, -1, -1):
            preceding_node = self.finger_table[i]
            if preceding_node.id < key_hash:
                break
        else:
            preceding_node = self
            
        return preceding_node.find_sucessor(key)

    def get(self, key: str) -> str:
        responsible_node = self.find_sucessor(key)
        
        if responsible_node == self:
            return self.data[key]

        return responsible_node.get(key)

    def put(self, key: str, value: str) -> None:
        responsible_node = self.find_sucessor(key)
        
        if responsible_node == self:
            self.data[key] = value

        responsible_node.put(key, value)