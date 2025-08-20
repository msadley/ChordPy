# ChordPy

> Um sistema de armazenamento chave-valor distribuído baseado no protocolo Chord, implementado em Python para fins acadêmicos.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow.svg?style=for-the-badge)

---

## Sobre o Projeto

**ChordPy** é uma implementação simplificada de uma Tabela de Hash Distribuída (DHT) baseada no protocolo Chord. Este projeto foi desenvolvido como parte da disciplina de **Estruturas de Dados e Algoritmos**, com o principal objetivo de explorar e entender na prática os conceitos de sistemas distribuídos, redes P2P e algoritmos de roteamento descentralizado.

O sistema cria um anel de nós em uma rede local, onde cada nó é responsável por um segmento do espaço de chaves, permitindo o armazenamento e a recuperação de dados de forma eficiente e descentralizada.

## Funcionalidades Implementadas

- **Join:** Permite que um novo nó se junte ao anel Chord, recebendo as informações necessárias de um nó já existente.
- **Leave:** Permite que um nó saia do anel de forma planejada, transferindo suas chaves e responsabilidades.
- **Lookup (find_successor):** Algoritmo principal para encontrar o nó sucessor responsável por uma determinada chave no anel.
- **Estabilização:** Processo periódico executado pelos nós para garantir que os ponteiros de sucessor e predecessor estejam corretos, mantendo a consistência do anel mesmo com a entrada e saída de nós.

## Detalhes Técnicos

- **Linguagem:** Python
- **Comunicação em Rede:** A comunicação entre os nós da rede é implementada utilizando **sockets puros**.
- **Algoritmo de Hash:** Utilizamos a biblioteca `hashlib` com o algoritmo **SHA-1** para gerar os identificadores tanto dos nós quanto das chaves.
- **Espaço de Identificadores:** O anel Chord opera com um espaço de chaves de $10$ bits, o que significa que os identificadores variam de $0$ a $2^{10}-1$ (ou seja, de 0 a 1023).

## Como Usar (Em Breve)

_Esta seção será detalhada assim que a implementação da interface de usuário e dos scripts de inicialização estiver concluída._

### Pré-requisitos

- Python 3.x

### Instalação e Execução

1. **Clone o repositório:**

    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    ```

2. **Navegue até o diretório do projeto:**

    ```bash
    cd ChordPy
    ```

3. **Para iniciar o anel (primeiro nó):**

    ```bash
    # Exemplo de comando a ser definido
    python node.py --port 8000
    ```

4. **Para adicionar um novo nó ao anel:**

    ```bash
    # Exemplo de comando a ser definido
    python node.py --port 8001 --join 127.0.0.1:8000
    ```

## Estrutura do Projeto (Em Breve)

_A descrição da estrutura de arquivos e seus respectivos papéis será adicionada aqui futuramente._

## Autores

Este projeto foi desenvolvido pela seguinte equipe:

- Adley Silva Mendes
- Iury Ruan do Nascimento Santos
- João Pedro Araújo de Medeiros
- José Paulo Freitas da Silva Farias

## Contexto Acadêmico

Este projeto foi desenvolvido como requisito para a disciplina de Estruturas de Dados e Algoritmos, ministrada pelo professor **João Arthur Brunet Monteiro**.
