"""Claymorphism + minimal theme (soft, puffy, pastel)."""
import streamlit as st


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600&family=Nunito:wght@500;600;700;800&display=swap');


/* =========================================================
   GLOBAL VARIABLES
   ========================================================= */

:root {
  --bg: #E9ECF8;
  --surface: #F4F6FD;
  --ink: #2A2F4F;
  --muted: #737A9C;

  --accent: #6C63FF;
  --accent-hi: #8A7DFF;

  --ok: #1F7F5C;
  --ok-bg: #D9F5EA;

  --warn: #9A6A05;
  --warn-bg: #FFF1CF;

  --bad: #B4374F;
  --bad-bg: #FFDDE3;

  --shadow-d: rgba(153,163,196,.50);
  --shadow-l: rgba(255,255,255,.95);

  --out:
    10px 10px 24px var(--shadow-d),
    -8px -8px 20px var(--shadow-l);

  --puffy:
    8px 8px 18px var(--shadow-d),
    -6px -6px 14px var(--shadow-l),
    inset 3px 3px 6px rgba(255,255,255,.95),
    inset -3px -3px 7px rgba(153,163,196,.28);

  --pressed:
    inset 6px 6px 12px rgba(153,163,196,.40),
    inset -6px -6px 12px rgba(255,255,255,.95);
}


/* =========================================================
   GLOBAL APP
   ========================================================= */

html,
body,
.stApp,
[data-testid="stAppViewContainer"] {
  font-family: 'Nunito', system-ui, sans-serif;
  color: var(--ink);
}

.stApp {
  background: var(--bg);
}

[data-testid="stHeader"] {
  background: transparent;
}

footer {
  visibility: hidden;
}


/* =========================================================
   MAIN CONTAINER
   ========================================================= */

.block-container {
  max-width: 980px;
  margin-top: 1.2rem;
  padding: 2.2rem 2.2rem 3rem;
  background: var(--surface);
  border-radius: 36px;

  box-shadow:
    16px 16px 40px var(--shadow-d),
    -12px -12px 32px var(--shadow-l);
}


/* =========================================================
   TYPOGRAPHY
   ========================================================= */

h1,
h2,
h3,
h4 {
  font-family: 'Fredoka', 'Nunito', sans-serif;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.01em;
}

p,
li,
label,
span,
div {
  color: inherit;
}

[data-testid="stCaptionContainer"],
.stCaption {
  color: var(--muted) !important;
}

hr {
  border: 0;
  height: 3px;
  border-radius: 3px;

  background: var(--bg);

  box-shadow:
    inset 1px 1px 2px var(--shadow-d),
    inset -1px -1px 2px var(--shadow-l);
}


/* Prevent long LLM markdown headings from becoming huge */
[data-testid="stTabs"] h1,
[data-testid="stTabs"] h2,
[data-testid="stTabs"] h3,
[data-testid="stTabs"] h4 {
  font-size: 1rem;
}


/* =========================================================
   REPOPILOT TITLE
   ========================================================= */

.main-title {
  font: 600 40px 'Fredoka', sans-serif;
  letter-spacing: -0.02em;
  display: inline-block;

  background:
    linear-gradient(
      135deg,
      var(--accent-hi),
      var(--accent)
    );

  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: var(--muted);
  font-size: 15px;
  margin: 0 0 18px;
  font-weight: 600;
}

.rp-card {
  display: none;
}

.rp-card-title {
  font: 600 20px 'Fredoka', sans-serif;
  margin: 8px 0 12px;
}


/* =========================================================
   STEP NAVIGATION
   ========================================================= */

.rp-steps {
  display: flex;
  gap: 10px;
  margin-bottom: 22px;
  flex-wrap: wrap;
}

.rp-step {
  padding: 7px 16px;
  border-radius: 999px;
  font-size: 12.5px;
  font-weight: 700;

  color: var(--muted);
  background: var(--surface);

  box-shadow: var(--pressed);
}

.rp-step-active {
  color: #fff;

  background:
    linear-gradient(
      145deg,
      var(--accent-hi),
      var(--accent)
    );

  box-shadow:
    6px 6px 14px rgba(108,99,255,.35),
    -4px -4px 10px var(--shadow-l),
    inset 2px 2px 4px rgba(255,255,255,.4);
}

.rp-step-done {
  color: var(--ok);
  background: var(--ok-bg);

  box-shadow:
    4px 4px 10px var(--shadow-d),
    -4px -4px 10px var(--shadow-l);
}


/* =========================================================
   BADGES
   ========================================================= */

.rp-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12.5px;
  font-weight: 700;
  margin: 3px 6px 3px 0;

  color: var(--muted);
  background: var(--surface);

  box-shadow: var(--puffy);
}


/* =========================================================
   REPOSITORY BAR
   ========================================================= */

.rp-repo-bar {
  padding: 14px 20px;
  border-radius: 22px;
  margin-bottom: 14px;

  background: var(--surface);
  box-shadow: var(--out);
}

.rp-repo-name {
  font: 600 16px 'Fredoka', sans-serif;
}

.rp-repo-path {
  color: var(--muted);
  font-size: 12px;
  word-break: break-all;
}


/* =========================================================
   RESULT BANNER
   ========================================================= */

.rp-result-banner {
  padding: 18px 22px;
  border-radius: 24px;
  margin-bottom: 18px;

  background: var(--surface);
  box-shadow: var(--out);
}

.rp-result-ok {
  background: var(--ok-bg);
}

.rp-result-warn {
  background: var(--warn-bg);
}

.rp-result-bad {
  background: var(--bad-bg);
}

.rp-result-title {
  font: 600 19px 'Fredoka', sans-serif;
  margin-bottom: 6px;
}

.rp-result-row {
  font-size: 14px;
  color: var(--muted);
  margin-top: 3px;
  font-weight: 600;
}

.rp-result-row code {
  color: var(--ink);
  background: rgba(255,255,255,.7);
  border-radius: 8px;
  padding: 1px 6px;
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button,
.stDownloadButton > button {
  border: 0;
  border-radius: 18px;
  padding: .6rem 1.2rem;
  min-height: 46px;

  font-weight: 800;
  color: var(--ink);

  background: var(--surface);

  box-shadow: var(--puffy);

  transition:
    box-shadow .15s,
    transform .15s;
}

.stButton > button:hover {
  color: var(--accent);
  transform: translateY(-1px);
}

.stButton > button:active {
  box-shadow: var(--pressed);
  transform: translateY(1px);
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
  color: #fff;

  background:
    linear-gradient(
      145deg,
      var(--accent-hi),
      var(--accent)
    );

  box-shadow:
    8px 8px 18px rgba(108,99,255,.38),
    -5px -5px 12px var(--shadow-l),
    inset 2px 2px 5px rgba(255,255,255,.45),
    inset -3px -3px 7px rgba(60,50,190,.35);
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
  color: #fff;
  filter: brightness(1.06);
}

.stButton > button p {
  color: inherit !important;
}


/* =========================================================
   FORM LABELS
   ========================================================= */

[data-testid="stTextInput"] label,
[data-testid="stTextInput"] label p,
[data-testid="stTextArea"] label,
[data-testid="stTextArea"] label p,
[data-testid="stTextInput"] [data-testid="stWidgetLabel"],
[data-testid="stTextArea"] [data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p {
  color: #17204A !important;
  -webkit-text-fill-color: #17204A !important;

  font-weight: 800 !important;
  opacity: 1 !important;
}


/* =========================================================
   DARK INPUT / TEXTAREA
   ========================================================= */

[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="textarea"] {
  background: #101735 !important;

  border: 0 !important;
  border-radius: 18px !important;

  box-shadow: var(--pressed) !important;
}


/* =========================================================
   WHITE TEXT INSIDE DARK INPUTS
   ========================================================= */

[data-baseweb="input"] input,
[data-baseweb="base-input"] input,
[data-baseweb="textarea"] textarea,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
input,
textarea {
  color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;

  background: transparent !important;

  font-weight: 600 !important;

  caret-color: #FFFFFF !important;

  opacity: 1 !important;
}


/* =========================================================
   INPUT PLACEHOLDER
   ========================================================= */

[data-baseweb="input"] input::placeholder,
[data-baseweb="textarea"] textarea::placeholder,
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder,
input::placeholder,
textarea::placeholder {
  color: #DDE2FF !important;
  -webkit-text-fill-color: #DDE2FF !important;

  opacity: .85 !important;
}


/* =========================================================
   DISABLED INPUTS
   ========================================================= */

[data-baseweb="input"] input:disabled,
[data-baseweb="base-input"] input:disabled,
[data-testid="stTextInput"] input:disabled {
  color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;
  opacity: 1 !important;
}


/* =========================================================
   REPOPILOT BLUE ROBOT ICON
   ========================================================= */

.rp-bot-icon {
  display: inline-block;

  color: #4D8DFF;
  -webkit-text-fill-color: #4D8DFF;

  filter:
    drop-shadow(
      0 4px 5px rgba(77,141,255,.22)
    );

  vertical-align: 2px;
}


/* =========================================================
   EXPANDERS
   ========================================================= */

[data-testid="stExpander"] {
  background: var(--surface);

  border: 0 !important;
  border-radius: 22px;

  box-shadow: var(--out);

  overflow: hidden;

  margin-top: 16px;
  margin-bottom: 18px;
}

[data-testid="stExpander"] details {
  border: 0 !important;
}

[data-testid="stExpander"] summary {
  font-weight: 800;
  padding: 14px 20px !important;
}

[data-testid="stExpander"] summary p {
  margin: 0 !important;
}


/* =========================================================
   REVIEW TABS
   IMPORTANT: EXTRA GAP BETWEEN SUMMARY / PLAN / WHAT CHANGES
   ========================================================= */

.stTabs [data-baseweb="tab-list"] {
  display: flex !important;

  gap: 18px !important;

  padding: 8px !important;

  margin-bottom: 18px !important;

  border-radius: 20px;

  background: transparent !important;

  box-shadow: none !important;

  border: 0 !important;
}


/* Individual tabs */

.stTabs [data-baseweb="tab"] {
  flex: 0 0 auto !important;

  min-height: 42px !important;

  height: auto !important;

  padding: 10px 20px !important;

  margin: 0 !important;

  border-radius: 14px !important;

  background: var(--surface) !important;

  color: var(--muted) !important;

  font-weight: 800 !important;

  box-shadow: var(--puffy) !important;

  transition:
    transform .15s ease,
    box-shadow .15s ease;
}


/* Tab hover */

.stTabs [data-baseweb="tab"]:hover {
  transform: translateY(-1px) !important;

  color: var(--accent) !important;
}


/* Active tab */

.stTabs [data-baseweb="tab"][aria-selected="true"] {
  color: var(--accent) !important;

  background: var(--surface) !important;

  box-shadow: var(--puffy) !important;
}


/* Tab text */

.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] span {
  margin: 0 !important;

  color: inherit !important;
}


/* Remove default BaseWeb underline */

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
  display: none !important;
}


/* =========================================================
   LIGHT ALERT / MESSAGE
   Example:
   "Please fill in both the GitHub URL and destination folder."
   
   LIGHT BACKGROUND = DARK TEXT
   ========================================================= */

[data-testid="stAlert"],
div[role="alert"],
.stAlert {
  border-radius: 20px;

  border: 0;

  box-shadow: var(--out);

  font-weight: 600;

  color: #17204A !important;
}


/* Force alert contents DARK */

[data-testid="stAlert"] *,
div[role="alert"] *,
.stAlert * {
  color: #17204A !important;

  -webkit-text-fill-color: #17204A !important;

  opacity: 1 !important;
}


/* =========================================================
   CODE
   ========================================================= */

[data-testid="stCode"] pre,
.stCodeBlock pre,
pre {
  background: var(--surface) !important;

  border-radius: 16px;

  box-shadow: var(--pressed);

  color: var(--ink);
}


/* =========================================================
   JSON
   ========================================================= */

[data-testid="stJson"] {
  background: var(--surface);

  border-radius: 16px;

  box-shadow: var(--pressed);

  padding: 8px;
}


/* =========================================================
   STATUS
   ========================================================= */

[data-testid="stStatus"],
[data-testid="stStatusWidget"] {
  border-radius: 22px;
}


/* =========================================================
   SCROLLBAR
   ========================================================= */

::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-thumb {
  background: var(--shadow-d);
  border-radius: 10px;
}


/* =========================================================
   BEFORE / AFTER DIFF
   ========================================================= */

.dv-stats {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin: 6px 0 12px;
}

.dv-chip {
  padding: 5px 14px;
  border-radius: 999px;

  font-size: 13px;
  font-weight: 800;

  background: var(--surface);

  box-shadow: var(--puffy);
}

.dv-chip.del {
  color: var(--bad);
  background: var(--bad-bg);
}

.dv-chip.add {
  color: var(--ok);
  background: var(--ok-bg);
}

.dv {
  border-radius: 22px;
  padding: 12px;

  background: var(--surface);

  box-shadow: var(--pressed);

  overflow-x: auto;
}

.dv-row {
  display: grid;

  grid-template-columns: 1fr 1fr;

  gap: 10px;

  margin-bottom: 3px;

  min-width: 520px;
}

.dv-head {
  margin-bottom: 10px;
}

.dv-h {
  font: 800 11.5px 'Nunito', sans-serif;

  letter-spacing: .05em;

  padding: 6px 14px;

  border-radius: 999px;

  width: fit-content;
}

.dv-h.before {
  background: var(--bad-bg);
  color: var(--bad);
}

.dv-h.after {
  background: var(--ok-bg);
  color: var(--ok);
}

.dv-cell {
  display: flex;

  gap: 8px;

  padding: 4px 10px;

  border-radius: 12px;

  min-height: 26px;

  font:
    13px/1.5
    ui-monospace,
    'Cascadia Code',
    Menlo,
    monospace;

  white-space: pre-wrap;

  word-break: break-word;
}

.dv-cell .ln {
  color: #9AA0BE;

  min-width: 24px;

  text-align: right;

  user-select: none;
}

.dv-cell .mk {
  width: 12px;

  font-weight: 800;
}

.dv-cell.same {
  color: #6E7598;
}

.dv-cell.del {
  background: var(--bad-bg);
  color: #6E1D2F;
}

.dv-cell.del .mk {
  color: #D9435C;
}

.dv-cell.add {
  background: var(--ok-bg);
  color: #0F4A35;
}

.dv-cell.add .mk {
  color: #23966E;
}

.dv-cell.empty {
  background:
    repeating-linear-gradient(
      135deg,
      transparent 0 6px,
      rgba(153,163,196,.16) 6px 12px
    );
}

.dv-cell mark {
  padding: 0 2px;

  border-radius: 5px;

  font-weight: 800;
}

.dv-cell.del mark {
  background: #FFAFBE;
  color: #5C1626;
}

.dv-cell.add mark {
  background: #9BE6C6;
  color: #0A3D2A;
}

.dv-gap {
  text-align: center;

  color: var(--muted);

  font-size: 12px;

  font-weight: 700;

  padding: 6px 0;
}

.dv-note {
  color: var(--muted);

  font-size: 12.5px;

  margin-top: 8px;

  font-weight: 600;
}


/* =========================================================
   COMPACT PLAN
   ========================================================= */

.pl {
  display: grid;

  gap: 12px;
}

.pl-step {
  display: flex;

  align-items: center;

  gap: 12px;

  padding: 10px 16px;

  border-radius: 18px;

  background: var(--surface);

  box-shadow: var(--puffy);
}

.pl-n {
  min-width: 30px;

  height: 30px;

  border-radius: 50%;

  display: grid;

  place-items: center;

  font-weight: 800;

  font-size: 13px;

  color: #fff;

  background:
    linear-gradient(
      145deg,
      var(--accent-hi),
      var(--accent)
    );
}

.pl-t {
  font-weight: 600;

  font-size: 14.5px;
}


/* =========================================================
   PLAN EXPANDED SECTION
   ========================================================= */

.rp-plan-expanded {
  margin-top: 18px;

  padding: 8px 0 4px;
}

.rp-plan-extra {
  display: flex;

  align-items: flex-start;

  gap: 14px;

  margin: 12px 0;

  padding: 14px 18px;

  border-radius: 18px;

  background: var(--surface);

  box-shadow: var(--out);

  line-height: 1.5;
}

.rp-plan-number {
  flex:
    0 0 32px;

  width: 32px;

  height: 32px;

  display: inline-flex;

  align-items: center;

  justify-content: center;

  border-radius: 50%;

  color: #fff !important;

  background:
    linear-gradient(
      145deg,
      var(--accent-hi),
      var(--accent)
    );

  box-shadow:
    3px 3px 8px rgba(108,99,255,.28),
    -2px -2px 6px var(--shadow-l);

  font-weight: 800;
}


/* =========================================================
   SHOW / HIDE PLAN BUTTON
   ========================================================= */

[data-testid="stButton"] {
  margin-top: 8px;
}

[data-testid="stButton"]:has(button[key="toggle_plan_steps"]) {
  margin-top: 22px !important;

  margin-bottom: 12px !important;
}

[data-testid="stButton"]:has(button[key="toggle_plan_steps"]) button {
  margin-top: 4px !important;

  border-radius: 16px !important;
}


/* =========================================================
   NORMAL MARKDOWN ON LIGHT BACKGROUND
   ========================================================= */

[data-testid="stMarkdownContainer"] {
  color: #17204A;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] strong {
  color: #17204A;
}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 720px) {

  .block-container {
    padding:
      1.2rem
      1rem
      2rem;

    border-radius: 26px;

    margin-top: .5rem;
  }

  .main-title {
    font-size: 32px;
  }

  .stTabs [data-baseweb="tab-list"] {
    gap: 10px !important;

    overflow-x: auto !important;

    padding: 6px !important;
  }

  .stTabs [data-baseweb="tab"] {
    padding:
      9px
      14px !important;

    white-space: nowrap !important;
  }
}
"""


def apply_theme():
    st.markdown(
        f"<style>{CSS}</style>",
        unsafe_allow_html=True
    )