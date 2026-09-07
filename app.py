import streamlit as st
import yt_dlp
import os
from google import genai

st.set_page_config(page_title="Flow Bot", page_icon="🎬")
st.title("🎬 My Google Flow Bot")

api_key = st.text_input("Enter your Google Gemini API Key:", type="password")
input_url = st.text_input("Paste YouTube / TikTok URL:")
aspect_ratio = st.radio("Format:", ["Vertical (9:16)", "Horizontal (16:9)"])

if st.button("Generate Scenes"):
    if not api_key or not input_url:
        st.warning("Please add your key and a URL.")
        st.stop()
        
    client = genai.Client(api_key=api_key)
    
    with st.spinner("Downloading audio and writing scenes... this takes a minute!"):
        # Download Audio
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'audio.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([input_url])
            
        # Send to Free Gemini AI
        orientation = "Vertical 9:16" if "Vertical" in aspect_ratio else "Horizontal 16:9"
        prompt = f"""
        Listen to this audio. Break the script into ~10-second scenes for a video generator.
        Format EVERY scene EXACTLY like this example. 
        
        {orientation}, 10-second realistic cinematic drama with native audio, no subtitles or on-screen text.
        
        Setting:
        [Details of the environment]
        
        Characters:
        [Detailed physical descriptions]
        
        Cinematography:
        [Camera angles, movement]
        
        Action:
        [Physical actions]
        
        Audio:
        [Character Name (voiceover/dialogue, emotion): "Exact spoken words."]
        
        Style:
        Realistic cinematic drama, quiet urgency, no text, no subtitles.
        """
        
        audio_file = client.files.upload(file="audio.mp3")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[audio_file, prompt]
        )
        
        st.success("Done!")
        st.code(response.text, language="text")
        os.remove("audio.mp3")
