"""Reusable HTML render helpers for Voice Agent UI."""


ORB_STATE_CSS = {
    "idle":      "",
    "listening": "listening",
    "thinking":  "",
    "speaking":  "speaking",
}

STATUS_MAP = {
    "idle":      ("STANDBY",      "status-idle"),
    "listening": ("LISTENING…",   "status-listen"),
    "thinking":  ("PROCESSING…",  "status-think"),
    "speaking":  ("RESPONDING…",  "status-speak"),
    "error":     ("ERROR",        "status-err"),
}


def render_header() -> str:
    return (
        "<div class='app-title'>VOICE AGENT</div>"
        "<div class='app-sub'>AI-Powered Voice Assistant</div>"
    )


def render_orb(orb_state: str) -> str:
    orb_cls  = ORB_STATE_CSS.get(orb_state, "")
    wave_cls = "active" if orb_state in ("listening", "speaking") else ""
    status_text, status_cls = STATUS_MAP.get(orb_state, ("STANDBY", "status-idle"))
    bars = "".join('<div class="bar"></div>' * 10)
    return f"""
<div class='orb-wrapper'>
  <div class='ring ring-3'></div>
  <div class='ring ring-2'></div>
  <div class='ring ring-1'></div>
  <div class='orb {orb_cls}'></div>
  <div class='waveform {wave_cls}'>{bars}</div>
</div>
<div style='text-align:center'>
  <span class='status-badge {status_cls}'>{status_text}</span>
</div>
"""


def render_chat_history(history: list) -> str:
    if not history:
        return ""
    bubbles = []
    for turn in history[-10:]:
        role_cls   = "bubble-user" if turn["role"] == "user" else "bubble-bot"
        role_label = "YOU" if turn["role"] == "user" else "AGENT"
        intent_tag = (
            f"<div class='bubble-intent'>⬡ {turn.get('intent','').upper()}</div>"
            if turn.get("intent") and turn["role"] == "bot"
            else ""
        )
        bubbles.append(f"""
        <div class='bubble {role_cls}'>
          <div class='bubble-label'>{role_label}</div>
          {turn['text']}
          {intent_tag}
        </div>""")
    return "<div class='chat-container'>" + "".join(bubbles) + "</div>"


def render_policy_card(pol: dict) -> str:
    status_color = (
        "ok" if pol["status"] == "Active"
        else ("warn" if pol["status"] == "Expiring Soon" else "err")
    )
    claims_color = "err" if pol["claims_pending"] else "ok"
    return f"""
<div class='policy-card'>
  <h4>📋 Policy Status — {pol['id']}</h4>
  <div class='policy-row'><span>Holder</span>       <span class='policy-val'>{pol['holder']}</span></div>
  <div class='policy-row'><span>Type</span>         <span class='policy-val'>{pol['type']}</span></div>
  <div class='policy-row'><span>Status</span>       <span class='policy-val {status_color}'>{pol['status']}</span></div>
  <div class='policy-row'><span>Coverage</span>     <span class='policy-val'>{pol['coverage']}</span></div>
  <div class='policy-row'><span>Premium Due</span>  <span class='policy-val warn'>{pol['premium_due']}</span></div>
  <div class='policy-row'><span>Pending Claims</span><span class='policy-val {claims_color}'>{pol['claims_pending']}</span></div>
</div>
"""


def render_low_confidence_warning() -> str:
    return """
<div style='text-align:center; color:#fbbf24; font-size:0.8rem; margin-top:0.5rem;
     font-family:Orbitron,monospace; letter-spacing:0.1em;'>
  ⚠ Low audio confidence — please speak clearly near the mic
</div>"""


def render_footer() -> str:
    return """
<div style='text-align:center; margin-top:3rem; color:#334155;
     font-size:0.72rem; font-family:Orbitron,monospace; letter-spacing:0.2em;'>
  VOICE AGENT v2.0 · POWERED BY FASTER-WHISPER + LANGGRAPH
</div>
"""
