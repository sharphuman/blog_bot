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
    
    # 1. Define the Styles to be injected EVERYWHERE
    # We apply these to every single tag so GHL can't revert to Times New Roman
    
    FONT_STYLE = "font-family: 'Inter', Helvetica, Arial, sans-serif; color: #334155; line-height: 1.8; font-size: 18px;"
    HEADER_STYLE = "font-family: 'Inter', Helvetica, Arial, sans-serif; color: #0f172a; font-weight: 700; margin-top: 40px; margin-bottom: 20px;"
    H2_STYLE = f"{HEADER_STYLE} font-size: 28px;"
    H3_STYLE = f"{HEADER_STYLE} font-size: 22px;"
    
    # The Takeaways box needs to be robust
    BOX_STYLE = "background-color: #f1f5f9; border-left: 5px solid #2563eb; padding: 25px; margin-bottom: 40px; border-radius: 8px;"
    
    prompt = f"""
    IDENTITY: {persona}
    TONE: {tone}
    TOPIC: "{topic}"
    DETAILS: {key_points}
    
    TASK: Write the blog post HTML.
    
    CRITICAL FORMATTING RULES (Apply these styles inline to every tag):
    
    1. Start with the Key Takeaways Box:
       <div style="{BOX_STYLE}">
          <h3 style="{H3_STYLE} margin-top: 0;">Key Takeaways</h3>
          <ul style="{FONT_STYLE} margin-bottom: 0; padding-left: 20px;">
             <li>...</li>
          </ul>
       </div>

    2. For every Main Header (H2), use EXACTLY: <h2 style="{H2_STYLE}">
    
    3. For every Paragraph (P), use EXACTLY: <p style="{FONT_STYLE} margin-bottom: 24px;">
    
    4. For Lists (UL/OL), use EXACTLY: <ul style="{FONT_STYLE} margin-bottom: 24px; padding-left: 20px;">
    
    5. For Bold Text, use: <strong style="color: #0f172a;">
    
    6. For Links, use: <a href="#" style="color: #2563eb; text-decoration: underline;">
    
    7. NO <html> or <body> tags. Output only the inner content.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        return clean_html_output(response.choices[0].message.content)
        
    except Exception as e: return f"Error: {e}"

def refine_blog_post(current_html, instructions):
    prompt = f"""
    Expert Editor Task: Edit this HTML.
    INSTRUCTIONS: "{instructions}"
    HTML CONTENT: {current_html}
    
    RULES: 
    1. Keep ALL the inline style="..." attributes exactly as they are. Do not strip them.
    2. Output ONLY HTML.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        return clean_html_output(response.choices[0].message.content)
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
st.title("✍️ Universal Auto-Blogger (Inline Style Fix)")

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
