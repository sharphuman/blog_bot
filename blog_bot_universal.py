import streamlit as st
from openai import OpenAI

# --- CONFIGURATION ---
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# --- AI WRITER ---
def generate_blog_post(topic, persona, key_points, tone):
    prompt = f"""
    IDENTITY & PERSONA:
    {persona}
    
    TASK:
    Write a high-value, authoritative blog post (approx 800-1000 words) about: "{topic}"
    
    TONE: {tone}
    
    CRITICAL DETAILS TO INCLUDE:
    {key_points}
    
    FORMATTING RULES:
    1. Output strictly in HTML format (use <h2>, <h3>, <p>, <ul>, <li>, <strong>).
    2. Do NOT use <html>, <head>, or <body> tags. Start directly with the content.
    3. Include a catchy, SEO-friendly Title in an <h1> tag at the top.
    4. Start with a "Key Takeaways" box (use a <div style="background-color: #f0f4f8; padding: 20px; border-left: 5px solid #007bff; margin-bottom: 20px;"> container).
    5. Use short paragraphs, bullet points, and bold text for readability.
    
    ENDING:
    Conclude with a strong Call to Action relevant to the persona described above.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def generate_seo_meta(content):
    """Generates the Meta Description and SEO Keywords"""
    prompt = f"""
    Read this blog post HTML and generate:
    1. A Meta Description (max 160 chars).
    2. A URL Slug (e.g. topic-name-here).
    3. 5 SEO Keywords.
    
    BLOG CONTENT:
    {content[:3000]}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except: return ""

# --- UI ---
st.set_page_config(page_title="Universal Auto-Blogger", page_icon="✍️", layout="wide")

st.title("✍️ Universal Auto-Blogger")
st.markdown("Define the writer, set the topic, and generate HTML for GoHighLevel.")

with st.form("blog_form"):
    
    # Left Column: The "Who" and "How"
    c1, c2 = st.columns([1, 1])
    
    with c1:
        persona = st.text_area("1. Who is the Writer?", 
            height=100,
            value="You are the Lead Growth Architect at 'Sharp Human'. You are an expert in AI Automation and Revenue Operations. You focus on efficiency, systems, and scaling revenue.",
            help="Tell the AI who to be. e.g. 'Senior Recruiter', 'Python Developer', 'Sales Coach'.")
        
        tone = st.select_slider("2. Tone of Voice", 
            options=["Professional & Corporate", "Direct & Bold", "Empathetic & Storytelling", "Technical & Educational", "Witty & Fast-Paced"], 
            value="Direct & Bold")

    # Right Column: The "What"
    with c2:
        topic = st.text_area("3. Blog Topic / Title", 
            height=68,
            placeholder="e.g. Why candidates ignore calls marked as Spam.")
            
        key_points = st.text_area("4. Specific Details to Cover (Optional)", 
            height=100,
            placeholder="- Mention A2P 10DLC compliance.\n- Tell the story about my client 'John'.\n- Mention that Sharp Human fixes this setup.",
            help="Bullet points of facts, stories, or products you MUST include.")
        
    submitted = st.form_submit_button("Generate Article")

if submitted and topic:
    with st.spinner("Writing your article..."):
        # 1. Write Content
        html_content = generate_blog_post(topic, persona, key_points, tone)
        
        # 2. Generate SEO Data
        seo_data = generate_seo_meta(html_content)
        
        # --- DISPLAY RESULTS ---
        st.success("Article Ready!")
        
        tab1, tab2, tab3 = st.tabs(["📖 Reading Mode", "COPY HTML (For GHL)", "🔍 SEO Data"])
        
        with tab1:
            st.markdown(html_content, unsafe_allow_html=True)
            
        with tab2:
            st.info("Step 1: Copy this code. Step 2: In GHL Blog, click the `< >` icon. Step 3: Paste.")
            st.code(html_content, language="html")
            
        with tab3:
            st.write(seo_data)
