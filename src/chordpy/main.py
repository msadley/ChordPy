from gui import ChordGUI
from chord import Chord
import threading
import sys


def main():
    chord = Chord(int(sys.argv[1]))
    gui = ChordGUI(chord)

    server_thread = threading.Thread(target=chord.start_server)
    server_thread.daemon = True
    server_thread.start()

    gui.start()


if __name__ == "__main__":
    main()
