from typing import Final, List, Dict

from node_local import ChordNode


def main() -> None:
    node0 = ChordNode("0")  # 4
    node1 = ChordNode("1")  # 3
    node2 = ChordNode("2")  # 0

    node0.join()


if __name__ == "__main__":
    main()
