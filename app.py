import streamlit as st
import tempfile
import requests
import io
import re
from PIL import Image
from faster_whisper import WhisperModel
from gtts import gTTS
import pyttsx3
from streamlit_mic_recorder import mic_recorder

from langgraph.graph import StateGraph
from typing import TypedDict, Optional, Dict

# ---------------- CONFIG ----------------
API_URL = "http://127.0.0.1:8000/process"  # change if needed

whisper_model = WhisperModel("base")
engine = pyttsx3.init()

# ---------------- UI STYLE ----------------
st.set_page_config(page_title="AI Voice Agent", layout="centered")

st.markdown("""
<style>
.chat-box {
    background: #1e293b;
    padding: 15px;
    border-radius: 12px;
    margin-top: 10px;
    color: white;
}
.mic {
    width: 70px;
    height: 70px;
    background: #2563eb;
    border-radius: 50%;
    margin: auto;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(37,99,235,0.7); }
    70% { box-shadow: 0 0 0 20px rgba(37,99,235,0); }
}
.speaking {
    animation: wave 1s infinite;
}
@keyframes wave {
    50% { transform: scale(1.08); }
}
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------

def transcribe(audio_path):
    segments, info = whisper_model.transcribe(audio_path)
    text = "".join([seg.text for seg in segments])
    return text.strip(), info.language


def speak(text, lang):
    if not text:
        text = "Sorry, I could not understand."

    file = "response.mp3"

    try:
        gTTS(text=text, lang=lang if lang in ["hi","mr","en"] else "en").save(file)
        return file
    except:
        pass

    try:
        engine.save_to_file(text, file)
        engine.runAndWait()
        return file
    except:
        return None


def call_backend(text):
    try:
        payload = {"prompt": text, "ocr_text": ""}
        res = requests.post(API_URL, json=payload, timeout=8)
        data = res.json()
        return data.get("response") or str(data)
    except:
        return "Backend not reachable"


def generate_with_image(image, prompt):
    try:
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        buffer.seek(0)

        res = requests.post(
            "http://192.168.0.95:8090/openai_generate_image",
            params={"prompt": prompt},
            files={"file": ("image.jpg", buffer, "image/jpeg")}
        )
        return res.json().get("response")
    except:
        return "Image processing failed"

# ---------------- LANGGRAPH ----------------

class AgentState(TypedDict):
    text: str
    intent: str
    response: str
    appointment: Optional[Dict]


def detect_intent_node(state):
    t = state["text"].lower()

    reschedule = [r"\breschedule\b", r"\bchange\b", r"\bmove\b", r"\bshift\b", r"\bpostpone\b"]
    schedule = [r"\bschedule\b", r"\bbook\b", r"\bfix\b", r"\bset up\b", r"\barrange\b"]
    query = [r"\bwhen\b.*\bappointment\b", r"\bmy appointment\b"]
    cancel = [r"\bcancel\b", r"\bdelete\b"]

    for p in reschedule:
        if re.search(p, t): return {**state, "intent": "reschedule"}

    for p in schedule:
        if re.search(p, t): return {**state, "intent": "schedule"}

    for p in query:
        if re.search(p, t): return {**state, "intent": "query"}

    for p in cancel:
        if re.search(p, t): return {**state, "intent": "cancel"}

    return {**state, "intent": "unknown"}


def schedule_node(state):
    return {
        **state,
        "appointment": {"date": "tomorrow", "time": "10 AM"},
        "response": "Appointment scheduled for tomorrow at 10 AM."
    }


def reschedule_node(state):
    if state.get("appointment"):
        return {
            **state,
            "appointment": {"date": "Friday", "time": "5 PM"},
            "response": "Appointment rescheduled to Friday at 5 PM."
        }
    return {**state, "response": "No appointment found."}


def query_node(state):
    appt = state.get("appointment")
    if appt:
        return {**state, "response": f"Your appointment is on {appt['date']} at {appt['time']}."}
    return {**state, "response": "No appointment scheduled."}


def cancel_node(state):
    if state.get("appointment"):
        return {**state, "appointment": None, "response": "Appointment cancelled."}
    return {**state, "response": "No appointment to cancel."}


def default_node(state):
    return {**state, "response": call_backend(state["text"])}


builder = StateGraph(AgentState)

builder.add_node("intent", detect_intent_node)
builder.add_node("schedule", schedule_node)
builder.add_node("reschedule", reschedule_node)
builder.add_node("query", query_node)
builder.add_node("cancel", cancel_node)
builder.add_node("default", default_node)

builder.set_entry_point("intent")

builder.add_conditional_edges(
    "intent",
    lambda s: s["intent"],
    {
        "schedule": "schedule",
        "reschedule": "reschedule",
        "query": "query",
        "cancel": "cancel",
        "unknown": "default"
    }
)

builder.set_finish_point("schedule")
builder.set_finish_point("reschedule")
builder.set_finish_point("query")
builder.set_finish_point("cancel")
builder.set_finish_point("default")

graph = builder.compile()

# ---------------- UI ----------------

st.title("🎤 AI Voice Agent")

if "state" not in st.session_state:
    st.session_state["state"] = {
        "text": "", "intent": "", "response": "", "appointment": None
    }

if "greeted" not in st.session_state:
    st.session_state["greeted"] = True
    greet = "Hello! I can schedule, reschedule, cancel or check your appointment."
    st.markdown(f"<div class='chat-box'>{greet}</div>", unsafe_allow_html=True)
    st.audio(speak(greet, "en"))

st.markdown("<div class='mic'></div>", unsafe_allow_html=True)

img_file = st.file_uploader("Upload Image (optional)")
image = Image.open(img_file) if img_file else None

audio = mic_recorder(start_prompt="🎤 Speak", stop_prompt="⏹️ Stop")

if audio:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio["bytes"])
        path = tmp.name

    text, lang = transcribe(path)

    st.markdown(f"<div class='chat-box'><b>You:</b><br>{text}</div>", unsafe_allow_html=True)

    state = st.session_state["state"]
    state["text"] = text

    result = graph.invoke(state)
    st.session_state["state"] = result

    response = result.get("response", "Error")

    if image:
        response = generate_with_image(image, text)

    st.markdown(f"<div class='chat-box speaking'><b>Bot:</b><br>{response}</div>", unsafe_allow_html=True)

    audio_out = speak(response, lang)
    if audio_out:
        st.audio(audio_out)