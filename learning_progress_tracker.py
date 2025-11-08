import streamlit as st
import json
import os
from functools import partial

st.set_page_config(page_title="Learning Progress Tracker", layout="wide")
st.title("📘 Learning Progress Tracker")

SAVE_FILE = "progress_data.json"

# ---- Ensure roadmap available ----
if "selected_tasks" not in st.session_state or "selected_career" not in st.session_state:
    st.warning("⚠️ No roadmap data found. Generate a roadmap first in the main app.")
    st.stop()

career = st.session_state["selected_career"]
tasks = st.session_state["selected_tasks"]
level = st.session_state.get("selected_level", "Unknown")

st.subheader(f"🎯 Tracking: {career} ({level})")

# ---- Load saved progress for this career (if present) ----
saved_progress = {}
if os.path.exists(SAVE_FILE):
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            saved_progress = json.load(f)
    except Exception:
        saved_progress = {}

# Use saved progress for this career if it exists, else default to Not Started
initial_progress = saved_progress.get(career, {t: "Not Started" for t in tasks})

# Initialize session progress and ensure it contains exactly current tasks
if "progress" not in st.session_state:
    st.session_state.progress = initial_progress.copy()
else:
    # Add any new tasks (if roadmap changed)
    for t in tasks:
        if t not in st.session_state.progress:
            st.session_state.progress[t] = initial_progress.get(t, "Not Started")
    # Remove tasks that are no longer in roadmap (optional)
    keys_to_remove = [k for k in st.session_state.progress.keys() if k not in tasks]
    for k in keys_to_remove:
        del st.session_state.progress[k]

# ---- Helper callback to sync widget value -> progress and rerun ----
def _on_change_task_status(task_key, widget_key):
    """
    Called when a selectbox changes.
    Writes the widget's current value into st.session_state.progress and reruns.
    """
    # read widget value and set progress
    new_val = st.session_state.get(widget_key)
    if new_val is not None:
        st.session_state.progress[task_key] = new_val
    # rerun so dashboard updates immediately
    st.rerun()

# ---- Dashboard (computed from st.session_state.progress) ----
def compute_stats():
    total = len(tasks)
    completed = sum(1 for t in tasks if st.session_state.progress.get(t) == "Completed")
    in_progress = sum(1 for t in tasks if st.session_state.progress.get(t) == "In Progress")
    pending = total - completed - in_progress
    percent = (completed / total) * 100 if total else 0.0
    return total, completed, in_progress, pending, percent

total, completed, in_progress, pending, percent = compute_stats()

st.markdown("### 📊 Overall Progress")
st.progress(percent / 100)
st.info(f"✅ {completed}/{total} completed  |  🕓 {in_progress} in progress  |  ⏳ {pending} not started  ({percent:.1f}%)")
if total > 0 and completed == total:
    st.success("🎉 All tasks completed — great job!")

st.markdown("---")

# ---- Task list with per-widget callbacks ----
st.markdown("### 🧩 Tasks")
for i, task in enumerate(tasks):
    widget_key = f"task_widget__{i}"
    # initialize widget state so selectbox shows the saved progress
    if widget_key not in st.session_state:
        st.session_state[widget_key] = st.session_state.progress.get(task, "Not Started")

    # create a partial callback that captures the task key and widget key
    callback = partial(_on_change_task_status, task, widget_key)

    # render selectbox with on_change callback
    new_status = st.selectbox(
        label=f"{i+1}. {task}",
        options=["Not Started", "In Progress", "Completed"],
        index=["Not Started", "In Progress", "Completed"].index(st.session_state[widget_key]),
        key=widget_key,
        on_change=callback
    )
    # (No immediate assignment here — the callback will sync widget -> st.session_state.progress)

st.markdown("---")

# ---- Controls: Save, Reset, Refresh ----
st.markdown("### ⚙️ Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Save Progress"):
        # load existing data
        existing = {}
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                existing = {}
        existing[career] = st.session_state.progress
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=4)
        st.success("✅ Progress saved to disk (progress_data.json).")


with col3:
    if st.button("🔄 Refresh Dashboard"):
        st.rerun()
