import yt_dlp

def get_video_info(url):
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info

def select_format(formats):
    # Filter only progressive formats (video + audio)
    progressive_formats = [
        f for f in formats 
        if f.get('acodec') != 'none' 
        and f.get('vcodec') != 'none'
    ]

    # Create dictionary of best quality for each resolution/format combo
    format_options = {}
    for f in progressive_formats:
        key = (f.get('resolution', 'Unknown'), f.get('ext', 'Unknown'))
        if key not in format_options or f.get('tbr', 0) > format_options[key].get('tbr', 0):
            format_options[key] = f

    if not format_options:
        print("No progressive formats available!")
        return None

    # Display available options
    print("\nAvailable formats:")
    sorted_formats = sorted(
        format_options.items(),
        key=lambda x: (
            -int(x[0][0].replace('p', '')) if x[0][0].endswith('p') else 0,
            x[0][1]
        )
    )
    
    for i, ((res, ext), fmt) in enumerate(sorted_formats, 1):
        print(f"{i}. {res} ({ext.upper()}) - {fmt.get('format_note', '')}")

    # Let user select
    while True:
        try:
            choice = int(input("\nEnter format number: "))
            if 1 <= choice <= len(sorted_formats):
                selected_format = sorted_formats[choice-1][1]
                return selected_format['format_id']
            print("Invalid number! Try again.")
        except ValueError:
            print("Please enter a valid number!")

def download_video():
    url = input("Enter YouTube URL: ")
    
    try:
        # Get video info
        video_info = get_video_info(url)
        print(f"\nTitle: {video_info['title']}")
        
        # Select format
        format_id = select_format(video_info['formats'])
        if not format_id:
            return

        # Download options
        ydl_opts = {
            'format': format_id,
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'progress_hooks': [lambda d: print("\rDownloading...", end='')],
        }

        # Start download
        print()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        print("\nDownload complete!")

    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    download_video()
