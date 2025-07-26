from dataclasses import dataclass
from typing import List, Tuple
import pdfplumber

@dataclass
class DrumNote:
    time: float  # in beats
    name: str


def parse_pdf(path: str) -> List[DrumNote]:
    """Parse a PDF file for simple drum notation keywords.

    This is a placeholder implementation that looks for text
    containing 'kick', 'snare', or 'hi-hat' and assigns each
    word to successive beats.
    """
    notes: List[DrumNote] = []
    try:
        with pdfplumber.open(path) as pdf:
            beat = 0
            for page in pdf.pages:
                text = page.extract_text() or ""
                for word in text.split():
                    lower = word.lower()
                    if lower in {"kick", "snare", "hi-hat", "hihat"}:
                        notes.append(DrumNote(time=beat, name=lower))
                        beat += 1
    except Exception as e:
        raise RuntimeError(f"Failed to parse PDF: {e}")
    return notes


def calculate_accuracy(expected: List[DrumNote], performed: List[Tuple[float, str]]) -> float:
    """Compare expected notes with performed notes.

    performed is a list of tuples (time_in_beats, name)
    Returns a hit accuracy percentage based on timing tolerance of 0.25 beat.
    """
    if not expected:
        return 0.0

    tolerance = 0.25
    hits = 0
    used = [False] * len(expected)
    for perf_time, perf_name in performed:
        for idx, note in enumerate(expected):
            if used[idx]:
                continue
            if note.name == perf_name and abs(note.time - perf_time) <= tolerance:
                hits += 1
                used[idx] = True
                break
    return 100.0 * hits / len(expected)
