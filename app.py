import streamlit as st
import yt_dlp
import os
import glob



st.title("🎵 Universal MP3 Downloader")

# 1. Initialize persistent memory architecture across server reruns
if 'downloaded_tracks' not in st.session_state:
    st.session_state.downloaded_tracks = []

SAVE_PATH = "temp_downloads"

def run_ytdl_download(urls, is_playlist=False):
    os.makedirs(SAVE_PATH, exist_ok=True)
    
    ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(SAVE_PATH, '%(title)s.%(ext)s'),
    'cookiefile': 'cookies.txt', 
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'ignoreerrors': True,
}
    ydl_opts['noplaylist'] = not is_playlist

    status_text = st.empty()
    progress_bar = st.progress(0)
    
    # Clear memory storage before a fresh download run
    st.session_state.downloaded_tracks = []
    
    total_items = len(urls)
    for idx, url in enumerate(urls):
        status_text.text(f"Processing ({idx+1}/{total_items}): {url}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            st.warning(f"Failed to process: {url}")
        progress_bar.progress((idx + 1) / total_items)
        
    status_text.text("Extraction phase complete! Verifying files...")
    
    # Find files and save directly to persistent memory
    found_files = glob.glob(os.path.join(SAVE_PATH, "*.mp3"))
    st.session_state.downloaded_tracks = found_files

# --- UI TABS ---
tab1, tab2 = st.tabs(["🎥 Single Videos", "🎼 Entire Playlist"])

with tab1:
    single_input = st.text_area("Paste video URLs (one per line):", key="single_url_box")
    if st.button("Download Videos"):
        video_list = [url.strip() for url in single_input.split('\n') if url.strip()]
        if video_list:
            run_ytdl_download(video_list, is_playlist=False)
        else:
            st.error("Please enter a link.")

with tab2:
    playlist_input = st.text_input("Paste the YouTube Playlist URL:", key="playlist_url_box")
    if st.button("Extract Playlist"):
        if playlist_input.strip():
            run_ytdl_download([playlist_input.strip()], is_playlist=True)
        else:
            st.error("Please enter a playlist link.")

# --- RENDER DOWNLOAD BUTTONS FROM STATE MEMORY ---
# This block stays visible even during button clicks/reruns!
if st.session_state.downloaded_tracks:
    st.success("Tracks ready for local acquisition!")
    for file_path in st.session_state.downloaded_tracks:
        if os.path.exists(file_path): # Verify file didn't disappear
            file_name = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"📥 Download {file_name}",
                    data=f,
                    file_name=file_name,
                    mime="audio/mp3",
                    key=f"dl_{file_name}"
                )