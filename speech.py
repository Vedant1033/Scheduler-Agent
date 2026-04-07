"""Speech utilities: STT (faster-whisper) and TTS (gTTS)."""

import os
import tempfile

import streamlit as st

from config import SUPPORTED_LANGS, WHISPER_MODEL, WHISPER_COMPUTE


# ── STT ──────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_whisper():
    from faster_whisper import WhisperModel
    return WhisperModel(WHISPER_MODEL, compute_type=WHISPER_COMPUTE)


def transcribe_audio(audio_bytes: bytes) -> tuple[str, str, float]:
    """Return (text, language_code, avg_logprob_confidence)."""
    model = load_whisper()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        path = f.name
    try:
        segments, info = model.transcribe(
            path,
            beam_size=5,
            best_of=5,
            temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            condition_on_previous_text=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=300),
            word_timestamps=False,
        )
        segs = list(segments)
        text = " ".join(s.text.strip() for s in segs).strip()
        avg_conf = (
            sum(s.avg_logprob for s in segs) / len(segs) if segs else -1.0
        )
        lang = info.language if info.language in SUPPORTED_LANGS else "en"
        return text, lang, avg_conf
    finally:
        os.unlink(path)


# ── TTS ──────────────────────────────────────────────────────────────────────

def text_to_speech(text: str, lang: str = "en") -> str | None:
    """Synthesise speech; returns path to mp3 or None on failure."""
    if not text:
        return None
    from gtts import gTTS

    safe_lang = lang if lang in SUPPORTED_LANGS else "en"
    out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    out.close()
    try:
        gTTS(text=text, lang=safe_lang, slow=False).save(out.name)
        return out.name
    except Exception:
        pass
    # pyttsx3 fallback
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.save_to_file(text, out.name)
        engine.runAndWait()
        return out.name
    except Exception:
        return None
