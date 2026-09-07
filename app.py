import streamlit as st
import yt_dlp
import os
import glob
from google import genai

# Expand the page to look more like a professional dashboard
st.set_page_config(page_title="My AI Studio", page_icon="🚀", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🚀 My AI Studio")
st.sidebar.write("Launch a capability and keep the work moving.")
st.sidebar.divider()

# Global API Key input so you only enter it once
api_key = st.sidebar.text_input("Enter Google Gemini API Key:", type="password")

# The Menu Options
page = st.sidebar.radio("Select a Tool:", [
    "🎬 Flow Prompt Bot", 
    "🖼️ Thumbnail Maker", 
    "👤 Character Forge"
])
st.sidebar.divider()
st.sidebar.caption("Powered by Google Gemini")

client = None
if api_key:
    client = genai.Client(api_key=api_key)

# ==========================================
# TOOL 1: FLOW PROMPT BOT
# ==========================================
if page == "🎬 Flow Prompt Bot":
    st.title("🎬 Flow Prompt Bot")
    st.write("Convert scripts or videos into production-ready Google Flow scenes.")
    
    # Text fallback added to bypass YouTube 403 Server Blocks
    input_method = st.radio("Input Method (Use Script if YouTube blocks the link):", ["Paste Script/Text", "YouTube URL"])
    aspect_ratio = st.radio("Format:", ["Vertical (9:16)", "Horizontal (16:9)"])
    
    if input_method == "Paste Script/Text":
        user_data = st.text_area("Paste your script or dialogue here:", height=150)
    else:
        user_data = st.text_input("Paste YouTube URL:")

    if st.button("Generate Scenes"):
        if not api_key or not user_data:
            st.warning("Please provide your API key in the sidebar and enter your script/URL.")
            st.stop()
            
        with st.spinner("Processing..."):
            try:
                orientation = "Vertical 9:16" if "Vertical" in aspect_ratio else "Horizontal 16:9"
                prompt = f"""
                Break the following content into ~10-second scenes for a video generator.
                Format EVERY scene EXACTLY like this example:
                
                {orientation}, 10-second realistic cinematic drama with native audio, no subtitles or on-screen text.
                Setting: [Details]
                Characters: [Details]
                Cinematography: [Details]
                Action: [Details]
                Audio: [Character Name: "Exact spoken words."]
                Style: Realistic cinematic drama, quiet urgency, no text, no subtitles.
                """
                
                if input_method == "YouTube URL":
                    ydl_opts = {
                        'format': 'm4a/bestaudio/best',
                        'outtmpl': 'audio.%(ext)s',
                        'quiet': True,
                        'extractor_args': {'youtube': {'player_client': ['android']}}
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([user_data])
                    audio_path = glob.glob("audio.*")[0]
                    uploaded_file = client.files.upload(file=audio_path)
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[uploaded_file, prompt]
                    )
                    os.remove(audio_path)
                else:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[prompt, "\n\nContent to process:\n" + user_data]
                    )
                    
                st.success("Done!")
                st.code(response.text, language="text")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# ==========================================
# TOOL 2: THUMBNAIL MAKER
# ==========================================
elif page == "🖼️ Thumbnail Maker":
    st.title("🖼️ Thumbnail Maker")
    st.write("Generate high-converting image prompts for YouTube thumbnails.")
    
    video_topic = st.text_input("What is your video about?")
    
    if st.button("Generate Thumbnail Concepts"):
        if not api_key or not video_topic:
            st.warning("Please provide your API key and a video topic.")
            st.stop()
            
        with st.spinner("Brainstorming..."):
            prompt = f"Create 3 highly visual, click-worthy Midjourney image prompts for a YouTube thumbnail about: {video_topic}. Describe the core subject, background, and lighting."
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            st.write(response.text)

# ==========================================
# TOOL 3: CHARACTER FORGE
# ==========================================
elif page == "👤 Character Forge":
    st.title("👤 Character Forge")
    st.write("Design consistent character profiles for AI generation.")
    
    char_desc = st.text_area("Describe your character briefly:")
    
    if st.button("Forge Character"):
        if not api_key or not char_desc:
            st.warning("Please provide your API key and a description.")
            st.stop()
            
        with st.spinner("Designing..."):
            prompt = f"Expand this brief description into a comprehensive AI image generation prompt for a character turnaround sheet (front, side, and back profile). Description: {char_desc}"
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            st.write(response.text)
