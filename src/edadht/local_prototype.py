from node_local import ChordNode


def main() -> None:
    node0 = ChordNode("0")  # 4
    node1 = ChordNode("1")  # 3
    node2 = ChordNode("2")  # 0
    node3 = ChordNode("4")  # 2

    node0.join()
    node0.put("2", "oioi")
    node0.put("1", "adley")
    node2.join(node0)
    node1.join(node0)

    node3.join(node1)

    print(node0)
    print("seu proximo: ", node0.getNext())
    print()
    print(node1)
    print("seu proximo: ", node1.getNext())
    print()
    print(node2)
    print("seu proximo: ", node2.getNext())
    print()
    print(node3)
    print("seu proximo: ", node3.getNext())
    print()


if __name__ == "__main__":
    main()
    print("done")
