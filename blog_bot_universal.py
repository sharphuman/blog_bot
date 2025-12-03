import streamlit as st
from openai import OpenAI

# --- CONFIGURATION ---
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# --- SESSION STATE ---
if "blog_content" not in st.session_state:
    st.session_state.blog_content = ""
if "seo_data" not in st.session_state:
    st.session_state.seo_data = ""

# --- AI WRITER ---
def generate_blog_post(topic, persona, key_points, tone):
    prompt = f"""
    IDENTITY: {persona}
    TONE: {tone}
    TOPIC: "{topic}"
    DETAILS: {key_points}
    
    TASK: Write a blog post using Markdown formatting.
    
    FORMATTING RULES:
    1. Use # for Main Title.
    2. Use ## for Section Headers.
    3. Use ### for sub-headers.
    4. Use **Bold** for emphasis.
    5. Use > for the "Key Takeaways" section (to make it a quote block).
    6. Do NOT use HTML code. Just clean text.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e: return f"Error: {e}"

def generate_seo_meta(content):
    prompt = f"Generate Meta Description (160 chars), Slug, and 5 Keywords for:\n{content[:3000]}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except: return ""

# --- UI ---
st.set_page_config(page_title="Stress-Free Blogger", page_icon="🧘", layout="wide")
st.title("🧘 Stress-Free Auto-Blogger")

with st.sidebar:
    st.header("Settings")
    persona = st.text_area("Persona", height=100, 
        value="Lead Revenue Architect at Sharp Human.")
    tone = st.select_slider("Tone", options=["Corporate", "Direct", "Educational"], value="Educational")
    if st.button("Start Over"):
        st.session_state.blog_content = ""
        st.rerun()

if not st.session_state.blog_content:
    with st.form("blog_form"):
        topic = st.text_area("Topic", "e.g. A2P 10DLC Compliance")
        key_points = st.text_area("Key Points", "- Mention Sharp Human Audit")
        submitted = st.form_submit_button("Generate")

    if submitted and topic:
        with st.spinner("Writing..."):
            st.session_state.blog_content = generate_blog_post(topic, persona, key_points, tone)
            st.session_state.seo_data = generate_seo_meta(st.session_state.blog_content)
            st.rerun()

else:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📖 The Article")
        st.info("Instructions: Highlight the text below, Copy (Ctrl+C), and Paste (Ctrl+V) directly into the GHL Visual Editor.")
        
        # Display as rendered text
        st.markdown(st.session_state.blog_content)
        
    with col2:
        st.subheader("🔍 SEO Data")
        st.code(st.session_state.seo_data, language="text")
