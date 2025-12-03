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

# --- STYLING (Force White Paper Look) ---
BLOG_WRAPPER_START = """
<div style="background-color: #ffffff; color: #000000; font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; padding: 40px; border-radius: 8px; border: 1px solid #e0e0e0;">
"""
BLOG_WRAPPER_END = "</div>"

# --- HELPER: AGGRESSIVE CLEANER ---
def clean_and_wrap_html(text):
    """
    Removes Markdown lines and wraps in the white container.
    """
    # 1. Strip Markdown lines
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        if "```" in line: continue # Skip lines with backticks
        clean_lines.append(line)
    
    text = "\n".join(clean_lines).strip()
    
    # 2. Strip previous wrappers to avoid duplication
    text = text.replace(BLOG_WRAPPER_START.strip(), "")
    text = text.replace(BLOG_WRAPPER_END.strip(), "")
    
    # 3. Return wrapped
    return f"{BLOG_WRAPPER_START}\n{text}\n{BLOG_WRAPPER_END}"

# --- AI WRITER ---
def generate_blog_post(topic, persona, key_points, tone):
    # Style for Takeaways Box (Grey BG, Blue Border, Black Text)
    takeaway_box = 'background-color: #f0f4f8; border-left: 6px solid #007bff; padding: 20px; margin-bottom: 30px; color: #000000 !important;'
    
    prompt = f"""
    IDENTITY: {persona}
    TONE: {tone}
    TOPIC: "{topic}"
    DETAILS: {key_points}
    
    TASK: Write the inner HTML content for a blog post.
    
    FORMATTING RULES:
    1. Start immediately with a Key Takeaways box: <div style="{takeaway_box}">
    2. Inside the box, use <h3>Key Takeaways</h3> and <ul>. Ensure text is Black.
    3. Use <h2> for main headers.
    4. Use <p> for paragraphs.
    5. Do NOT use <html>, <head>, or <body> tags.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        return clean_and_wrap_html(response.choices[0].message.content)
        
    except Exception as e: return f"Error: {e}"

def refine_blog_post(current_html, instructions):
    # Strip wrapper for editing
    core_text = current_html.replace(BLOG_WRAPPER_START, "").replace(BLOG_WRAPPER_END, "")
    
    prompt = f"""
    You are an Expert Editor. Edit this HTML based on instructions.
    USER INSTRUCTIONS: "{instructions}"
    CURRENT HTML: {core_text}
    RULES: Output ONLY valid HTML. Keep formatting tags.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        return clean_and_wrap_html(response.choices[0].message.content)
    except Exception as e: return current_html

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
st.title("✍️ Universal Auto-Blogger (Final Fix)")

with st.sidebar:
    st.header("1. Settings")
    persona = st.text_area("Persona", height=100, 
        value="Lead Revenue Architect at Sharp Human. Expert in AI and RevOps.")
    tone = st.select_slider("Tone", options=["Corporate", "Direct", "Educational"], value="Direct")
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
            content = generate_blog_post(topic, persona, key_points, tone)
            st.session_state.blog_content = content
            st.session_state.seo_data = generate_seo_meta(content)
            st.rerun()

else:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💬 Editor")
        user_feedback = st.chat_input("Make edits here...")
        if user_feedback:
            with st.spinner("Editing..."):
                st.session_state.blog_content = refine_blog_post(st.session_state.blog_content, user_feedback)
                st.rerun()
        st.markdown("### SEO Data")
        st.code(st.session_state.seo_data)

    with col2:
        st.subheader("📖 Preview")
        # Renders the HTML to verify it looks correct (White box, black text)
        st.markdown(st.session_state.blog_content, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 HTML Code")
        st.info("Copy this EXACTLY into the GHL Code Editor (< > button).")
        st.code(st.session_state.blog_content, language="html")
