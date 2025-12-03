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

# --- STYLING CONSTANTS (The Safety Net) ---
# We force this wrapper onto EVERY blog post, no matter what the AI does.
# This ensures it is always White Background with Dark Text.
BLOG_WRAPPER_START = """
<div style="background-color: #ffffff; color: #333333; font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; padding: 20px; border-radius: 8px;">
"""
BLOG_WRAPPER_END = "</div>"

# --- HELPER: CLEANER ---
def clean_and_wrap_html(text):
    """
    1. Strips markdown backticks.
    2. Removes any existing wrappers (to prevent duplicates).
    3. Re-applies the master White Background wrapper.
    """
    # Strip Markdown
    text = text.replace("```html", "").replace("```", "").strip()
    
    # Strip previous wrappers if they exist (cleanup)
    text = text.replace(BLOG_WRAPPER_START.strip(), "")
    text = text.replace(BLOG_WRAPPER_END.strip(), "")
    
    # Return wrapped content
    return f"{BLOG_WRAPPER_START}\n{text}\n{BLOG_WRAPPER_END}"

# --- AI WRITER ---
def generate_blog_post(topic, persona, key_points, tone):
    
    # Specific style for the Takeaways box to ensure visibility
    takeaway_box_style = 'background-color: #f0f4f8; border-left: 5px solid #007bff; padding: 15px; margin-bottom: 25px; color: #000000;'
    
    prompt = f"""
    IDENTITY: {persona}
    TONE: {tone}
    TOPIC: "{topic}"
    DETAILS: {key_points}
    
    TASK: Write the inner HTML content for a blog post.
    
    FORMATTING RULES:
    1. Start immediately with a Key Takeaways box using this div: <div style="{takeaway_box_style}">
    2. Inside that box, use <h3>Key Takeaways</h3> and <ul>. Ensure text is Black.
    3. After the box, use <h2> for main headers.
    4. Use <p> for paragraphs.
    5. DO NOT use <html>, <head>, <body>, or main wrapper divs.
    6. NO markdown backticks.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        # We wrap it in Python to guarantee the style sticks
        return clean_and_wrap_html(response.choices[0].message.content)
        
    except Exception as e: return f"Error: {e}"

def refine_blog_post(current_html, instructions):
    # Strip wrapper before sending to AI (so it only edits text)
    core_text = current_html.replace(BLOG_WRAPPER_START, "").replace(BLOG_WRAPPER_END, "")
    
    prompt = f"""
    You are an Expert Editor. Edit this HTML content based on instructions.
    
    USER INSTRUCTIONS: "{instructions}"
    CURRENT HTML CONTENT:
    {core_text}
    
    RULES: 
    1. Output ONLY valid HTML. 
    2. Keep the formatting tags (h2, ul, div style=...). 
    3. Do NOT add markdown backticks.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        # Re-wrap the result
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
st.title("✍️ Universal Auto-Blogger (Safe Mode)")

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
        # This preview will now show the white box correctly
        st.markdown(st.session_state.blog_content, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 Final Code")
        st.info("Click the copy button in the top-right of the box below.")
        
        # Using st.code provides a built-in one-click COPY button
        st.code(st.session_state.blog_content, language="html")
