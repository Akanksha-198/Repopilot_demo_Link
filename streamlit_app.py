import streamlit as st
from pathlib import Path

from app.cloud_setup import bootstrap, require_password, IS_CLOUD, DEFAULT_WORKSPACE
from app.clay_theme import apply_theme
from app.diff_view import render_diff, short_text, plan_html

bootstrap()

from app.github_Tool import (
    clone_repository,
    repository_name as repo_name_from_url
)

from app.scanner import scan_repository

from app.agent_graph_ui import (
    build_ui_agent_graph,
    build_apply_graph,
    create_repair_diff,
    build_repair_apply_graph,
    ingest_repository_files
)

from app.git_tools import (
    get_git_status,
    create_feature_branch,
    get_git_diff,
    commit_changes,
    get_last_commit_info,
    push_branch,
    undo_last_commit,
    revert_last_commit,
    ignore_backup_files
)

from app.github_api import create_pull_request

MAX_REPAIR_ATTEMPTS = 3

# ============================================================
# PAGE CONFIG + THEME
# ============================================================

st.set_page_config(
    page_title="RepoPilot",
    page_icon="🤖",
    layout="wide"
)

apply_theme()
require_password()


# ============================================================
# SESSION STATE
# ============================================================

for key, default in {
    "repository_path": None,
    "repository_name": None,
    "scan_result": None,
    "review_result": None,
    "apply_result": None,
    "repair_result": None,
    "repair_apply_result": None,
    "git_action_message": None,
    "repair_attempt_count": 0,
}.items():

    if key not in st.session_state:
        st.session_state[key] = default


def reset_task_state():
    """Clear everything from the task/review stage onward, keep the repo loaded."""

    st.session_state.review_result = None
    st.session_state.apply_result = None
    st.session_state.repair_result = None
    st.session_state.repair_apply_result = None
    st.session_state.repair_attempt_count = 0
    st.session_state.plan_steps_expanded = False


def reset_repo_state():
    """Fully reset — load a different repository."""

    st.session_state.repository_path = None
    st.session_state.repository_name = None
    st.session_state.scan_result = None
    reset_task_state()


# ============================================================
# ACTION FEEDBACK
#
# Every git action shows a live progress box while it runs, and
# afterwards a message that survives st.rerun() (stored in
# session_state) and is shown at the TOP of the page + as a toast,
# so it is never hidden inside a collapsed expander.
# ============================================================

def flash(level, text):
    st.session_state.git_action_message = (level, text)


def show_flash():
    message = st.session_state.git_action_message
    if not message:
        return
    level, text = message
    st.toast(text, icon="✅" if level == "success" else "⚠️")
    if level == "success":
        st.success(text)
    else:
        st.error(text)
    st.session_state.git_action_message = None


def run_action(title, steps, fn, ok_label, fail_label):
    """Run a blocking action inside a progress box. fn() must return a dict with 'success'."""

    with st.status(title, expanded=True) as action_status:
        for step in steps:
            st.write(step)
        result = fn()
        ok = bool(result.get("success", False))
        action_status.update(
            label=ok_label if ok else fail_label,
            state="complete" if ok else "error"
        )
    return result


def do_push():
    repo = st.session_state.repository_path
    result = run_action(
        "🚀 Pushing to GitHub…",
        ["🔐 Authenticating with GitHub…", "📤 Uploading your commits…", "🌿 Updating the remote branch…"],
        lambda: push_branch(repo),
        "✅ Pushed to GitHub",
        "❌ Push failed"
    )
    ok = result.get("success", False)
    flash("success" if ok else "error", ("🚀 Pushed to GitHub. " if ok else "") + str(result.get("message", "")))
    st.rerun()


def do_undo():
    repo = st.session_state.repository_path
    result = run_action(
        "↩️ Undoing the last commit…",
        ["📝 Moving the branch back one commit…", "📂 Keeping your file changes safe…"],
        lambda: undo_last_commit(repo),
        "✅ Commit undone",
        "❌ Undo failed"
    )
    flash("success" if result.get("success") else "error", str(result.get("message", "")))
    st.rerun()


def do_revert():
    repo = st.session_state.repository_path
    result = run_action(
        "⏪ Reverting the last commit…",
        ["🧮 Creating a new commit that reverses the last one…"],
        lambda: revert_last_commit(repo),
        "✅ Revert commit created",
        "❌ Revert failed"
    )
    message = str(result.get("message", ""))
    if result.get("success"):
        message += f" (commit `{result.get('commit_hash', '')}`)"
    flash("success" if result.get("success") else "error", message)
    st.rerun()


def do_ignore_backups():
    repo = st.session_state.repository_path
    result = run_action(
        "🧹 Cleaning up backup files…",
        ["🔎 Finding tracked backup files…", "🚫 Removing them from git tracking…"],
        lambda: ignore_backup_files(repo),
        "✅ Backup files are no longer tracked",
        "❌ Cleanup failed"
    )
    flash("success" if result.get("success") else "error", str(result.get("message", "")))
    st.rerun()


def do_pull_request(title, body):
    repo = st.session_state.repository_path
    result = run_action(
        "🔀 Opening the pull request…",
        ["🔐 Contacting GitHub…", "📝 Creating the pull request…"],
        lambda: create_pull_request(repo, title, body),
        "✅ Pull request is ready",
        "❌ Pull request failed"
    )
    if result.get("success"):
        note = "Pull request already existed" if result.get("already_existed") else str(result.get("message", "Pull request created"))
        flash("success", f"{note} → {result.get('url', '')}")
    else:
        flash("error", str(result.get("message", "Pull request failed.")))
    st.rerun()


def do_commit(files, message):
    repo = st.session_state.repository_path
    result = run_action(
        "📝 Committing your change…",
        ["📂 Staging only the changed file…", "🧾 Writing the commit…"],
        lambda: commit_changes(repo, files, message),
        "✅ Change committed",
        "❌ Commit failed"
    )
    if result.get("success"):
        flash("success", f"{result.get('message', 'Committed.')} (commit `{result.get('commit_hash', '')}`)")
    else:
        flash("error", f"Commit failed: {result.get('message', '')}")
    st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown('<div class="main-title"><span class="rp-bot-icon">🤖</span> RepoPilot</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-powered repository maintenance & repair agent</div>',
    unsafe_allow_html=True
)


# ============================================================
# STEP INDICATOR
# ============================================================

repo_loaded = st.session_state.repository_path is not None
task_reviewed = st.session_state.review_result is not None
change_applied = st.session_state.apply_result is not None

def step_class(done, active):
    if done:
        return "rp-step rp-step-done"
    if active:
        return "rp-step rp-step-active"
    return "rp-step"

steps_html = f"""
<div class="rp-steps">
  <span class="{step_class(repo_loaded, not repo_loaded)}">1 · Repository</span>
  <span class="{step_class(task_reviewed, repo_loaded and not task_reviewed)}">2 · Task</span>
  <span class="{step_class(change_applied, task_reviewed and not change_applied)}">3 · Review &amp; Apply</span>
  <span class="{step_class(change_applied, False)}">4 · Result</span>
</div>
"""

st.markdown(steps_html, unsafe_allow_html=True)

show_flash()


# ============================================================
# STEP 1 — REPOSITORY
# ============================================================

if not repo_loaded:

    st.markdown('<div class="rp-card-title">📦 Load a Repository</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        github_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/username/repo.git"
        )

    with col2:
        if IS_CLOUD:
            clone_destination = DEFAULT_WORKSPACE
            st.text_input("Workspace", value="Managed by RepoPilot", disabled=True)
        else:
            clone_destination = st.text_input(
                "Local Clone Destination",
                placeholder=r"C:\...\RepoPilot\workspace"
            )

    if st.button("📥 Clone, Scan & Index Repository", type="primary", use_container_width=True):

        if not github_url or not clone_destination:
            st.warning("Please fill in both the GitHub URL and the destination folder.")
            st.stop()

        try:
            with st.status("🤖 Preparing the repository...", expanded=True) as status:

                st.write("🌐 Cloning from GitHub...")
                repo_path = clone_repository(github_url, Path(clone_destination))

                repo_name = repo_name_from_url(github_url)

                st.write("🗂️ Scanning repository structure...")
                scan_result = scan_repository(repo_path)

                st.write("🧠 Chunking & embedding source files...")
                chunk_count = ingest_repository_files(str(repo_path), repo_name)

                status.update(label=f"✅ Ready — indexed {chunk_count} code chunks.", state="complete")

            st.session_state.repository_path = str(repo_path)
            st.session_state.repository_name = repo_name
            st.session_state.scan_result = scan_result
            reset_task_state()
            st.rerun()

        except Exception as error:
            st.error(f"Could not prepare the repository:\n\n{error}")

    st.stop()


# ------------------------------------------------------------
# Repo already loaded — compact status bar + collapsible overview
# ------------------------------------------------------------

scan = st.session_state.scan_result or {}

repo_bar_col1, repo_bar_col2 = st.columns([5, 1])

with repo_bar_col1:
    st.markdown(
        f"""
        <div class="rp-repo-bar">
            <div>
                <div class="rp-repo-name">📁 {st.session_state.repository_name}</div>
                <div class="rp-repo-path">{st.session_state.repository_path}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with repo_bar_col2:
    if st.button("🔁 Change Repo", use_container_width=True):
        reset_repo_state()
        st.rerun()

with st.expander(f"🗂️ {scan.get('file_count', 0)} files · click to view languages & re-index"):

    languages = scan.get("languages", {})

    if languages:
        badges = "".join(
            f'<span class="rp-badge">{lang} · {count}</span>'
            for lang, count in languages.items()
        )
        st.markdown(badges, unsafe_allow_html=True)

    important_files = scan.get("important_files", [])
    if important_files:
        st.caption("Important files: " + ", ".join(f"`{f}`" for f in important_files))

    if st.button("🔄 Re-index (after manual edits)"):
        try:
            with st.spinner("Re-indexing..."):
                chunk_count = ingest_repository_files(
                    st.session_state.repository_path,
                    st.session_state.repository_name
                )
                st.session_state.scan_result = scan_repository(
                    Path(st.session_state.repository_path)
                )
            st.success(f"Re-indexed {chunk_count} chunks.")
            st.rerun()
        except Exception as error:
            st.error(f"Re-indexing failed:\n\n{error}")


# ------------------------------------------------------------
# PHASE 6A — GIT STATUS
# ------------------------------------------------------------

git_status = get_git_status(st.session_state.repository_path)

with st.expander(
    f"🌿 Git: {git_status['branch'] or 'unknown branch'}"
    + (" · clean" if git_status["clean"] else " · uncommitted changes")
):

    if git_status["error"]:

        st.warning(git_status["error"])

    else:

        st.write(f"**Branch:** `{git_status['branch']}`")

        if git_status["clean"]:

            st.success("Working tree clean — no staged, modified, or untracked files.")

        else:

            if git_status["staged"]:
                st.write("**Staged:**")
                for f in git_status["staged"]:
                    st.write(f"- `{f}`")

            if git_status["modified"]:
                st.write("**Modified (unstaged):**")
                for f in git_status["modified"]:
                    st.write(f"- `{f}`")

            if git_status["untracked"]:
                st.write("**Untracked:**")
                for f in git_status["untracked"]:
                    st.write(f"- `{f}`")

        if st.button("📋 View Git Diff", key="view_git_diff_btn"):

            diff_result = get_git_diff(st.session_state.repository_path)

            if diff_result["error"]:
                st.warning(diff_result["error"])
            elif not diff_result["diff"]:
                st.info("No unstaged changes — working tree matches HEAD.")
            else:
                st.code(diff_result["diff"], language="diff")

        commit_info = get_last_commit_info(st.session_state.repository_path)

        if commit_info["has_commit"] and commit_info["branch"] not in ("main", "master", ""):

            st.divider()
            st.write(f"**Last commit:** `{commit_info['hash']}` — {commit_info['message']}")
            st.write(f"**Pushed to GitHub:** {'✅ Yes' if commit_info['pushed'] else '⏳ Not yet'}")

            if not commit_info["pushed"]:

                col_push, col_undo = st.columns(2)

                with col_push:
                    if st.button("🚀 Push to GitHub", type="primary", use_container_width=True, key="push_btn"):
                        do_push()

                with col_undo:
                    if st.button("↩️ Undo Last Commit", use_container_width=True, key="undo_btn"):
                        do_undo()

            else:

                st.caption("This commit is already on GitHub — undo is disabled to avoid rewriting shared history. Use Revert instead.")

                if st.button("⏪ Revert Last Commit (safe — adds a new commit)", use_container_width=True, key="revert_btn"):
                    do_revert()

                st.divider()
                st.write("**Open a Pull Request**")

                default_pr_title = commit_info["message"]

                pr_title = st.text_input(
                    "PR title",
                    value=default_pr_title,
                    key="pr_title_input"
                )

                default_pr_body = (
                    f"Automated change by RepoPilot.\n\n"
                    f"**Branch:** `{commit_info['branch']}`\n"
                    f"**Last commit:** `{commit_info['hash']}` — {commit_info['message']}\n\n"
                    f"Please review the diff before merging."
                )

                pr_body = st.text_area(
                    "PR description",
                    value=default_pr_body,
                    key="pr_body_input"
                )

                if st.button("🔀 Create Pull Request", type="primary", use_container_width=True, key="create_pr_btn"):
                    do_pull_request(pr_title, pr_body)

        st.divider()

        if st.button("🧹 Stop Tracking Backup Files", use_container_width=True, key="ignore_backups_btn"):
            do_ignore_backups()


# ============================================================
# STEP 2 — ENGINEERING TASK
# ============================================================

st.markdown('<div class="rp-card-title">🛠️ What do you want RepoPilot to do?</div>', unsafe_allow_html=True)

user_request = st.text_area(
    "Task",
    placeholder="Example: Check index.js and remove the error.",
    height=100,
    label_visibility="collapsed"
)

analyze_clicked = st.button("🚀 Analyze & Prepare Change", type="primary", use_container_width=True)

if analyze_clicked:

    if not user_request:
        st.warning("Please describe the engineering task.")
        st.stop()

    try:
        with st.status("🤖 Analyzing the repository...", expanded=True) as status:

            st.write("🧠 Understanding the task...")
            st.write("🔎 Retrieving relevant code...")
            st.write("📊 Analyzing repository...")
            st.write("📝 Creating implementation plan...")
            st.write("💻 Generating proposed code change...")
            st.write("📋 Generating diff...")

            graph = build_ui_agent_graph()

            initial_state = {
                "user_request": user_request,
                "repository_name": st.session_state.repository_name,
                "repository_path": st.session_state.repository_path
            }

            result = graph.invoke(initial_state)

            status.update(label="✅ Analysis complete.", state="complete")

        st.session_state.review_result = result
        reset_task_state()
        st.session_state.review_result = result
        st.rerun()

    except Exception as error:
        st.error(f"RepoPilot encountered an error:\n\n{error}")


# ============================================================
# STEP 3 — REVIEW & APPLY
# ============================================================

result = st.session_state.review_result

if result:

    st.markdown('<div class="rp-card-title">🔎 Review Proposed Change</div>', unsafe_allow_html=True)

    tab_understanding, tab_plan, tab_diff = st.tabs(
        ["🧠 Summary", "📝 Plan", "🔍 What changes"]
    )

    with tab_understanding:
        summary_text, summary_cut = short_text(result.get("task_understanding", ""), 420)
        st.markdown(summary_text or "No task understanding generated.")
        if summary_cut:
            with st.expander("Show full explanation"):
                st.write(result.get("task_understanding", ""))

    with tab_plan:
        plan = result.get("plan", [])
        if plan:
            st.markdown(plan_html(plan), unsafe_allow_html=True)

            if len(plan) > 5:
                # Use an explicit toggle instead of st.expander so the control
                # clearly changes from SHOW -> HIDE when the steps are open.
                if "plan_steps_expanded" not in st.session_state:
                    st.session_state.plan_steps_expanded = False

                toggle_label = (
                    f"🙈 Hide all {len(plan)} steps"
                    if st.session_state.plan_steps_expanded
                    else f"👁️ Show all {len(plan)} steps"
                )

                if st.button(
                    toggle_label,
                    key="toggle_plan_steps",
                    use_container_width=False,
                ):
                    st.session_state.plan_steps_expanded = not st.session_state.plan_steps_expanded
                    st.rerun()

                if st.session_state.plan_steps_expanded:
                    st.markdown('<div class="rp-plan-expanded">', unsafe_allow_html=True)
                    for index, step in enumerate(plan, start=1):
                        st.markdown(
                            f'<div class="rp-plan-extra"><span class="rp-plan-number">{index}</span><span>{step}</span></div>',
                            unsafe_allow_html=True,
                        )
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.caption("No implementation plan was generated.")

    with tab_diff:
        changes = result.get("proposed_changes", [])
        change = changes[0] if changes else {}

        if change:
            st.write(f"**File:** `{change.get('file_path', '')}`")
            if change.get("reason"):
                st.write(f"**Why:** {change['reason']}")

        diff = result.get("diff", "")
        if diff:
            st.markdown(
                render_diff(change.get("old_content", ""), change.get("new_content", "")),
                unsafe_allow_html=True
            )
            with st.expander("Show raw diff (advanced)"):
                st.code(diff, language="diff")
        else:
            change_result = result.get("change_result", {})
            if change_result.get("status") == "no_change_needed":
                st.info(
                    change_result.get(
                        "message",
                        "RepoPilot determined no change is needed for this request."
                    )
                )
            else:
                st.error(change_result.get("message", "No diff was generated."))

    diff = result.get("diff", "")

    if diff:

        col1, col2 = st.columns(2)

        with col1:
            approve_clicked = st.button("✅ Approve & Apply", type="primary", use_container_width=True)

        with col2:
            reject_clicked = st.button("❌ Reject", use_container_width=True)

        if reject_clicked:
            st.session_state.review_result = None
            flash("success", "Change rejected. No file was modified.")
            st.rerun()

        if approve_clicked:

            try:
                # PHASE 6B — never apply directly on main/master.
                branch_result = create_feature_branch(
                    st.session_state.repository_path,
                    user_request=result.get("user_request", "")
                )

                if not branch_result["success"]:
                    st.error(
                        "Could not prepare a safe branch to apply "
                        f"this change on:\n\n{branch_result['error']}"
                    )
                    st.stop()

                approved_state = dict(result)
                approved_state["change_approved"] = True

                with st.status("Applying approved change...", expanded=True) as status:

                    if branch_result["created_new"]:
                        st.write(f"🌿 Created feature branch `{branch_result['branch']}`...")
                    else:
                        st.write(f"🌿 Using existing branch `{branch_result['branch']}`...")

                    st.write("💾 Creating backup...")
                    st.write("✏️ Applying change...")
                    st.write("🧪 Running validation...")

                    apply_graph = build_apply_graph()
                    apply_result = apply_graph.invoke(approved_state)

                    status.update(label="✅ Change applied.", state="complete")

                apply_result["applied_on_branch"] = branch_result["branch"]

                st.session_state.repair_result = None
                st.session_state.repair_apply_result = None

                # Keep embeddings in sync with the file that was just changed
                if apply_result.get("change_result", {}).get("status") == "modified":
                    ingest_repository_files(
                        st.session_state.repository_path,
                        st.session_state.repository_name
                    )

                st.session_state.apply_result = apply_result
                st.rerun()

            except Exception as error:
                st.session_state.apply_result = None
                st.error(f"Change could not be applied:\n\n{error}")


# ============================================================
# STEP 4 — RESULT
# ============================================================

apply_result = st.session_state.apply_result

if apply_result:

    change_result = apply_result.get("change_result", {})
    validation_result = apply_result.get("validation_result", {})
    status = change_result.get("status", "unknown")
    validation_passed = validation_result.get("success", False)

    if status == "modified" and validation_passed:
        banner_class = "rp-result-ok"
        banner_title = "✅ Task Complete"
    elif status == "modified":
        banner_class = "rp-result-warn"
        banner_title = "⚠️ Change Applied — Validation Failed"
    else:
        banner_class = "rp-result-bad"
        banner_title = "❌ Change Not Applied"

    applied_on_branch = apply_result.get("applied_on_branch", "")

    st.markdown(
        f"""
        <div class="rp-result-banner {banner_class}">
            <div class="rp-result-title">{banner_title}</div>
            <div class="rp-result-row">📄 File: <code>{change_result.get('file_path', 'N/A')}</code></div>
            <div class="rp-result-row">💾 Backup: <code>{change_result.get('backup_path', 'N/A')}</code></div>
            <div class="rp-result-row">🧪 Validation: {"Passed" if validation_passed else "Failed / unavailable"}</div>
            {f'<div class="rp-result-row">🌿 Branch: <code>{applied_on_branch}</code></div>' if applied_on_branch else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

    if not validation_passed and status == "modified":
        with st.expander("View validation details"):
            st.json(validation_result)

    # PHASE 6D — COMMIT (only after a validated, modified change)

    if status == "modified" and validation_passed:

        committed_file = change_result.get("file_path", "")

        file_diff_check = get_git_diff(st.session_state.repository_path, file_path=committed_file)
        file_already_committed = (not file_diff_check["error"]) and (file_diff_check["diff"] == "")

        if file_already_committed:

            commit_info = get_last_commit_info(st.session_state.repository_path)

            st.markdown('<div class="rp-card-title">✅ Committed</div>', unsafe_allow_html=True)
            st.write(f"**Commit:** `{commit_info['hash']}` — {commit_info['message']}")

            if commit_info["pushed"]:
                st.success("✅ Already pushed to GitHub.")
            else:
                if st.button("🚀 Push to GitHub", type="primary", use_container_width=True, key="apply_inline_push_btn"):
                    do_push()

        else:

            st.markdown('<div class="rp-card-title">📝 Commit This Change</div>', unsafe_allow_html=True)

            task_desc = apply_result.get("user_request", "").strip()

            default_commit_message = (
                f"RepoPilot: {task_desc} ({committed_file})"
                if task_desc else
                f"RepoPilot: update {committed_file}"
            )

            commit_message = st.text_input(
                "Commit message",
                value=default_commit_message,
                key="apply_commit_message"
            )

            st.caption(f"Will commit only: `{committed_file}` (backup file is never committed)")

            if st.button("📝 Commit This Change", type="primary", use_container_width=True, key="commit_apply_btn"):
                do_commit([committed_file], commit_message)

    if validation_passed:
        if st.button("🔁 Start New Task", use_container_width=True):
            reset_task_state()
            st.rerun()

    # ========================================================
    # REPAIR FLOW
    # ========================================================

    if not validation_passed and status == "modified":

        st.markdown('<div class="rp-card-title">🛠️ AI Repair Assistant</div>', unsafe_allow_html=True)
        st.write("The applied change did not pass validation. RepoPilot can analyze the failure and prepare a repair for your review.")

        repair_clicked = st.button("🔍 Analyze Failure & Prepare Repair", type="primary", use_container_width=True)

        if repair_clicked:
            try:
                repair_state = dict(apply_result)

                with st.status("🤖 Analyzing the validation failure...", expanded=True) as status:
                    st.write("🔎 Reading validation output...")
                    st.write("🧠 Analyzing with Mistral...")
                    st.write("📋 Generating repair diff...")

                    repair_output = create_repair_diff(repair_state)

                    status.update(label="✅ Repair proposal ready.", state="complete")

                st.session_state.repair_result = repair_output
                st.session_state.repair_apply_result = None
                st.rerun()

            except Exception as error:
                st.error(f"Repair analysis failed:\n\n{error}")


# ============================================================
# REPAIR REVIEW
# ============================================================

repair_result = st.session_state.repair_result

if repair_result:

    repair_status = repair_result.get("repair_result", {}).get("status", "unknown")

    if repair_status == "ready_for_review":

        st.markdown('<div class="rp-card-title">🔧 Proposed Repair</div>', unsafe_allow_html=True)

        tab_analysis, tab_repair_diff = st.tabs(["🔎 What went wrong", "🔍 What changes"])

        with tab_analysis:
            analysis_text, analysis_cut = short_text(repair_result.get("failure_analysis", ""), 520)
            st.markdown(analysis_text)
            if analysis_cut:
                with st.expander("Show full analysis"):
                    st.write(repair_result.get("failure_analysis", ""))

        with tab_repair_diff:
            repair_proposal = repair_result.get("repair_proposal", {})
            if repair_proposal:
                st.write(f"**File:** `{repair_proposal.get('file_path', 'N/A')}`")
                st.write(f"**Why:** {repair_proposal.get('reason', 'No reason provided.')}")

            repair_diff = repair_result.get("repair_diff", "")
            if repair_diff:
                st.markdown(
                    render_diff(repair_proposal.get("old_content", ""), repair_proposal.get("new_content", "")),
                    unsafe_allow_html=True
                )
                with st.expander("Show raw diff (advanced)"):
                    st.code(repair_diff, language="diff")

        col1, col2 = st.columns(2)

        with col1:
            approve_repair = st.button("✅ Approve Repair", type="primary", use_container_width=True)

        with col2:
            reject_repair = st.button("❌ Reject Repair", use_container_width=True)

        if reject_repair:
            st.session_state.repair_result = None
            st.session_state.repair_apply_result = None
            flash("success", "Repair rejected. No additional file modification was made.")
            st.rerun()

        if approve_repair:

            try:
                # PHASE 6B — same branch safety as the normal apply flow.
                branch_result = create_feature_branch(
                    st.session_state.repository_path,
                    user_request=st.session_state.apply_result.get("user_request", "")
                )

                if not branch_result["success"]:
                    st.error(
                        "Could not prepare a safe branch to apply "
                        f"this repair on:\n\n{branch_result['error']}"
                    )
                    st.stop()

                repair_apply_state = dict(st.session_state.apply_result)
                repair_apply_state.update(repair_result)
                repair_apply_state["repair_approved"] = True

                with st.status("Applying approved repair...", expanded=True) as status:

                    if branch_result["created_new"]:
                        st.write(f"🌿 Created feature branch `{branch_result['branch']}`...")
                    else:
                        st.write(f"🌿 Using existing branch `{branch_result['branch']}`...")

                    st.write("💾 Creating backup...")
                    st.write("🛠️ Applying repair...")
                    st.write("🧪 Re-validating repository...")

                    repair_apply_graph = build_repair_apply_graph()
                    repair_apply_result = repair_apply_graph.invoke(repair_apply_state)

                    status.update(label="✅ Repair applied.", state="complete")

                repair_apply_result["applied_on_branch"] = branch_result["branch"]

                # PHASE 5F — this is repair attempt #1 for this task,
                # unless a retry already bumped the counter earlier.
                if st.session_state.repair_attempt_count == 0:
                    st.session_state.repair_attempt_count = 1

                st.session_state.repair_apply_result = repair_apply_result
                st.rerun()

            except Exception as error:
                st.error(f"Repair could not be applied:\n\n{error}")

    elif repair_status != "not_needed":
        message = repair_result.get("repair_result", {}).get("message", "Repair could not be prepared.")
        st.error(message)


# ============================================================
# REPAIR RESULT
# ============================================================

repair_apply_result = st.session_state.repair_apply_result

if repair_apply_result:

    repair_apply_status = repair_apply_result.get("repair_result", {})
    status = repair_apply_status.get("status", "unknown")

    new_validation_result = repair_apply_result.get("validation_result", {})
    new_validation_passed = new_validation_result.get("success", False)

    if status == "modified" and new_validation_passed:
        banner_class = "rp-result-ok"
        banner_title = "✅ Repair Applied — Validation Passed"
    elif status == "modified":
        banner_class = "rp-result-warn"
        banner_title = "⚠️ Repair Applied — Still Failing"
    else:
        banner_class = "rp-result-bad"
        banner_title = "❌ Repair Not Applied"

    repair_applied_on_branch = repair_apply_result.get("applied_on_branch", "")

    st.markdown(
        f"""
        <div class="rp-result-banner {banner_class}">
            <div class="rp-result-title">{banner_title}</div>
            <div class="rp-result-row">📄 File: <code>{repair_apply_status.get('file_path', 'N/A')}</code></div>
            <div class="rp-result-row">💾 Backup: <code>{repair_apply_status.get('backup_path', 'N/A')}</code></div>
            <div class="rp-result-row">🧪 New validation: {"Passed" if new_validation_passed else "Still failing"}</div>
            {f'<div class="rp-result-row">🌿 Branch: <code>{repair_applied_on_branch}</code></div>' if repair_applied_on_branch else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

    if not new_validation_passed:
        with st.expander("View new validation details"):
            st.json(new_validation_result)

    # PHASE 5F — Controlled repair loop (max MAX_REPAIR_ATTEMPTS, never unbounded)

    if status == "modified" and not new_validation_passed:

        attempts_used = st.session_state.repair_attempt_count

        if attempts_used < MAX_REPAIR_ATTEMPTS:

            st.warning(
                f"Repair attempt {attempts_used} of {MAX_REPAIR_ATTEMPTS} "
                f"did not resolve the validation failure."
            )

            if st.button("🔁 Try Repair Again", type="primary", use_container_width=True, key="retry_repair_btn"):

                try:
                    retry_state = dict(repair_apply_result)

                    with st.status("🤖 Analyzing the new validation failure...", expanded=True) as retry_status:
                        st.write("🔎 Reading validation output...")
                        st.write("🧠 Analyzing with Mistral...")
                        st.write("📋 Generating repair diff...")

                        retry_repair_output = create_repair_diff(retry_state)

                        retry_status.update(label="✅ Repair proposal ready.", state="complete")

                    st.session_state.repair_attempt_count = attempts_used + 1
                    st.session_state.repair_result = retry_repair_output
                    st.session_state.repair_apply_result = None
                    st.rerun()

                except Exception as error:
                    st.error(f"Repair analysis failed:\n\n{error}")

        else:

            st.error(
                f"🛑 Maximum repair attempts ({MAX_REPAIR_ATTEMPTS}) reached. "
                f"RepoPilot will not attempt further automatic repairs on "
                f"this task. Manual review is needed -- check the validation "
                f"details above, or start a new task with a more specific "
                f"description of the problem."
            )

    # PHASE 6D — COMMIT (only after a validated, modified repair)

    if status == "modified" and new_validation_passed:

        committed_file = repair_apply_status.get("file_path", "")

        file_diff_check = get_git_diff(st.session_state.repository_path, file_path=committed_file)
        file_already_committed = (not file_diff_check["error"]) and (file_diff_check["diff"] == "")

        if file_already_committed:

            commit_info = get_last_commit_info(st.session_state.repository_path)

            st.markdown('<div class="rp-card-title">✅ Committed</div>', unsafe_allow_html=True)
            st.write(f"**Commit:** `{commit_info['hash']}` — {commit_info['message']}")

            if commit_info["pushed"]:
                st.success("✅ Already pushed to GitHub.")
            else:
                if st.button("🚀 Push to GitHub", type="primary", use_container_width=True, key="repair_inline_push_btn"):
                    do_push()

        else:

            st.markdown('<div class="rp-card-title">📝 Commit This Repair</div>', unsafe_allow_html=True)

            repair_reason = repair_result.get("repair_proposal", {}).get("reason", "").strip() if repair_result else ""

            default_repair_commit_message = (
                f"RepoPilot repair: {repair_reason[:100]} ({committed_file})"
                if repair_reason else
                f"RepoPilot repair: fix {committed_file}"
            )

            repair_commit_message = st.text_input(
                "Commit message",
                value=default_repair_commit_message,
                key="repair_commit_message"
            )

            st.caption(f"Will commit only: `{committed_file}` (backup file is never committed)")

            if st.button("📝 Commit This Repair", type="primary", use_container_width=True, key="commit_repair_btn"):
                do_commit([committed_file], repair_commit_message)

    if st.button("🔁 Start New Task ", use_container_width=True, key="start_new_after_repair"):
        reset_task_state()
        st.rerun()
