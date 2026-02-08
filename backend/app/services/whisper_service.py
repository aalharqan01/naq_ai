"""Audio transcription service using faster-whisper."""

import json
import logging
from pathlib import Path

from app.config import settings

logger = logging.getLogger("dhakira.whisper")

# Lazy-loaded model
_model = None


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        logger.info(f"Loading Whisper model: {settings.whisper_model}")
        _model = WhisperModel(
            settings.whisper_model,
            device="cpu",
            compute_type="int8",
        )
        logger.info("Whisper model loaded")
    return _model


def transcribe_audio(audio_path: str, language: str | None = None) -> dict:
    """
    Transcribe an audio file to text with timestamps.

    Returns:
        {
            "text": "full transcript",
            "segments": [{"start": 0.0, "end": 5.2, "text": "..."}],
            "language": "ar",
            "duration": 120.5
        }
    """
    model = _get_model()
    path = Path(audio_path)

    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    logger.info(f"Transcribing: {path.name}")

    options = {}
    if language:
        options["language"] = language

    raw_segments, info = model.transcribe(str(path), **options)

    segments = []
    full_text_parts = []

    for seg in raw_segments:
        text = seg.text.strip()
        if text:
            segments.append({
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": text,
            })
            full_text_parts.append(text)

    duration = segments[-1]["end"] if segments else 0.0

    transcript = {
        "text": " ".join(full_text_parts),
        "segments": segments,
        "language": info.language if info else (language or "unknown"),
        "duration": duration,
    }

    # Save processed transcript
    out_path = Path(settings.processed_dir) / f"{path.stem}_transcript.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)

    logger.info(
        f"Transcription complete: {len(segments)} segments, "
        f"{duration:.1f}s, language={transcript['language']}"
    )

    return transcript
