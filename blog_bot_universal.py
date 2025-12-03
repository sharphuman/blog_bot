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

# --- 🎨 THE "MODERN SAAS" STYLING ENGINE ---
# This CSS forces the blog to look like a high-end tech site (Stripe/Notion style).
# We use !important to override GoHighLevel defaults.

BLOG_WRAPPER_START = """
<div style="
    max-width: 720px;
    margin: 0 auto;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    color: #334155; /* Slate 700 */
    font-size: 19px;
    line-height: 1.8;
    background-color: #ffffff;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
">
"""
BLOG_WRAPPER_END = "</div>"

# The "Notion Style" Callout Box
TAKEAWAY_BOX = """
<div style="
    background-color: #f8fafc; 
    border-left: 5px solid #2563eb; 
    padding: 24px; 
    border-radius: 6px; 
    margin-bottom: 40px;
    margin-top: 10px;
">
"""

# --- HELPER: CLEANER ---
def clean_and_wrap_html(text):
    text = text.replace("```html", "").replace("```", "").strip()
    text = text.replace(BLOG_WRAPPER_START.strip(), "").replace(BLOG_WRAPPER_END.strip(), "")
    return f"{BLOG_WRAPPER_START}\n{text}\n{BLOG_WRAPPER_END}"

# --- AI WRITER ---
def generate_blog_post(topic, persona, key_points, tone):
    
    prompt = f"""
    IDENTITY: {persona}
    TONE: {tone} (Write like a modern tech thought leader. Crisp, authoritative, human.)
    TOPIC: "{topic}"
    DETAILS: {key_points}
    
    TASK: Write the HTML content.
    
    STYLING RULES (Strictly enforce these inline styles):
    1. Start with the Key Takeaways box using EXACTLY this string: {TAKEAWAY_BOX}
    2. Inside that box, use <h3 style="margin-top: 0; color: #0f172a; font-weight: 700; font-size: 20px;">Key Takeaways</h3> and <ul style="color: #334155; margin-bottom: 0; padding-left: 20px;">.
    3. HEADERS: Use <h2 style="color: #0f172a; font-weight: 700; font-size: 28px; margin-top: 50px; margin-bottom: 20px; letter-spacing: -0.02em;"> for main sections.
    4. PARAGRAPHS: Use <p style="margin-bottom: 24px;">.
    5. EMPHASIS: Use <strong style="color: #0f172a; font-weight: 600;"> for bold text.
    6. LINKS: Use <a href="#" style="color: #2563eb; text-decoration: underline; text-decoration-thickness: 2px; font-weight: 500;"> for links.
    7. NO <html>/<body> tags.
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
    Expert Editor Task: Edit this HTML.
    INSTRUCTIONS: "{instructions}"
    HTML CONTENT: {core_text}
    RULES: Keep the inline CSS styles exactly as they are. Output ONLY HTML.
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
st.title("✍️ Universal Auto-Blogger (Modern UI)")

with st.sidebar:
    st.header("1. Settings")
    persona = st.text_area("Persona", height=100, 
        value="Lead Revenue Architect at Sharp Human. Expert in AI and RevOps.")
    tone = st.select_slider("Tone", 
        options=["Corporate", "Direct", "Educational", "Storyteller", "Witty"], 
        value="Educational")
        
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
