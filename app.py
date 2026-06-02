import streamlit as st
import yt_dlp
import os
import glob

st.title("🎵 Universal MP3 Downloader")
st.write("Download individual tracks or entire playlists directly to MP3.")

# Create two tabs for separate download modes
tab1, tab2 = st.tabs(["🎥 Single Videos / Links", "🎼 Entire Playlist"])

# Directory configuration
SAVE_PATH = "temp_downloads"

# Core yt-dlp downloader helper function
def run_ytdl_download(urls, is_playlist=False):
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
    
    # If downloading a full playlist link, let yt-dlp manage the recursion natively
    if is_playlist:
        ydl_opts['noplaylist'] = False
    else:
        ydl_opts['noplaylist'] = True

    status_text = st.empty()
    progress_bar = st.progress(0)
    
    total_items = len(urls)
    for idx, url in enumerate(urls):
        status_text.text(f"Processing ({idx+1}/{total_items}): {url}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            st.warning(f"Failed to process URL: {url}")
        progress_bar.progress((idx + 1) / total_items)
        
    status_text.text("Extraction complete! Aggregating files...")
    
    # Locate generated MP3 tracks
    mp3_files = glob.glob(os.path.join(SAVE_PATH, "*.mp3"))
    
    if mp3_files:
        st.success(f"Successfully processed audio tracks!")
        for file_path in mp3_files:
            file_name = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"📥 Download {file_name}",
                    data=f,
                    file_name=file_name,
                    mime="audio/mp3",
                    key=file_name # Unique key tracking for Streamlit loops
                )
            # Delete file locally on server after browser attachment to maintain disc space
            os.remove(file_path)
    else:
        st.error("No valid MP3 files could be extracted.")

# --- TAB 1: SINGLE VIDEOS ---
with tab1:
    st.subheader("Download Individual Videos")
    single_input = st.text_area(
        "Paste video URLs (one per line):", 
        height=150, 
        placeholder="https://www.youtube.com/watch?v=...\nhttps://youtu.be/..."
    )
    
    if st.button("Download Videos", key="btn_single"):
        if not single_input.strip():
            st.error("Please enter at least one video URL.")
        else:
            video_list = [url.strip() for url in single_input.split('\n') if url.strip()]
            run_ytdl_download(video_list, is_playlist=False)

# --- TAB 2: PLAYLIST DOWNLOAD ---
with tab2:
    st.subheader("Download Full Playlist")
    playlist_input = st.text_input(
        "Paste the YouTube Playlist URL:", 
        placeholder="https://www.youtube.com/playlist?list=..."
    )
    
    if st.button("Extract Playlist", key="btn_playlist"):
        if not playlist_input.strip():
            st.error("Please provide a valid playlist URL.")
        else:
            # We treat the single playlist URL as an item in an array, 
            # but mark is_playlist=True so yt-dlp parses the internal items.
            run_ytdl_download([playlist_input.strip()], is_playlist=True)