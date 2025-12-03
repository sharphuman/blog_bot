import streamlit as st
from openai import OpenAI

# --- CONFIGURATION ---
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# --- SESSION STATE SETUP (The Bot's Memory) ---
if "blog_content" not in st.session_state:
    st.session_state.blog_content = ""
if "seo_data" not in st.session_state:
    st.session_state.seo_data = ""

# --- AI FUNCTIONS ---

def generate_blog_post(topic, persona, key_points, tone):
    prompt = f"""
    IDENTITY: {persona}
    TONE: {tone}
    TOPIC: "{topic}"
    DETAILS: {key_points}
    
    TASK: Write a high-value blog post (HTML format).
    RULES: Use <h2>, <ul>, <strong>. No <html> tags. Start with <h1> Title. Include a 'Key Takeaways' box.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e: return f"Error: {e}"

def refine_blog_post(current_content, instructions):
    """
    Takes existing HTML and applies user corrections.
    """
    prompt = f"""
    You are an Expert Editor.
    
    YOUR TASK:
    Edit the following HTML blog post based strictly on the user's instructions.
    Do NOT lose the HTML formatting (<h2>, <ul>, etc).
    Keep the rest of the article consistent if not asked to change it.
    
    USER INSTRUCTIONS: "{instructions}"
    
    CURRENT HTML CONTENT:
    {current_content}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e: return current_content

def generate_seo_meta(content):
    prompt = f"Generate Meta Description (160 chars), Slug, and 5 Keywords for this HTML:\n{content[:3000]}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except: return ""

# --- UI ---
st.set_page_config(page_title="Universal Auto-Blogger", page_icon="✍️", layout="wide")
st.title("✍️ Universal Auto-Blogger & Editor")

# --- SECTION 1: GENERATION FORM ---
with st.sidebar:
    st.header("1. Draft Settings")
    persona = st.text_area("Persona", height=100, 
        value="Lead Revenue Architect at Sharp Human. Expert in AI, Deliverability, and RevOps.")
    tone = st.select_slider("Tone", options=["Corporate", "Direct", "Educational", "Witty"], value="Direct")
    
    st.divider()
    if st.button("Clear / Start Over", type="secondary"):
        st.session_state.blog_content = ""
        st.rerun()

# Main Input Area (Only show if empty)
if not st.session_state.blog_content:
    with st.form("blog_form"):
        st.subheader("Create New Post")
        topic = st.text_area("Topic", height=68, placeholder="e.g. A2P 10DLC Compliance Fixes")
        key_points = st.text_area("Key Points", height=100, placeholder="- Mention Sharp Human Audit\n- Explain the 'Spam Likely' risk")
        submitted = st.form_submit_button("Generate First Draft")

    if submitted and topic:
        with st.spinner("Drafting article..."):
            content = generate_blog_post(topic, persona, key_points, tone)
            st.session_state.blog_content = content
            st.session_state.seo_data = generate_seo_meta(content)
            st.rerun()

# --- SECTION 2: EDITOR & REFINEMENT ---
else:
    # Two Columns: Editor on Left, Preview on Right
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💬 AI Editor Chat")
        st.info("The blog is generated. Use the chat below to tweak it.")
        
        # THE CHAT INTERFACE
        user_feedback = st.chat_input("Ex: 'Make the title punchier' or 'Fix the A2P definition'")
        
        if user_feedback:
            with st.spinner("Applying edits..."):
                new_version = refine_blog_post(st.session_state.blog_content, user_feedback)
                st.session_state.blog_content = new_version
                st.rerun()
                
        st.divider()
        st.markdown("### 🔍 SEO Data")
        st.code(st.session_state.seo_data, language="text")

    with col2:
        st.subheader("📖 Live Preview")
        # Display the HTML visually
        st.markdown(st.session_state.blog_content, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 HTML Code (For GHL)")
        st.text_area("Copy this:", value=st.session_state.blog_content, height=300)
