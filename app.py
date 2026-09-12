import streamlit as st
from groq import Groq

# Set page layout
st.set_page_config(
    page_title="AI Content & Roadmap Generator",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Content & Roadmap Generator")
st.write("Generate tailored learning roadmaps and social media posts powered by Groq.")

# Sidebar for API Key
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input(
    "Enter your Groq API Key:",
    type="password",
    help="Get a free key at https://console.groq.com"
)

# User Selection Inputs
st.subheader("Customize Your Request")

col1, col2 = st.columns(2)

with col1:
    content_type = st.selectbox(
        "Content Type",
        ["Learning Roadmap", "Social Media Post", "Tutorial Breakdown", "Quick Tips List"]
    )
    topic = st.text_input(
        "Topic / Subject",
        placeholder="e.g., Python for Beginners, System Design, Data Science"
    )
    platform = st.selectbox(
        "Target Platform",
        ["LinkedIn", "Twitter / X", "Instagram", "Medium", "Dev.to"]
    )

with col2:
    target_audience = st.selectbox(
        "Target Audience",
        ["Absolute Beginners", "Intermediate Developers", "College Students", "Tech Professionals"]
    )
    tone = st.selectbox(
        "Tone",
        ["Professional & Informative", "Casual & Engaging", "Inspirational", "Step-by-Step Educational"]
    )

# Generation Logic
if st.button("✨ Generate Output", type="primary"):
    if not api_key:
        st.error("Please enter your Groq API Key in the sidebar to proceed.")
    elif not topic.strip():
        st.warning("Please enter a topic before generating.")
    else:
        try:
            client = Groq(api_key=api_key)
            
            prompt = f"""
            You are an expert tech content creator and educator.
            
            Generate a high-quality {content_type} based on the following details:
            - Topic: {topic}
            - Platform: {platform}
            - Target Audience: {target_audience}
            - Tone: {tone}
            
            Structure the output clearly with:
            1. Title / Headline
            2. Main Content (If it's a Learning Roadmap, organize it into clear timeline modules like Week 1, Week 2, etc.)
            3. Engaging Caption / Summary
            4. 5-10 Relevant Hashtags tailored for {platform}
            """

            with st.spinner("Generating your content..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2048,
                )
                
                result_text = response.choices[0].message.content
                
                st.success("Generation Complete!")
                st.markdown("---")
                st.markdown(result_text)
                
                # Download Button for the generated content
                st.download_button(
                    label="📥 Download Generated Content (.txt)",
                    data=result_text,
                    file_name=f"{topic.lower().replace(' ', '_')}_content.txt",
                    mime="text/plain"
                )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")