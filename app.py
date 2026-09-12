import streamlit as st
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from schemas import RoadmapResponse

# Load environment variables for local testing
load_dotenv()

st.set_page_config(
    page_title="AI Learning Roadmap Generator",
    page_icon="🗺️",
    layout="wide"
)

# Securely fetch API key from Secrets or Environment
def get_gemini_api_key():
    # 1. Check Streamlit Cloud Secrets (Live Deployment)
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    # 2. Check Local .env File (Local Development)
    elif os.getenv("GEMINI_API_KEY"):
        return os.getenv("GEMINI_API_KEY")
    return None

api_key = get_gemini_api_key()

if not api_key:
    st.error("⚠️ Gemini API Key config nahi hui! Deployment Settings / Secrets check karein.")
    st.stop()

# Initialize Gemini Client background mein (Hidden from UI)
client = genai.Client(api_key=api_key)

st.title("🗺️ AI Learning Roadmap Generator")
st.caption("Enter your learning preferences to get a step-by-step roadmap.")

st.divider()

# Input Form
with st.form("roadmap_form"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        domain = st.text_input("Domain / Field", placeholder="e.g. Data Science, Web Dev")
    with col2:
        level = st.selectbox("Current Skill Level", ["Beginner", "Intermediate", "Advanced"])
    with col3:
        time_frame = st.text_input("Time Commitment", placeholder="e.g. 3 Months (10 hrs/week)")
        
    submit_btn = st.form_submit_button("🚀 Generate Roadmap", type="primary", use_container_width=True)

if submit_btn:
    if not domain.strip():
        st.warning("Please enter a domain/field name!")
    else:
        with st.spinner("🤖 Designing curriculum..."):
            try:
                prompt = f"Create a comprehensive roadmap for Domain: {domain}, Level: {level}, Duration: {time_frame}"

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=RoadmapResponse,
                        temperature=0.3
                    ),
                )

                roadmap = RoadmapResponse.model_validate_json(response.text)

                st.success("✅ Roadmap Generated!")
                st.header(roadmap.title)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.metric(label="Skill Level", value=roadmap.target_level)
                with c2:
                    st.metric(label="Est. Total Time", value=roadmap.total_estimated_time)

                st.info(f"**Overview:** {roadmap.summary}")

                st.subheader("📋 Prerequisites")
                st.write(", ".join([f"`{p}`" for p in roadmap.prerequisites]))

                st.divider()
                st.subheader("🗺️ Detailed Modules & Steps")

                for m in roadmap.milestones:
                    with st.expander(f"Phase {m.phase_number}: {m.phase_title} ({m.estimated_time})", expanded=True):
                        st.write("**Key Concepts:**")
                        for concept in m.key_concepts:
                            st.markdown(f"- {concept}")
                        
                        st.markdown(f"**🛠️ Project:** {m.hands_on_project}")
                        
                        st.write("**📚 Resources:**")
                        for res in m.recommended_resources:
                            st.markdown(f"- **[{res.type}]** {res.title}")

            except Exception as e:
                st.error(f"Error generating roadmap: {str(e)}")