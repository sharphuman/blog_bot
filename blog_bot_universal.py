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

# --- HELPER: CLEANER ---
def clean_html_output(text):
    text = text.replace("```html", "").replace("```", "").strip()
    return text

# --- AI WRITER ---
def generate_blog_post(topic, persona, key_points, tone):
    
    # MASTER STYLE WRAPPER
    # This forces the whole blog to have a White Background and Dark Text
    # No more invisible text issues!
    wrapper_start = """
    <div style="background-color: #ffffff; color: #333333; font-family: sans-serif; padding: 20px; border-radius: 8px; line-height: 1.6;">
    """
    wrapper_end = "</div>"
    
    # Key Takeaways Box Style (Clean Grey)
    box_style = 'border: 1px solid #e0e0e0; background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin-bottom: 30px;'
    
    prompt = f"""
    IDENTITY: {persona}
    TONE: {tone}
    TOPIC: "{topic}"
    DETAILS: {key_points}
    
    TASK: Write a blog post in HTML.
    
    FORMATTING RULES:
    1. Start with the Key Takeaways box using EXACTLY this div: <div style="{box_style}">
    2. Inside that box, use an <h3> tag for the title "Key Takeaways".
    3. Use <h2> for all main section headers.
    4. Use <strong> for emphasis.
    5. DO NOT include <html> or <body> tags.
    6. NO markdown backticks.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        # Wrap the AI content in our Safe Color Container
        raw_html = clean_html_output(response.choices[0].message.content)
        return f"{wrapper_start}\n{raw_html}\n{wrapper_end}"
        
    except Exception as e: return f"Error: {e}"

def refine_blog_post(current_content, instructions):
    # We strip the wrapper before editing, then re-add it later
    # This prevents the AI from messing up the outer container
    core_content = current_content.replace('<div style="background-color: #ffffff; color: #333333; font-family: sans-serif; padding: 20px; border-radius: 8px; line-height: 1.6;">', '').replace('</div>', '')
    
    prompt = f"""
    You are an Expert Editor. Edit this HTML content based on instructions.
    USER INSTRUCTIONS: "{instructions}"
    CURRENT HTML: {core_content}
    
    RULES: Output ONLY valid HTML. Keep formatting tags (h2, ul). No markdown.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": prompt}]
        )
        new_core = clean_html_output(response.choices[0].message.content)
        
        # Re-wrap in the Safe Color Container
        wrapper_start = """
        <div style="background-color: #ffffff; color: #333333; font-family: sans-serif; padding: 20px; border-radius: 8px; line-height: 1.6;">
        """
        return f"{wrapper_start}\n{new_core}\n</div>"
        
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
st.title("✍️ Universal Auto-Blogger")

# SIDEBAR
with st.sidebar:
    st.header("1. Draft Settings")
    persona = st.text_area("Persona", height=100, 
        value="Lead Revenue Architect at Sharp Human. Expert in AI, Deliverability, and RevOps.")
    tone = st.select_slider("Tone", options=["Corporate", "Direct", "Educational", "Witty"], value="Direct")
    
    st.divider()
    if st.button("Clear / Start Over", type="secondary"):
        st.session_state.blog_content = ""
        st.rerun()

# GENERATION FORM
if not st.session_state.blog_content:
    with st.form("blog_form"):
        st.subheader("Create New Post")
        topic = st.text_area("Topic", height=68, placeholder="e.g. A2P 10DLC Compliance")
        key_points = st.text_area("Key Points", height=100, placeholder="- Mention Sharp Human Audit")
        submitted = st.form_submit_button("Generate First Draft")

    if submitted and topic:
        with st.spinner("Drafting article..."):
            content = generate_blog_post(topic, persona, key_points, tone)
            st.session_state.blog_content = content
            st.session_state.seo_data = generate_seo_meta(content)
            st.rerun()

# EDITOR & PREVIEW
else:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💬 AI Editor")
        user_feedback = st.chat_input("Ex: 'Make the title punchier'")
        if user_feedback:
            with st.spinner("Applying edits..."):
                new_ver = refine_blog_post(st.session_state.blog_content, user_feedback)
                st.session_state.blog_content = new_ver
                st.rerun()
        
        st.divider()
        st.markdown("### 🔍 SEO Data")
        st.code(st.session_state.seo_data, language="text")

    with col2:
        st.subheader("📖 Live Preview")
        # Render HTML (It will look like a white document now)
        st.markdown(st.session_state.blog_content, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 HTML Code (For GHL)")
        st.text_area("Copy this:", value=st.session_state.blog_content, height=300)
