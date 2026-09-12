import streamlit as st
import os
from typing import List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

# ==========================================
# 1. Structured Data Schema
# ==========================================
class Resource(BaseModel):
    title: str
    type: str = Field(..., description="Book, Course, YouTube, Documentation, etc.")

class Milestone(BaseModel):
    phase_number: int
    phase_title: str
    estimated_time: str
    key_concepts: List[str]
    hands_on_project: str
    recommended_resources: List[Resource]

class RoadmapResponse(BaseModel):
    title: str
    summary: str
    target_level: str
    total_estimated_time: str
    prerequisites: List[str]
    milestones: List[Milestone]

# ==========================================
# 2. Config & Security Setup
# ==========================================
load_dotenv()

st.set_page_config(
    page_title="AI Learning Roadmap Generator",
    page_icon="🎓",
    layout="wide"
)

def get_gemini_api_key():
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    elif os.getenv("GEMINI_API_KEY"):
        return os.getenv("GEMINI_API_KEY")
    return None

api_key = get_gemini_api_key()

if not api_key:
    st.error("⚠️ Gemini API Key missing! Streamlit Cloud Secrets check karein.")
    st.stop()

client = genai.Client(api_key=api_key)

# ==========================================
# 3. UI Layout
# ==========================================
st.title("🎓 AI Learning Roadmap Generator")
st.caption("Create a personalized learning roadmap based on your field, skill level, and available time.")

st.write("") 

domain = st.text_input("📚 Domain / Field", placeholder="e.g. Machine Learning")
level = st.selectbox("🎯 Skill Level", ["Beginner", "Intermediate", "Advanced"])
time_frame = st.text_input("⏰ Time Available", placeholder="e.g. 8 weeks, 2 hours per day")

st.write("") 

submit_btn = st.button("🚀 Generate Roadmap", type="secondary")

# ==========================================
# 4. Processing with Latest Gemini 3.6 Model
# ==========================================
if submit_btn:
    if not domain.strip():
        st.warning("Please enter a domain or field!")
    else:
        with st.spinner("⚡ Designing your customized learning roadmap..."):
            prompt = f"""
            You are an expert curriculum planner. Create a step-by-step learning roadmap for:
            - Domain/Field: {domain}
            - Skill Level: {level}
            - Time Commitment: {time_frame}
            
            Provide logical phases, key topics, a practical project, and helpful resources.
            """

            try:
                # Direct call with Google's mandated model
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=RoadmapResponse,
                        temperature=0.3,
                    ),
                )

                roadmap = RoadmapResponse.model_validate_json(response.text)

                # Output Display
                st.divider()
                st.success("🎉 Roadmap Generated Successfully!")
                st.header(roadmap.title)
                
                col1, col2 = st.columns(2)
                col1.metric(label="Skill Level Target", value=roadmap.target_level)
                col2.metric(label="Total Estimated Time", value=roadmap.total_estimated_time)

                st.info(f"**Overview:** {roadmap.summary}")

                if roadmap.prerequisites:
                    st.subheader("📋 Prerequisites")
                    st.write(", ".join([f"`{p}`" for p in roadmap.prerequisites]))

                st.divider()
                st.subheader("🗺️ Learning Path Steps")

                for m in roadmap.milestones:
                    with st.expander(f"Phase {m.phase_number}: {m.phase_title} ({m.estimated_time})", expanded=True):
                        st.markdown("**🧠 Key Concepts & Topics to Master:**")
                        for concept in m.key_concepts:
                            st.markdown(f"- {concept}")
                        
                        st.markdown(f"**🛠️ Practical Project:** {m.hands_on_project}")
                        
                        st.markdown("**📚 Recommended Resources:**")
                        for res in m.recommended_resources:
                            st.markdown(f"- **[{res.type}]** {res.title}")

            except Exception as e:
                st.error(f"API Error: {str(e)}")
