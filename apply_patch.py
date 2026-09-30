"""
Run once, next to streamlit_app.py:   python apply_patch.py
Makes 3 small edits (a backup streamlit_app.py.bak is kept):
  1. bootstrap() for deployment (secrets, npm shim, git identity)
  2. replaces the old <style> theme block with the glass theme + optional password gate
  3. on Streamlit Cloud, hides the "Local Clone Destination" box and uses a server folder
"""
import re
import shutil
import sys
from pathlib import Path

target = Path("streamlit_app.py")
if not target.exists():
    sys.exit("streamlit_app.py not found. Run this script from the folder that contains it.")
src = target.read_text(encoding="utf-8")
if "apply_theme()" in src:
    sys.exit("Already patched. Nothing to do.")

shutil.copy(target, "streamlit_app.py.bak")

# 1. bootstrap right after the first two imports
head = "import streamlit as st\nfrom pathlib import Path\n"
if head not in src.replace("\r\n", "\n")[:200]:
    sys.exit("Unexpected file header. Expected 'import streamlit as st' then 'from pathlib import Path'.")
src = src.replace("\r\n", "\n")
src = src.replace(
    head,
    head + "\nfrom app.cloud_setup import bootstrap, require_password, IS_CLOUD, DEFAULT_WORKSPACE\n"
           "from app.glass_theme import apply_theme\n\nbootstrap()\n", 1)

# 2. theme block -> glass theme + password gate
theme = re.compile(r'st\.markdown\(\s*"""\s*<style>.*?</style>\s*""",\s*unsafe_allow_html=True\s*\)', re.S)
if not theme.search(src):
    sys.exit("Could not find the old <style> theme block.")
src = theme.sub("apply_theme()\nrequire_password()", src, count=1)

# 3. clone destination
dest = re.compile(r'(?P<i>[ \t]*)clone_destination = st\.text_input\(\s*"Local Clone Destination",\s*placeholder=r"[^"]*"\s*\)')
m = dest.search(src)
if not m:
    sys.exit("Could not find the 'Local Clone Destination' input.")
i = m.group("i")
replacement = (
    f'{i}if IS_CLOUD:\n'
    f'{i}    clone_destination = DEFAULT_WORKSPACE\n'
    f'{i}    st.text_input("Workspace", value="Managed by RepoPilot", disabled=True)\n'
    f'{i}else:\n'
    f'{i}    clone_destination = st.text_input(\n'
    f'{i}        "Local Clone Destination",\n'
    f'{i}        placeholder=r"C:\\...\\RepoPilot\\workspace"\n'
    f'{i}    )'
)
src = dest.sub(lambda _: replacement, src, count=1)

target.write_text(src, encoding="utf-8")
print("Patched OK. Backup saved as streamlit_app.py.bak")
