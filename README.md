# Drum-Practice-midi

Prototype application for practicing drums with MIDI feedback.

## Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

On Linux you may need ALSA libraries for MIDI support:

```bash
sudo apt-get install libasound2t64
```

## Running

Execute the GUI with:

```bash
python -m drum_practice.gui
```

Load a PDF containing simple drum notation keywords (kick, snare, hi-hat). If the PDF also contains a text like "120 BPM" the tempo spin box will be set automatically. Select a MIDI input device when starting playback. The application will show note accuracy after stopping.
