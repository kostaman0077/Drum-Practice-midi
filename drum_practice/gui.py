import sys
from typing import List, Tuple

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from .core import DrumNote, parse_pdf, calculate_accuracy
from .midi_input import MidiListener

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drum Practice")
        self.resize(800, 600)
        self.notes: List[DrumNote] = []
        self.performed: List[Tuple[float, str]] = []
        self.midi_listener: MidiListener | None = None

        # Widgets
        self.load_button = QtWidgets.QPushButton("Load PDF")
        self.bpm_spin = QtWidgets.QSpinBox()
        self.bpm_spin.setRange(40, 300)
        self.bpm_spin.setValue(120)
        self.start_button = QtWidgets.QPushButton("Start")
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.sheet = QtWidgets.QTextEdit()
        self.sheet.setReadOnly(True)
        self.stats_label = QtWidgets.QLabel("Accuracy: n/a")
        self.progress = QtWidgets.QProgressBar()

        # Layout
        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(self.load_button)
        controls.addWidget(QtWidgets.QLabel("BPM:"))
        controls.addWidget(self.bpm_spin)
        controls.addWidget(self.start_button)
        controls.addWidget(self.stop_button)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(self.sheet)
        layout.addWidget(self.progress)
        layout.addWidget(self.stats_label)

        # Signals
        self.load_button.clicked.connect(self.load_pdf)
        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.stop)

        # Timer for playback
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.current_index = 0

    def closeEvent(self, event):
        self.stop()
        super().closeEvent(event)

    def load_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", filter="PDF Files (*.pdf)")
        if not path:
            return
        try:
            self.notes, bpm = parse_pdf(path)
            if not self.notes:
                raise RuntimeError("No drum notes found in PDF")
            if bpm:
                self.bpm_spin.setValue(bpm)
            self.sheet.setPlainText("\n".join(f"{n.time}: {n.name}" for n in self.notes))
            self.progress.setMaximum(len(self.notes))
            self.current_index = 0
            self.performed.clear()
            self.stats_label.setText("Accuracy: n/a")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def start(self):
        if not self.notes:
            QMessageBox.warning(self, "No notes", "Load a PDF first")
            return
        self.timer.start(int(60000 / self.bpm_spin.value()))
        self.open_midi()

    def stop(self):
        self.timer.stop()
        if self.midi_listener:
            self.midi_listener.stop()
            self.midi_listener = None
        acc = calculate_accuracy(self.notes, self.performed)
        self.stats_label.setText(f"Accuracy: {acc:.1f}%")

    def open_midi(self):
        import mido
        ports = mido.get_input_names()
        if not ports:
            QMessageBox.warning(self, "MIDI", "No MIDI input devices found")
            return
        port, ok = QtWidgets.QInputDialog.getItem(self, "MIDI Input", "Select device:", ports, 0, False)
        if ok and port:
            self.performed.clear()
            self.midi_listener = MidiListener(port_name=port, callback=self.record_hit)
            try:
                self.midi_listener.start()
            except Exception as e:
                QMessageBox.critical(self, "MIDI", f"Failed to open MIDI device: {e}")
                self.midi_listener = None

    def record_hit(self, note: Tuple[float, str]):
        # record the hit using the current playback index as time reference
        _time, name = note
        self.performed.append((float(self.current_index), name))

    def tick(self):
        if self.current_index >= len(self.notes):
            self.stop()
            return
        self.progress.setValue(self.current_index + 1)
        self.current_index += 1
        try:
            import winsound
            winsound.Beep(1000, 50)
        except Exception:
            pass


def run():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()
