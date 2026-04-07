import os
import streamlit as st
from streamlit_mic_recorder import mic_recorder

from UI.styles import GLOBAL_CSS
from UI.components import (
    render_header,
    render_orb,
    render_chat_history,
    render_policy_card,
    render_low_confidence_warning,
    render_footer,
)
from utils.speech import transcribe_audio, text_to_speech
from agents.voice_agent import graph

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Voice Agent",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)  # fix: was STYLES

# ─────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "text": "", "intent": "", "response": "",
        "lang": "en", "confidence": 0.0,
        "appointment": None, "policy": None, "history": [],
    }
if "orb_state" not in st.session_state:
    st.session_state.orb_state = "idle"

# ─────────────────────────────────────────
# UI LAYOUT
# ─────────────────────────────────────────
st.markdown(render_header(), unsafe_allow_html=True)
st.markdown(render_orb(st.session_state.orb_state), unsafe_allow_html=True)

st.markdown("<div class='scan-line'></div>", unsafe_allow_html=True)

# Chat history
history = st.session_state.agent_state.get("history", [])
if history:
    st.markdown(render_chat_history(history), unsafe_allow_html=True)  # fix: was render_history

# Policy card
pol = st.session_state.agent_state.get("policy")
if pol:
    st.markdown(render_policy_card(pol), unsafe_allow_html=True)

st.markdown("<div class='scan-line'></div>", unsafe_allow_html=True)

# Controls row
col1, col2 = st.columns([4, 1])
with col2:
    if st.button("🗑 Clear"):
        st.session_state.agent_state["history"] = []
        st.session_state.agent_state["policy"] = None
        st.session_state.orb_state = "idle"
        st.rerun()

st.markdown("#### 🎤 Tap to speak")
audio = mic_recorder(
    start_prompt="Hold & Speak",
    stop_prompt="Release to Send",
    key="mic",
)

# ─────────────────────────────────────────
# PROCESS AUDIO
# ─────────────────────────────────────────
if audio and audio.get("bytes"):
    st.session_state.orb_state = "thinking"

    # STT
    try:
        text, lang, conf = transcribe_audio(audio["bytes"])
    except Exception:
        text, lang, conf = "", "en", -2.0

    if not text:
        conf = -2.0

    # Update state and run graph
    state = st.session_state.agent_state
    state.update({"text": text, "lang": lang, "confidence": conf})

    try:
        result = graph.invoke(state)
    except Exception as e:
        result = {**state, "intent": "error", "response": f"Agent error: {e}"}

    response = result.get("response", "Sorry, I encountered an error.")

    # Append to history
    hist = result.get("history", [])
    if text:
        hist.append({"role": "user", "text": text, "intent": None})
    hist.append({"role": "bot", "text": response, "intent": result.get("intent", "")})
    result["history"] = hist

    st.session_state.agent_state = result
    st.session_state.orb_state = "speaking"

    # TTS playback
    audio_path = text_to_speech(response, lang)
    if audio_path:
        with open(audio_path, "rb") as f:
            st.audio(f.read(), format="audio/mp3", autoplay=True)
        os.unlink(audio_path)

    st.session_state.orb_state = "idle"
    st.rerun()

# ─────────────────────────────────────────
# LOW CONFIDENCE WARNING
# ─────────────────────────────────────────
conf = st.session_state.agent_state.get("confidence", 0.0)
history = st.session_state.agent_state.get("history", [])
if conf < -1.0 and st.session_state.orb_state == "idle" and history:
    st.markdown(render_low_confidence_warning(), unsafe_allow_html=True)

st.markdown(render_footer(), unsafe_allow_html=True)