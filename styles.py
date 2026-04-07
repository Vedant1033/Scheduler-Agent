"""Holographic CSS theme for Voice Agent."""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

:root {
  --bg:        #040d1a;
  --surface:   #071428;
  --ring-1:    #00e5ff;
  --ring-2:    #7c3aed;
  --ring-3:    #06b6d4;
  --text:      #e0f2fe;
  --muted:     #64748b;
  --user-bg:   rgba(0,229,255,0.07);
  --bot-bg:    rgba(124,58,237,0.10);
  --ok:        #22d3ee;
  --warn:      #fbbf24;
  --err:       #f87171;
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Rajdhani', sans-serif !important;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stSidebar"] { background: var(--surface) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 1rem 5rem !important; max-width: 760px !important; }

/* ── Title ── */
.app-title {
  text-align: center;
  font-family: 'Orbitron', monospace;
  font-size: 2.4rem;
  font-weight: 900;
  letter-spacing: 0.25em;
  background: linear-gradient(90deg, var(--ring-1), var(--ring-2), var(--ring-3));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.2rem;
}
.app-sub {
  text-align: center;
  color: var(--muted);
  font-size: 0.82rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  margin-bottom: 2rem;
}

/* ── Orb ── */
.orb-wrapper {
  display: flex; justify-content: center; align-items: center;
  height: 220px; margin: 0.5rem 0 1.5rem; position: relative;
}
.orb {
  width: 110px; height: 110px; border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #00e5ff55, #7c3aed88 60%, #040d1a);
  box-shadow: 0 0 30px #00e5ff55, 0 0 60px #7c3aed44, inset 0 0 30px #00000099;
  position: relative; z-index: 3; transition: transform 0.3s ease;
}
.orb.listening { animation: orb-pulse 0.8s ease-in-out infinite alternate; }
.orb.speaking  { animation: orb-wave  1.2s ease-in-out infinite; }
@keyframes orb-pulse {
  from { box-shadow: 0 0 30px #00e5ff88, 0 0 60px #7c3aed55; transform: scale(1);    }
  to   { box-shadow: 0 0 70px #00e5ffcc, 0 0 120px #7c3aed99; transform: scale(1.12);}
}
@keyframes orb-wave {
  0%,100% { transform: scale(1.0);  box-shadow: 0 0 40px #7c3aedaa, 0 0 80px #06b6d455;  }
  50%     { transform: scale(1.08); box-shadow: 0 0 80px #7c3aeddd, 0 0 120px #06b6d4aa; }
}

.ring {
  position: absolute; border-radius: 50%;
  border: 1.5px solid transparent;
  top: 50%; left: 50%; transform-origin: center;
}
.ring-1 { width:150px; height:150px; margin:-75px 0 0 -75px;
           border-top-color:var(--ring-1); border-right-color:var(--ring-1);
           animation:spin-cw 3s linear infinite; opacity:0.6; }
.ring-2 { width:185px; height:185px; margin:-92.5px 0 0 -92.5px;
           border-bottom-color:var(--ring-2); border-left-color:var(--ring-2);
           animation:spin-ccw 5s linear infinite; opacity:0.45; }
.ring-3 { width:220px; height:220px; margin:-110px 0 0 -110px;
           border-top-color:var(--ring-3); border-right-color:var(--ring-3);
           animation:spin-cw 8s linear infinite; opacity:0.25; }
@keyframes spin-cw  { to { transform: rotate(360deg);  } }
@keyframes spin-ccw { to { transform: rotate(-360deg); } }

.waveform {
  display:flex; align-items:center; gap:3px;
  position:absolute; bottom:28px; height:32px;
}
.bar { width:3px; background:var(--ring-1); border-radius:3px; opacity:0.4;
       animation:bar-idle 2s ease-in-out infinite; }
.waveform.active .bar { opacity:1; }
.bar:nth-child(1)  { animation-duration:1.1s;  height:8px;  }
.bar:nth-child(2)  { animation-duration:0.9s;  height:18px; animation-delay:0.1s;  }
.bar:nth-child(3)  { animation-duration:1.3s;  height:28px; animation-delay:0.2s;  }
.bar:nth-child(4)  { animation-duration:0.8s;  height:20px; animation-delay:0.05s; }
.bar:nth-child(5)  { animation-duration:1.2s;  height:32px; animation-delay:0.15s; }
.bar:nth-child(6)  { animation-duration:1.0s;  height:22px; animation-delay:0.3s;  }
.bar:nth-child(7)  { animation-duration:1.4s;  height:14px; animation-delay:0.1s;  }
.bar:nth-child(8)  { animation-duration:0.95s; height:26px; animation-delay:0.2s;  }
.bar:nth-child(9)  { animation-duration:1.15s; height:10px; animation-delay:0.08s; }
.bar:nth-child(10) { animation-duration:1.05s; height:20px; animation-delay:0.25s; }
@keyframes bar-idle { 0%,100% { transform:scaleY(0.4); } 50% { transform:scaleY(1.0); } }

/* ── Status badge ── */
.status-badge {
  text-align:center; font-family:'Orbitron',monospace;
  font-size:0.65rem; letter-spacing:0.25em;
  padding:4px 14px; border-radius:20px;
  display:inline-block; margin:0 auto 1.5rem; border:1px solid;
}
.status-idle   { color:var(--muted);  border-color:var(--muted);  background:rgba(100,116,139,0.08); }
.status-listen { color:var(--ok);     border-color:var(--ok);     background:rgba(34,211,238,0.08);  animation:blink 1s infinite; }
.status-think  { color:var(--warn);   border-color:var(--warn);   background:rgba(251,191,36,0.08);  }
.status-speak  { color:var(--ring-2); border-color:var(--ring-2); background:rgba(124,58,237,0.10);  }
.status-err    { color:var(--err);    border-color:var(--err);    background:rgba(248,113,113,0.08); }
@keyframes blink { 50% { opacity:0.4; } }

/* ── Chat bubbles ── */
.chat-container { display:flex; flex-direction:column; gap:10px; margin-bottom:1.5rem; }
.bubble {
  padding:12px 16px; border-radius:14px;
  font-size:0.95rem; line-height:1.55; max-width:90%;
  position:relative; animation:fade-up 0.35s ease both;
}
@keyframes fade-up {
  from { opacity:0; transform:translateY(10px); }
  to   { opacity:1; transform:translateY(0);    }
}
.bubble-user { background:var(--user-bg); border:1px solid rgba(0,229,255,0.18);
               align-self:flex-end; border-bottom-right-radius:4px; }
.bubble-bot  { background:var(--bot-bg);  border:1px solid rgba(124,58,237,0.22);
               align-self:flex-start; border-bottom-left-radius:4px; }
.bubble-label { font-family:'Orbitron',monospace; font-size:0.58rem;
                letter-spacing:0.2em; opacity:0.55; margin-bottom:4px; text-transform:uppercase; }
.bubble-user .bubble-label { color:var(--ring-1); }
.bubble-bot  .bubble-label { color:var(--ring-2); }
.bubble-intent { font-size:0.68rem; opacity:0.5; margin-top:6px;
                 font-family:'Orbitron',monospace; letter-spacing:0.1em; }

/* ── Policy card ── */
.policy-card {
  background:rgba(6,182,212,0.06); border:1px solid rgba(6,182,212,0.25);
  border-radius:12px; padding:14px 18px; margin:1rem 0; animation:fade-up 0.4s ease both;
}
.policy-card h4 {
  font-family:'Orbitron',monospace; font-size:0.72rem;
  letter-spacing:0.2em; color:var(--ring-3); margin:0 0 8px 0; text-transform:uppercase;
}
.policy-row {
  display:flex; justify-content:space-between;
  padding:5px 0; border-bottom:1px solid rgba(255,255,255,0.05); font-size:0.88rem;
}
.policy-row:last-child { border-bottom:none; }
.policy-val           { font-weight:600; color:var(--ok);  }
.policy-val.warn      { color:var(--warn); }
.policy-val.err       { color:var(--err);  }

/* ── Buttons ── */
.stButton > button {
  background:linear-gradient(135deg,#00e5ff22,#7c3aed33) !important;
  border:1px solid rgba(0,229,255,0.3) !important;
  color:var(--text) !important;
  font-family:'Orbitron',monospace !important;
  font-size:0.7rem !important; letter-spacing:0.15em !important;
  border-radius:8px !important; padding:0.5rem 1.2rem !important;
  transition:all 0.2s ease !important;
}
.stButton > button:hover {
  border-color:var(--ring-1) !important;
  box-shadow:0 0 16px rgba(0,229,255,0.25) !important;
}

/* ── Misc ── */
.scan-line {
  height:1px;
  background:linear-gradient(90deg,transparent,var(--ring-1),var(--ring-2),transparent);
  margin:1.5rem 0; opacity:0.35;
}
iframe { border-radius:10px; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:var(--ring-2); border-radius:4px; }
</style>
"""
