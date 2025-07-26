from dataclasses import dataclass
from typing import List, Tuple, Optional
import pdfplumber

@dataclass
class DrumNote:
    time: float  # in beats
    name: str


def parse_pdf(path: str) -> Tuple[List[DrumNote], Optional[int]]:
    """Parse a PDF file for simple drum notation keywords and BPM.

    This is a placeholder implementation that looks for text
    containing 'kick', 'snare', or 'hi-hat' and assigns each
    word to successive beats.
    """
    notes: List[DrumNote] = []
    bpm: Optional[int] = None
    try:
        with pdfplumber.open(path) as pdf:
            beat = 0
            for page in pdf.pages:
                text = page.extract_text() or ""
                if bpm is None:
                    import re
                    match = re.search(r"(\d+)\s*bpm", text, re.IGNORECASE)
                    if match:
                        bpm = int(match.group(1))

                # Normalize text for simple drum keyword search
                cleaned = (text.replace("hi hat", "hi-hat")
                               .replace("HI HAT", "hi-hat")
                               .replace("–", "-")
                               .replace("—", "-")
                               .replace("‑", "-"))
                import re
                for word in re.findall(r"\b[\w-]+\b", cleaned):
                    lower = word.lower().strip(".,;:!?")
                    if lower in {"hihat", "hi-hat"}:
                        lower = "hi-hat"
                    if lower in {"kick", "snare", "hi-hat"}:
                        notes.append(DrumNote(time=beat, name=lower))
                        beat += 1
    except Exception as e:
        raise RuntimeError(f"Failed to parse PDF: {e}")
    return notes, bpm


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
