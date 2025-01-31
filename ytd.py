import yt_dlp

def download_video():
    url = input("Enter YouTube URL: ")
    
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': False,
        'no_warnings': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download complete!")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    download_video()
