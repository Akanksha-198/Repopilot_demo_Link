"""
Run once from the folder that contains app/ :   python patch_prompts.py
Makes RepoPilot's "Understanding" and "Plan" answers short (edits 2 prompts in app/agent_graph_ui.py).
A backup app/agent_graph_ui.py.bak is kept. Safe to run twice.
"""
import shutil
import sys
from pathlib import Path

p = Path("app/agent_graph_ui.py")
if not p.exists():
    sys.exit("app/agent_graph_ui.py not found. Run this from the folder that contains the app folder.")
raw = p.read_bytes().decode("utf-8")
if "FORMAT RULES (strict)" in raw:
    sys.exit("Already patched. Nothing to do.")

nl = "\r\n" if "\r\n" in raw else "\n"
src = raw.replace("\r\n", "\n")

rules = (
    "Do not propose code changes yet.\n\n"
    "FORMAT RULES (strict):\n"
    "- Answer in at most 4 short bullet points, under 80 words in total.\n"
    "- No headings, no tables, no 'Next Steps' section.\n"
    "- Do NOT ask the user any questions."
)
plan_old = "Create 3 to 7 steps."
plan_new = "Create 3 to 5 steps. Each step must be ONE short sentence (under 15 words)."

if src.count("Do not propose code changes yet.") != 1 or src.count(plan_old) != 1:
    sys.exit("Could not find the expected prompt lines (file may have been edited). Nothing changed.")

shutil.copy(p, "app/agent_graph_ui.py.bak")
src = src.replace("Do not propose code changes yet.", rules, 1).replace(plan_old, plan_new, 1)
p.write_bytes(src.replace("\n", nl).encode("utf-8"))
print("Patched OK. Backup saved as app/agent_graph_ui.py.bak")
