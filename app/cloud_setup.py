"""
Deployment helpers for Streamlit Community Cloud (also safe to run locally).
- copies st.secrets into environment variables (so app/model.py etc. keep working unchanged)
- makes the "npm.cmd" call in validator.py work on Linux
- sets a git identity + token helper so commit / push work without a terminal
- optional access-password gate so strangers cannot spend your Mistral / GitHub credits
"""
import hmac
import os
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

import streamlit as st

IS_CLOUD = Path("/mount/src").exists() or os.getenv("REPOPILOT_CLOUD") == "1"
DEFAULT_WORKSPACE = str(Path(tempfile.gettempdir()) / "repopilot_workspace")
_DONE = False


def _load_secrets():
    try:
        for key in st.secrets:
            value = st.secrets[key]
            if isinstance(value, (str, int, float, bool)) and key not in os.environ:
                os.environ[key] = str(value)
    except Exception:
        pass  # no secrets file (normal on your laptop)


def _npm_shim():
    npm = shutil.which("npm")
    if npm and not shutil.which("npm.cmd"):
        shim_dir = Path(tempfile.gettempdir()) / "rp_bin"
        shim_dir.mkdir(exist_ok=True)
        link = shim_dir / "npm.cmd"
        if not link.exists():
            link.symlink_to(npm)
        os.environ["PATH"] = str(shim_dir) + os.pathsep + os.environ.get("PATH", "")


def _git_identity():
    try:
        for key, default in (("user.name", "RepoPilot"), ("user.email", "repopilot@users.noreply.github.com")):
            current = subprocess.run(["git", "config", "--global", key], capture_output=True, text=True).stdout.strip()
            if not current:
                subprocess.run(["git", "config", "--global", key, default], check=False)
    except FileNotFoundError:
        pass


def _askpass():
    if not os.getenv("GITHUB_TOKEN"):
        return
    script = Path(tempfile.gettempdir()) / "rp_askpass.sh"
    script.write_text('#!/bin/sh\ncase "$1" in\n  Username*) echo "x-access-token" ;;\n  *) echo "$GITHUB_TOKEN" ;;\nesac\n')
    script.chmod(stat.S_IRWXU)
    os.environ["GIT_ASKPASS"] = str(script)
    os.environ["GIT_TERMINAL_PROMPT"] = "0"
    os.environ.setdefault("GH_TOKEN", os.environ["GITHUB_TOKEN"])


def bootstrap():
    global _DONE
    if _DONE:
        return
    _DONE = True
    _load_secrets()
    if IS_CLOUD:
        Path(DEFAULT_WORKSPACE).mkdir(parents=True, exist_ok=True)
        _git_identity()
        _askpass()
    if os.name != "nt":
        _npm_shim()


def require_password():
    """If APP_PASSWORD is set (secrets), nothing renders until it is entered."""
    expected = os.getenv("APP_PASSWORD", "")
    if not expected or st.session_state.get("rp_unlocked"):
        return
    st.markdown('<div class="main-title">RepoPilot</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Private demo. Enter the access password to continue.</div>', unsafe_allow_html=True)
    entered = st.text_input("Access password", type="password")
    if entered:
        if hmac.compare_digest(entered, expected):
            st.session_state.rp_unlocked = True
            st.rerun()
        st.error("Incorrect password.")
    st.stop()
