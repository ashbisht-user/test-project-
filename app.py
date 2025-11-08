import streamlit as st
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ---- PAGE CONFIG ----
st.set_page_config(page_title="AI Career Roadmap Generator", page_icon="🚀", layout="wide")

# ---- LOAD DATA ----
with open("Untitled (2).json", "r", encoding="utf-8") as f:
    careers = json.load(f)

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

st.title("🚀 AI Career Roadmap Generator")
st.markdown("Enter your **skills** and **interests** to discover your ideal career path and personalized roadmap.")

# ---- USER INPUT ----
user_skills_input = st.text_input("🧠 Enter your skills (comma-separated):", "")
user_interests_input = st.text_input("💡 Enter your interests (comma-separated):", "")

# ---- GENERATE CAREER MATCHES ----
if st.button("🎯 Generate Career Matches"):
    user_skills = [s.strip().lower() for s in user_skills_input.split(",") if s.strip()]
    user_interests = [i.strip().lower() for i in user_interests_input.split(",") if i.strip()]

    career_texts = [" ".join(c["required_skills"] + c["interest_tags"]) for c in careers]
    career_vectors = model.encode(career_texts, normalize_embeddings=True)
    user_vector = model.encode([" ".join(user_skills + user_interests)], normalize_embeddings=True)

    similarities = cosine_similarity(user_vector, career_vectors)[0]
    top_indices = np.argsort(similarities)[::-1][:3]
    recommendations = [careers[i] for i in top_indices]
    st.session_state["recommendations"] = recommendations

# ---- SHOW RECOMMENDATIONS ----
if "recommendations" in st.session_state:
    st.subheader("🎯 Top Career Matches For You")
    rec_cols = st.columns(3)
    for idx, c in enumerate(st.session_state["recommendations"]):
        with rec_cols[idx]:
            st.markdown(f"### 🧭 {c['career']}")
            st.caption(f"**Key Skills:** {', '.join(c['required_skills'][:5])}")
            st.caption(f"**Focus Areas:** {', '.join(c['interest_tags'][:3])}")

    # Select career and level
    selected_career_name = st.selectbox("Select your preferred career:", [c["career"] for c in st.session_state["recommendations"]])
    selected_career_data = next(c for c in st.session_state["recommendations"] if c["career"] == selected_career_name)
    selected_level = st.radio("Select your current level:", ["Beginner", "Intermediate", "Advanced"])

    # Show roadmap only when button clicked
    if st.button("📍 Generate Roadmap"):
        st.markdown("---")
        st.subheader(f"🗺️ Personalized Roadmap for {selected_career_name} ({selected_level})")

        roadmap_steps = []
        if selected_level == "Beginner":
            roadmap_steps += [("Beginner", step) for step in selected_career_data["roadmap"]["Beginner"]]
            roadmap_steps += [("Intermediate", step) for step in selected_career_data["roadmap"]["Intermediate"]]
            roadmap_steps += [("Advanced", step) for step in selected_career_data["roadmap"]["Advanced"]]
        elif selected_level == "Intermediate":
            roadmap_steps += [("Intermediate", step) for step in selected_career_data["roadmap"]["Intermediate"]]
            roadmap_steps += [("Advanced", step) for step in selected_career_data["roadmap"]["Advanced"]]
        else:
            roadmap_steps += [("Advanced", step) for step in selected_career_data["roadmap"]["Advanced"]]

        # Display roadmap section-wise
        for level in ["Beginner", "Intermediate", "Advanced"]:
            level_steps = [step for lvl, step in roadmap_steps if lvl == level]
            if level_steps:
                st.markdown(f"## {'🟢' if level=='Beginner' else '🟠' if level=='Intermediate' else '🔴'} {level} Level")
                for i, step in enumerate(level_steps, start=1):
                    st.markdown(f"""
                    <div style='background-color:#1E1E1E;padding:15px;border-radius:10px;margin-bottom:10px;
                                border-left:5px solid #00BFFF'>
                        <h4 style='color:#00BFFF;'>Step {i}</h4>
                        <p style='color:#ddd;'>{step}</p>
                    </div>
                    """, unsafe_allow_html=True)

        # Recommended resources
        st.markdown("### 📚 Recommended Resources:")
        for r in selected_career_data["resources"]:
            st.markdown(f"🔗 {r}")

        # Save for tracker page
        st.session_state["selected_career"] = selected_career_name
        st.session_state["selected_level"] = selected_level
        st.session_state["selected_tasks"] = [step for _, step in roadmap_steps]

        st.success("✅ Roadmap generated successfully!")
        if st.button("🚀 Go to Learning Progress Tracker"):
            st.switch_page("pages/learning_progress_tracker.py")
