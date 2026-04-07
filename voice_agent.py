"""LangGraph voice agent: intent detection, nodes, and compiled graph."""

import re
import datetime
from typing import TypedDict, Optional, Dict, List

from langgraph.graph import StateGraph

from utils.llm import generate_gemini_api
from utils.policy import lookup_policy


# ── State ─────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    text: str
    intent: str
    response: str
    lang: str
    confidence: float
    appointment: Optional[Dict]
    policy: Optional[Dict]
    history: List[Dict]


# ── Intent patterns (most-specific first) ────────────────────────────────────

INTENT_PATTERNS = [
    ("policy_check", [r"\bpolicy\b", r"\binsurance\b", r"\bcoverage\b", r"\bclaim\b", r"\bpremium\b"]),
    ("reschedule",   [r"\breschedule\b", r"\bchange.*appoint\b", r"\bmove.*appoint\b", r"\bpostpone\b", r"\bshift.*appoint\b"]),
    ("schedule",     [r"\bschedule\b", r"\bbook\b.*appoint\b", r"\bfix.*appoint\b", r"\bset up.*appoint\b", r"\bnew appoint\b"]),
    ("query_appt",   [r"\bwhen\b.*\bappoint\b", r"\bmy appoint\b", r"\bcheck.*appoint\b", r"\bappoint.*detail\b"]),
    ("cancel",       [r"\bcancel\b", r"\bdelete.*appoint\b", r"\bremove.*appoint\b"]),
    ("greeting",     [r"^\s*(hi|hello|hey|good\s+(morning|afternoon|evening)|namaste|namaskar)\b"]),
    ("farewell",     [r"\b(bye|goodbye|see you|thanks|thank you|that.?s all)\b"]),
    ("help",         [r"\bhelp\b", r"\bwhat can you\b", r"\bwhat do you\b", r"\boptions\b"]),
    ("repeat",       [r"\brepeat\b", r"\bsay again\b", r"\bpardon\b", r"\bwhat did you say\b"]),
    ("unknown",      []),
]


def detect_intent(text: str) -> str:
    t = text.lower()
    for intent, patterns in INTENT_PATTERNS:
        if intent == "unknown":
            return "unknown"
        for p in patterns:
            if re.search(p, t):
                return intent
    return "unknown"


# ── Nodes ─────────────────────────────────────────────────────────────────────

def intent_node(state: AgentState) -> AgentState:
    return {**state, "intent": detect_intent(state["text"])}


def greeting_node(state: AgentState) -> AgentState:
    hour = datetime.datetime.now().hour
    tod = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
    return {**state, "response": (
        f"{tod}! I'm your Voice Agent AI assistant. "
        "I can help you schedule appointments, check policy status, and more. "
        "How can I assist you?"
    )}


def farewell_node(state: AgentState) -> AgentState:
    return {**state, "response": "Thank you for reaching out! Have a wonderful day. Goodbye!"}


def help_node(state: AgentState) -> AgentState:
    return {**state, "response": (
        "Here's what I can do: "
        "1) Schedule, reschedule, cancel or check appointments. "
        "2) Check your insurance policy status and coverage details. "
        "3) Answer general questions. "
        "Just speak naturally!"
    )}


def repeat_node(state: AgentState) -> AgentState:
    for turn in reversed(state.get("history", [])):
        if turn.get("role") == "bot":
            return {**state, "response": turn["text"]}
    return {**state, "response": "I don't have a previous response to repeat."}


def policy_check_node(state: AgentState) -> AgentState:
    policy = lookup_policy(state["text"])
    if policy:
        r = (
            f"Policy {policy['id']} found. "
            f"Holder: {policy['holder']}. "
            f"Type: {policy['type']}. "
            f"Status: {policy['status']}. "
            f"Coverage: {policy['coverage']}. "
        )
        if policy["claims_pending"]:
            r += f"You have {policy['claims_pending']} pending claim(s). "
        if policy["status"] in ("Expiring Soon", "Lapsed"):
            r += "Please renew your policy to maintain coverage."
        return {**state, "policy": policy, "response": r}
    return {**state, "response": "I couldn't find a matching policy. Please provide your policy number or registered name."}


def _extract_datetime(text: str, fallback_date="tomorrow", fallback_time="10:00 AM"):
    date, time_str = fallback_date, fallback_time
    for word in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        if word in text.lower():
            date = word.capitalize()
            break
    times = re.findall(r'\b\d{1,2}(?::\d{2})?\s*(?:am|pm)\b', text, re.IGNORECASE)
    if times:
        time_str = times[0].upper()
    return date, time_str


def schedule_node(state: AgentState) -> AgentState:
    date, time_str = _extract_datetime(state["text"])
    appt = {"date": date, "time": time_str}
    return {**state, "appointment": appt, "response": f"Done! Your appointment is scheduled for {date} at {time_str}. I'll send you a reminder."}


def reschedule_node(state: AgentState) -> AgentState:
    if not state.get("appointment"):
        return {**state, "response": "You don't have an existing appointment. Would you like to book a new one?"}
    old = state["appointment"]
    date, time_str = _extract_datetime(state["text"], old["date"], old["time"])
    appt = {"date": date, "time": time_str}
    return {**state, "appointment": appt, "response": f"Rescheduled! Your new appointment is on {date} at {time_str}."}


def query_appt_node(state: AgentState) -> AgentState:
    a = state.get("appointment")
    if a:
        return {**state, "response": f"Your appointment is on {a['date']} at {a['time']}."}
    return {**state, "response": "You have no upcoming appointments. Shall I schedule one?"}


def cancel_node(state: AgentState) -> AgentState:
    if state.get("appointment"):
        return {**state, "appointment": None, "response": "Your appointment has been cancelled. Let me know if you'd like to rebook."}
    return {**state, "response": "You have no appointment to cancel."}


def low_confidence_node(state: AgentState) -> AgentState:
    return {**state, "response": "I didn't catch that clearly. Could you please repeat or rephrase?"}


def default_node(state: AgentState) -> AgentState:
    prompt = (
        "You are a multilingual AI voice assistant.\n\n"
        "Capabilities:\n"
        "- Handle appointments (schedule, reschedule, cancel, query)\n"
        "- Handle insurance policy queries\n"
        "- Answer general questions naturally\n\n"
        "Rules:\n"
        "- Respond in SAME language as user (Hindi / English / Marathi)\n"
        "- Keep responses short and conversational\n"
        "- Be clear and helpful\n"
        "- If user intent is unclear, ask a follow-up\n\n"
        f"User: {state['text']}"
    )
    resp = generate_gemini_api(prompt, state["text"])
    return {**state, "response": resp}


# ── Graph ─────────────────────────────────────────────────────────────────────

def _build_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    nodes = {
        "intent":       intent_node,
        "greeting":     greeting_node,
        "farewell":     farewell_node,
        "help":         help_node,
        "repeat":       repeat_node,
        "policy_check": policy_check_node,
        "schedule":     schedule_node,
        "reschedule":   reschedule_node,
        "query_appt":   query_appt_node,
        "cancel":       cancel_node,
        "low_conf":     low_confidence_node,
        "default":      default_node,
    }
    for name, fn in nodes.items():
        builder.add_node(name, fn)

    builder.set_entry_point("intent")

    def route(s: AgentState) -> str:
        if s["confidence"] < -1.0:
            return "low_conf"
        return s["intent"]

    dest_nodes = list(nodes.keys())
    dest_nodes.remove("intent")
    dest_nodes.append("unknown")

    builder.add_conditional_edges("intent", route, {
        "greeting":     "greeting",
        "farewell":     "farewell",
        "help":         "help",
        "repeat":       "repeat",
        "policy_check": "policy_check",
        "schedule":     "schedule",
        "reschedule":   "reschedule",
        "query_appt":   "query_appt",
        "cancel":       "cancel",
        "low_conf":     "low_conf",
        "unknown":      "default",
    })

    for node in ["greeting", "farewell", "help", "repeat", "policy_check",
                 "schedule", "reschedule", "query_appt", "cancel", "low_conf", "default"]:
        builder.set_finish_point(node)

    return builder.compile()


graph = _build_graph()
