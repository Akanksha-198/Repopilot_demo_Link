"""Glassmorphism + minimal theme for the Streamlit UI (CSS only, no logic)."""
import streamlit as st

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=Manrope:wght@400;500;600&display=swap');

:root {
  --ink: #E8ECF6; --muted: #8B94AB; --line: rgba(255,255,255,.12);
  --accent: #8B9CFF; --accent2: #5EEAD4; --ok: #5EE6A8; --warn: #F5C86B; --bad: #FF7A8A;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
  font-family: 'Manrope', system-ui, sans-serif; color: var(--ink);
}
.stApp {
  background:
    radial-gradient(900px 600px at 6% -8%, rgba(79,91,255,.40), transparent 60%),
    radial-gradient(800px 560px at 102% 106%, rgba(20,184,166,.26), transparent 60%),
    #070B18;
  background-attachment: fixed;
}
[data-testid="stHeader"] { background: transparent; }
footer { visibility: hidden; }

/* the whole page is one frosted glass sheet */
.block-container {
  max-width: 980px; margin-top: 1.4rem; padding: 2.2rem 2.2rem 3rem;
  background: rgba(255,255,255,.05); border: 1px solid var(--line); border-radius: 24px;
  -webkit-backdrop-filter: blur(26px) saturate(140%); backdrop-filter: blur(26px) saturate(140%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.07), 0 30px 80px -30px rgba(0,0,0,.7);
}
h1, h2, h3, h4 { font-family: 'Bricolage Grotesque', 'Segoe UI', sans-serif; letter-spacing: -0.02em; color: var(--ink); }
p, li, label, span { color: var(--ink); }
[data-testid="stCaptionContainer"], .stCaption { color: var(--muted) !important; }
hr { border-color: var(--line) !important; }

/* ---- custom classes used by streamlit_app.py ---- */
.main-title {
  font: 700 42px 'Bricolage Grotesque', sans-serif; letter-spacing: -0.03em; margin: 0;
  background: linear-gradient(120deg, var(--accent), var(--accent2));
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; display: inline-block;
}
.subtitle { color: var(--muted); font-size: 15px; margin: 2px 0 18px; }
.rp-card { display: none; }               /* old wrapper divs are empty in Streamlit; the glass sheet replaces them */
.rp-card-title { font: 700 20px 'Bricolage Grotesque', sans-serif; margin: 10px 0 12px; }

.rp-steps { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
.rp-step { padding: 5px 14px; border-radius: 999px; font-size: 12.5px; font-weight: 600; color: var(--muted);
  border: 1px solid var(--line); background: rgba(255,255,255,.04); }
.rp-step-active { color: var(--ink); background: rgba(139,156,255,.16); border-color: rgba(139,156,255,.55); }
.rp-step-done { color: var(--ok); border-color: rgba(94,230,168,.35); background: rgba(94,230,168,.08); }

.rp-badge { display: inline-block; padding: 3px 11px; border-radius: 999px; font-size: 12.5px; margin: 2px 5px 2px 0;
  background: rgba(255,255,255,.07); border: 1px solid var(--line); color: var(--muted); }
.rp-repo-bar { padding: 12px 18px; border-radius: 14px; margin-bottom: 14px;
  background: rgba(255,255,255,.05); border: 1px solid var(--line); }
.rp-repo-name { font-weight: 600; font-size: 15.5px; color: var(--ink); }
.rp-repo-path { color: var(--muted); font-size: 12px; word-break: break-all; }

.rp-result-banner { padding: 16px 20px; border-radius: 16px; margin-bottom: 16px; border: 1px solid var(--line); background: rgba(255,255,255,.05); }
.rp-result-ok   { background: rgba(94,230,168,.09);  border-color: rgba(94,230,168,.40); }
.rp-result-warn { background: rgba(245,200,107,.09); border-color: rgba(245,200,107,.40); }
.rp-result-bad  { background: rgba(255,122,138,.09); border-color: rgba(255,122,138,.40); }
.rp-result-title { font: 700 18px 'Bricolage Grotesque', sans-serif; margin-bottom: 6px; }
.rp-result-row { font-size: 14px; color: var(--muted); margin-top: 2px; }
.rp-result-row code { color: var(--ink); }

/* ---- native Streamlit widgets ---- */
.stButton > button, .stDownloadButton > button {
  border-radius: 12px; border: 1px solid var(--line); background: rgba(255,255,255,.08); color: var(--ink);
  font-weight: 600; transition: background .15s, transform .15s, border-color .15s;
}
.stButton > button:hover { background: rgba(255,255,255,.14); border-color: rgba(255,255,255,.25); color: var(--ink); }
.stButton > button:active { transform: translateY(1px); }
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
  border: 0; color: #0A0F1E; background: linear-gradient(120deg, var(--accent), var(--accent2));
}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover { filter: brightness(1.08); color: #0A0F1E; }

[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"] {
  background: rgba(0,0,0,.28) !important; border: 1px solid var(--line) !important; border-radius: 12px !important;
}
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea, [data-baseweb="base-input"] input {
  color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important; background: transparent !important;
}
input::placeholder, textarea::placeholder { color: #5D6684 !important; }

[data-testid="stExpander"] { background: rgba(255,255,255,.045); border: 1px solid var(--line) !important; border-radius: 16px; overflow: hidden; }
[data-testid="stExpander"] details { border: 0 !important; }
[data-testid="stExpander"] summary { color: var(--ink); }

.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { background: transparent; color: var(--muted); font-weight: 600; }
.stTabs [aria-selected="true"] { color: var(--ink); }
.stTabs [data-baseweb="tab-highlight"] { background: var(--accent); }
.stTabs [data-baseweb="tab-border"] { background: transparent; }

[data-testid="stAlert"] { border-radius: 14px; border: 1px solid var(--line); background: rgba(255,255,255,.05); }
[data-testid="stCode"] pre, .stCodeBlock pre, pre {
  background: rgba(0,0,0,.35) !important; border: 1px solid var(--line); border-radius: 12px;
}
[data-testid="stJson"] { background: rgba(0,0,0,.25); border-radius: 12px; padding: 8px; }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,.14); border-radius: 10px; }

@media (max-width: 720px) { .block-container { padding: 1.2rem 1rem 2rem; border-radius: 18px; margin-top: .6rem; } .main-title { font-size: 32px; } }
"""


def apply_theme():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
