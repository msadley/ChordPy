from .controller import ChordController
from cli import menu


def main() -> None:
    chordpy = Chord()
    menu(chordpy)


if __name__ == "__main__":
    main()