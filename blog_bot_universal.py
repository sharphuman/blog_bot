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

# --- 🌑 DARK MODE STYLING ENGINE ---
# Optimized for your Dark Theme website (Acquisity/GHL)

FONT_STACK = "font-family: 'Inter', system-ui, -apple-system, sans-serif;"

STYLE_CONFIG = {
    # 1. Main Container: Transparent background so it shows your site's dark color
    "WRAPPER": f"{FONT_STACK} max-width: 740px; margin: 0 auto; background: transparent; padding: 20px;",
    
    # 2. Typography: White/Light Grey text for Dark Backgrounds
    "H2": f"{FONT_STACK} color: #ffffff; font-size: 32px; font-weight: 700; margin-top: 60px; margin-bottom: 24px; letter-spacing: -0.02em;",
    "H3": f"{FONT_STACK} color: #f8fafc; font-size: 24px; font-weight: 600; margin-top: 40px; margin-bottom: 16px;",
    "P": f"{FONT_STACK} color: #cbd5e1; font-size: 19px; line-height: 1.8; margin-bottom: 28px;", # Slate 300 (Soft White)
    
    # 3. Lists
    "UL": f"{FONT_STACK} color: #cbd5e1; font-size: 19px; line-height: 1.8; margin-bottom: 28px; padding-left: 24px;",
    "LI": "margin-bottom: 14px; padding-left: 8px;",
    
    # 4. Accents
    "STRONG": "color: #ffffff; font-weight: 600;", # Pure white for bold
    "LINK": "color: #60a5fa; text-decoration: underline; text-underline-offset: 4px;", # Light Blue link
    
    # 5. The "Dark Card" for Takeaways
    # Dark Grey background (#1e293b) with Blue Border
    "BOX": f"{FONT_STACK} background: #1e293b; border-left: 4px solid #3b82f6; border-radius: 8px; padding: 32px; margin-bottom: 48px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);"
}

def inject_elite_styles(raw_html):
    html = raw_html.replace("```html", "").replace("```", "").strip()
    
    # Inject Inline Styles
    html = html.replace("<h2>", f'<h2 style="{STYLE_CONFIG["H2"]}">')
    html = html.replace("<h3>", f'<h3 style="{STYLE_CONFIG["H3"]}">')
    html = html.replace("<p>", f'<p style="{STYLE_CONFIG["P"]}">')
    html = html.replace("<ul>", f'<ul style="{STYLE_CONFIG["UL"]}">')
    html = html.replace("<li>", f'<li style="{STYLE_CONFIG["LI"]}">')
    html = html.replace("<strong>", f'<strong style="{STYLE_CONFIG["STRONG"]}">')
    html = html.replace("<a ", f'<a style="{STYLE_CONFIG["LINK"]}" ')
    
    if '<div class="takeaways">' in html:
        html = html.replace('<div class="takeaways">', f'<div style="{STYLE_CONFIG["BOX"]}">')
    
    return f'<div style="{STYLE_CONFIG["WRAPPER"]}">{html}</div>'

# --- AI WRITER ---
def generate_blog_post(topic, persona, key_points, tone):
    prompt = f"""
    IDENTITY: {persona}
    TONE: {tone}
    TOPIC: "{topic}"
    DETAILS: {key_points}
    
    TASK: Write blog content using simple HTML tags.
    
    CRITICAL STRUCTURE RULES:
    1. Start with: <div class="takeaways">
    2. Inside box: <h3>Key Takeaways</h3> and <ul> list. Close </div>.
    3. Use <h2> for headers.
    4. Use <p> for text.
    5. Use <strong> for emphasis.
    6. Do NOT add style attributes (Python handles it).
    7. No Markdown.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": prompt}]
        )
        return inject_elite_styles(response.choices[0].message.content)
    except Exception as e: return f"Error: {e}"

def refine_blog_post(current_html, instructions):
    # Strip wrapper to edit content
    try:
        core_text = current_html.split('style="')[1].split('">', 1)[1].rsplit('</div>', 1)[0]
    except:
        core_text = current_html # Fallback if split fails

    prompt = f"""
    Editor Task: Edit this content based on instructions.
    INSTRUCTIONS: "{instructions}"
    CONTENT: {core_text}
    RULES: Return simple HTML tags (h2, p, ul). No styles. No markdown.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": prompt}]
        )
        return inject_elite_styles(response.choices[0].message.content)
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
st.set_page_config(page_title="Dark Mode Auto-Blogger", page_icon="🌑", layout="wide")
st.title("🌑 Dark Mode Auto-Blogger")

# Dark Mode Preview Hack for Streamlit
st.markdown("""
<style>
    div[data-testid="stMarkdownContainer"] p { color: #ccc; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("1. Settings")
    persona = st.text_area("Persona", height=100, 
        value="Lead Revenue Architect at Sharp Human. Expert in AI and RevOps.")
    tone = st.select_slider("Tone", options=["Corporate", "Direct", "Educational", "Storyteller"], value="Educational")
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
        st.subheader("📖 Dark Mode Preview")
        # Wrapper to simulate dark background in Streamlit
        st.markdown(f"""
        <div style="background-color: #0f172a; padding: 20px; border-radius: 10px;">
            {st.session_state.blog_content}
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 Copy This Code")
        st.code(st.session_state.blog_content, language="html")
