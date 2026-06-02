import streamlit as st
import yt_dlp
import os
import glob

st.title("🎵 Sandy's RoadTrip MP3 Downloader")
st.write("Paste your YouTube URLs below (one per line) to download them as MP3s.")

# Text area for user input
url_input = st.text_area("YouTube URLs", height=200, placeholder="https://youtube.com/watch?v=...\nhttps://youtu.be/...")

if st.button("Start Download"):
    if not url_input.strip():
        st.error("Please enter at least one URL.")
    else:
        # Split input text into a list of clean URLs
        urls = [url.strip() for url in url_input.split('\n') if url.strip()]
        
        # Temporary directory on the cloud server to store files
        SAVE_PATH = "temp_downloads"
        os.makedirs(SAVE_PATH, exist_ok=True)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(SAVE_PATH, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ignoreerrors': True,
        }
        
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        for idx, url in enumerate(urls):
            status_text.text(f"Processing ({idx+1}/{len(urls)}): {url}")
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                st.warning(f"Failed to download: {url}")
            progress_bar.progress((idx + 1) / len(urls))
            
        status_text.text("Downloads complete! Preparing your files...")
        
        # Find all completed MP3 files
        mp3_files = glob.glob(os.path.join(SAVE_PATH, "*.mp3"))
        
        if mp3_files:
            st.success(f"Successfully processed {len(mp3_files)} files!")
            # Let the user download the files from the browser
            for file_path in mp3_files:
                file_name = os.path.basename(file_path)
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"📥 Download {file_name}",
                        data=f,
                        file_name=file_name,
                        mime="audio/mp3"
                    )
                # Clean up file after giving it to user
                os.remove(file_path)
        else:
            st.error("No MP3s were successfully created.")