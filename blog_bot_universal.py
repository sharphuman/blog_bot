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

# --- 🎨 ELITE STYLING ENGINE (The "Stripe" Aesthetic) ---
# We define the styles here in Python. The AI doesn't touch them.
# This ensures 100% consistency.

FONT_STACK = "font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;"

STYLE_CONFIG = {
    "WRAPPER": f"{FONT_STACK} max-width: 720px; margin: 0 auto; background: #ffffff; padding: 48px; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,0.06);",
    "H2": f"{FONT_STACK} color: #111827; font-size: 30px; font-weight: 700; letter-spacing: -0.02em; margin-top: 56px; margin-bottom: 24px; line-height: 1.3;",
    "H3": f"{FONT_STACK} color: #1e293b; font-size: 22px; font-weight: 600; margin-top: 40px; margin-bottom: 16px;",
    "P": f"{FONT_STACK} color: #374151; font-size: 19px; line-height: 1.75; margin-bottom: 28px;",
    "UL": f"{FONT_STACK} color: #374151; font-size: 19px; line-height: 1.75; margin-bottom: 28px; padding-left: 24px;",
    "LI": "margin-bottom: 12px; padding-left: 8px;",
    "STRONG": "color: #111827; font-weight: 600;",
    "LINK": "color: #2563eb; text-decoration: underline; text-underline-offset: 4px; font-weight: 500;",
    "BOX": f"{FONT_STACK} background: #F8FAFC; border-left: 4px solid #2563eb; border-radius: 8px; padding: 32px; margin-bottom: 48px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);"
}

def inject_elite_styles(raw_html):
    """
    Takes raw HTML from AI and forcibly injects modern CSS into every tag.
    """
    # 1. Clean Markdown
    html = raw_html.replace("```html", "").replace("```", "").strip()
    
    # 2. Inject Styles (Brute Force Replacement)
    html = html.replace("<h2>", f'<h2 style="{STYLE_CONFIG["H2"]}">')
    html = html.replace("<h3>", f'<h3 style="{STYLE_CONFIG["H3"]}">')
    html = html.replace("<p>", f'<p style="{STYLE_CONFIG["P"]}">')
    html = html.replace("<ul>", f'<ul style="{STYLE_CONFIG["UL"]}">')
    html = html.replace("<li>", f'<li style="{STYLE_CONFIG["LI"]}">')
    html = html.replace("<strong>", f'<strong style="{STYLE_CONFIG["STRONG"]}">')
    html = html.replace("<a ", f'<a style="{STYLE_CONFIG["LINK"]}" ')
    
    # 3. Handle the Key Takeaways Box
    # We look for a marker div and replace it with our full styled box
    if '<div class="takeaways">' in html:
        html = html.replace('<div class="takeaways">', f'<div style="{STYLE_CONFIG["BOX"]}">')
    
    # 4. Wrap in Master Container
    final_html = f'<div style="{STYLE_CONFIG["WRAPPER"]}">{html}</div>'
    
    return final_html

# --- AI WRITER ---
def generate_blog_post(topic, persona, key_points, tone):
    prompt = f"""
    IDENTITY: {persona}
    TONE: {tone}
    TOPIC: "{topic}"
    DETAILS: {key_points}
    
    TASK: Write the blog content using VERY simple HTML tags.
    
    CRITICAL STRUCTURE RULES:
    1. Start with this EXACT line for the box: <div class="takeaways">
    2. Inside the box, put an <h3>Key Takeaways</h3> and a <ul> list. Close the </div>.
    3. Use <h2> for main headers.
    4. Use <p> for text.
    5. Use <strong> for emphasis.
    6. Do NOT add any style="..." attributes. The Python script will add them later.
    7. No Markdown.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        # Pass raw HTML to our Styler Function
        return inject_elite_styles(response.choices[0].message.content)
        
    except Exception as e: return f"Error: {e}"

def refine_blog_post(current_html, instructions):
    # Strip wrapper to edit content
    core_text = current_html.split('<div style="')[1] # Hacky but works to strip the first container
    core_text = core_text.split('">', 1)[1]
    core_text = core_text.rsplit('</div>', 1)[0]
    
    prompt = f"""
    Editor Task: Edit this content based on instructions.
    INSTRUCTIONS: "{instructions}"
    CONTENT: {core_text}
    RULES: Return simple HTML tags (h2, p, ul). No styles. No markdown.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
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
st.set_page_config(page_title="Universal Auto-Blogger", page_icon="✍️", layout="wide")
st.title("✍️ Universal Auto-Blogger (Elite Design)")

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
        user_feedback = st.chat_input("Make edits here...")
        if user_feedback:
            with st.spinner("Editing..."):
                st.session_state.blog_content = refine_blog_post(st.session_state.blog_content, user_feedback)
                st.rerun()
        st.markdown("### SEO Data")
        st.code(st.session_state.seo_data)

    with col2:
        st.subheader("📖 Preview (What you see is what you get)")
        # Renders the HTML visually
        st.markdown(st.session_state.blog_content, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 HTML Code")
        st.info("Copy this EXACTLY into the GHL Code Editor (< > button).")
        st.code(st.session_state.blog_content, language="html")
