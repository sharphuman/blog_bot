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

# --- DESIGNER STYLING (The "Human" Look) ---
# This CSS makes it look like a high-end Medium article or Magazine
BLOG_WRAPPER_START = """
<div style="
    background-color: #ffffff; 
    color: #374151; 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
    font-size: 18px; 
    line-height: 1.7; 
    padding: 40px; 
    border-radius: 12px; 
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); 
    max-width: 800px; 
    margin: 0 auto;">
"""
BLOG_WRAPPER_END = "</div>"

# --- HELPER: CLEANER ---
def clean_and_wrap_html(text):
    text = text.replace("```html", "").replace("```", "").strip()
    text = text.replace(BLOG_WRAPPER_START.strip(), "").replace(BLOG_WRAPPER_END.strip(), "")
    return f"{BLOG_WRAPPER_START}\n{text}\n{BLOG_WRAPPER_END}"

# --- AI WRITER ---
def generate_blog_post(topic, persona, key_points, tone):
    
    # Styled "Key Takeaways" Box (Modern Card Style)
    takeaway_style = """
    background-color: #f8fafc; 
    border-left: 6px solid #2563eb; 
    padding: 24px; 
    border-radius: 8px; 
    margin-bottom: 40px; 
    color: #1e293b !important;
    """
    
    prompt = f"""
    IDENTITY: {persona}
    TONE: {tone} (Write like a human expert, not a robot. Use contractions, vary sentence length.)
    TOPIC: "{topic}"
    DETAILS: {key_points}
    
    TASK: Write the inner HTML content.
    
    FORMATTING RULES (Strict):
    1. Start with the Key Takeaways box: <div style="{takeaway_style}">
    2. Inside box: <h3>Key Takeaways</h3> and <ul>. Text MUST be Dark (#1e293b).
    3. HEADERS: Use <h2 style="color: #0f172a; margin-top: 40px; font-weight: 700;"> for main sections.
    4. EMPHASIS: Use <strong style="color: #2563eb;"> for key phrases (adds blue highlights).
    5. LINKS: If you mention "Contact Us", link to /contact.
    6. No <html>/<body> tags. No Markdown.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        return clean_and_wrap_html(response.choices[0].message.content)
        
    except Exception as e: return f"Error: {e}"

def refine_blog_post(current_html, instructions):
    core_text = current_html.replace(BLOG_WRAPPER_START, "").replace(BLOG_WRAPPER_END, "")
    
    prompt = f"""
    Expert Editor Task: Edit this HTML based on instructions.
    INSTRUCTIONS: "{instructions}"
    HTML CONTENT: {core_text}
    RULES: Keep the inline CSS styles (color, font, etc). Output ONLY HTML.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        return clean_and_wrap_html(response.choices[0].message.content)
    except Exception as e: return current_html

def generate_seo_meta(content):
    prompt = f"Generate Meta Description (160 chars), Slug, and 5 Keywords for:\n{content[:3000]}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except: return ""

# --- UI ---
st.set_page_config(page_title="Universal Auto-Blogger", page_icon="✍️", layout="wide")
st.title("✍️ Universal Auto-Blogger (Designer Edition)")

with st.sidebar:
    st.header("1. Settings")
    persona = st.text_area("Persona", height=100, 
        value="Lead Revenue Architect at Sharp Human. Expert in AI and RevOps.")
    tone = st.select_slider("Tone", options=["Corporate", "Direct", "Storyteller", "Witty"], value="Storyteller")
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
        user_feedback = st.chat_input("Ex: 'Make the intro punchier'")
        if user_feedback:
            with st.spinner("Editing..."):
                st.session_state.blog_content = refine_blog_post(st.session_state.blog_content, user_feedback)
                st.rerun()
        st.markdown("### SEO Data")
        st.code(st.session_state.seo_data)

    with col2:
        st.subheader("📖 Preview")
        st.markdown(st.session_state.blog_content, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 HTML Code")
        st.info("Copy this EXACTLY into the GHL Code Editor (< > button).")
        st.code(st.session_state.blog_content, language="html")
