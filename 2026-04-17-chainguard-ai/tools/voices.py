from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class VoiceSummaryTool:
    output_dir: Path

    def synthesize(self, text: str, language_label: str) -> str | None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = self.output_dir / f"summary-{language_label.lower().replace(' ', '-')}.wav"
        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.save_to_file(text, str(audio_path))
            engine.runAndWait()
            return str(audio_path)
        except Exception:
            return None
