import mido
from typing import Callable, Tuple

class MidiListener:
    """Listen to a MIDI input port and dispatch note_on events."""
    def __init__(self, port_name: str, callback: Callable[[Tuple[float, str]], None]):
        self.port_name = port_name
        self.callback = callback
        self.port = None

    def start(self):
        self.port = mido.open_input(self.port_name, callback=self._handle)

    def stop(self):
        if self.port:
            self.port.close()
            self.port = None

    def _handle(self, msg):
        if msg.type == 'note_on' and msg.velocity > 0:
            # map midi note numbers to simple names
            name = str(msg.note)
            time = mido.tick2second(msg.time, 480, 500000)  # simple convert
            self.callback((time, name))
