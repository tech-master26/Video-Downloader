import os
import re
import yt_dlp
from functools import cmp_to_key

# ANSI Color Codes
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[38;2;0;255;0m"
COLOR_CYAN = "\033[38;2;0;255;255m"
COLOR_YELLOW = "\033[38;2;255;255;0m"
COLOR_PINK = "\033[38;2;255;20;147m"

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    banner = rf"""
{COLOR_CYAN}
  ██████╗  ██████╗ ██╗    ██╗███╗   ██╗██╗      ██████╗  █████╗ ██████╗ 
  ██╔══██╗██╔═══██╗██║    ██║████╗  ██║██║     ██╔═══██╗██╔══██╗██╔══██╗
  ██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║██║     ██║   ██║███████║██║  ██║
  ██║  ██║██║   ██║██║███╗██║██║╚██╗██║██║     ██║   ██║██╔══██║██║  ██║
  ██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║███████╗╚██████╔╝██║  ██║██████╔╝
  ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ 
{COLOR_PINK}
Supporting YouTube, TikTok, Instagram & Facebook
{COLOR_RESET}
"""
    print(banner)

def detect_platform(url):
    """Detect the platform from the URL"""
    domain = re.search(r'(https?://(?:www\.)?([^/]+))', url)
    if domain:
        domain = domain.group(2).lower()
        if 'youtube' in domain or 'youtu.be' in domain:
            return 'youtube'
        elif 'tiktok' in domain:
            return 'tiktok'
        elif 'instagram' in domain:
            return 'instagram'
        elif 'facebook' in domain:
            return 'facebook'
    return 'unknown'

def get_color_gradient(index, total):
    """Generate gradient from green (high) to red (low)"""
    if total == 1:
        return COLOR_GREEN
    
    ratio = index / (total - 1)
    r = int(255 * ratio)
    g = int(255 * (1 - ratio))
    return f"\033[38;2;{r};{g};0m"

def get_video_info(url):
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def select_format(formats, platform):
    # Bypass format selection for Facebook
    if platform == 'facebook':
        return 'best'

    # Filter valid formats based on platform
    if platform == 'instagram':
        formats = [f for f in formats if f.get('vcodec') != 'none']
    else:
        formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') != 'none']
    
    # Handle empty formats
    if not formats:
        return 'best'

    # Sort by resolution and bitrate with None safety
    def compare(a, b):
        a_res = int(a.get('height', 0)) if a.get('height') else 0
        b_res = int(b.get('height', 0)) if b.get('height') else 0
        return (b_res - a_res) or (b.get('tbr', 0) - a.get('tbr', 0))
    
    try:
        formats.sort(key=cmp_to_key(compare))
    except:
        return 'best'

    # Remove duplicate resolutions
    seen = set()
    unique_formats = []
    for f in formats:
        res = f.get('height') or f.get('format_note', 'Unknown')
        if res not in seen:
            seen.add(res)
            unique_formats.append(f)

    # If only one format available, auto-select
    if len(unique_formats) == 1:
        return unique_formats[0]['format_id']

    # Display options with color gradient
    print(f"\n{COLOR_YELLOW}Available Formats:{COLOR_RESET}")
    for i, fmt in enumerate(unique_formats, 1):
        color = get_color_gradient(i-1, len(unique_formats))
        ext = fmt.get('ext', 'mp4').upper()
        res = fmt.get('height', 'Unknown')
        fps = fmt.get('fps', 0)
        
        res_display = f"{res}p" if isinstance(res, int) else res
        fps_display = f"({fps}fps)" if fps else ""
        
        print(f"{color}[{i}] {res_display} {ext} {fps_display}{COLOR_RESET}")

    # Get user selection
    while True:
        try:
            choice = input(f"\n{COLOR_GREEN}Enter format number (or Enter for best): {COLOR_RESET}").strip()
            if not choice:
                return 'best'
            choice = int(choice)
            if 1 <= choice <= len(unique_formats):
                return unique_formats[choice-1]['format_id']
            print("Invalid number! Try again.")
        except ValueError:
            print("Please enter a valid number!")

def rename_file(download_dir):
    files = [f for f in os.listdir(download_dir) if os.path.isfile(os.path.join(download_dir, f))]
    if not files:
        print("No files found to rename!")
        return
    
    latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(download_dir, f)))
    print(f"\nCurrent filename: {COLOR_CYAN}{latest_file}{COLOR_RESET}")
    
    new_name = input("Enter new filename (with extension): ").strip()
    if new_name:
        os.rename(
            os.path.join(download_dir, latest_file),
            os.path.join(download_dir, new_name)
        )
        print(f"File renamed to {COLOR_GREEN}{new_name}{COLOR_RESET}")

def choose_download_dir():
    default_dir = 'downloads'
    print(f"\n{COLOR_CYAN}Choose download directory:{COLOR_RESET}")
    print(f"[1] Default directory ({default_dir})")
    print("[2] Custom directory")
    
    while True:
        choice = input(f"{COLOR_GREEN}Enter choice (1/2): {COLOR_RESET}").strip()
        if choice == '1':
            return default_dir
        elif choice == '2':
            custom_dir = input("Enter custom directory path: ").strip()
            if os.path.isdir(custom_dir):
                return custom_dir
            print(f"{COLOR_YELLOW}Directory doesn't exist! Creating...{COLOR_RESET}")
            os.makedirs(custom_dir, exist_ok=True)
            return custom_dir
        print("Invalid choice! Try again.")

def download_video():
    clear_screen()
    print_banner()
    
    try:
        # Get URL and detect platform
        url = input(f"{COLOR_GREEN}Enter Video URL: {COLOR_RESET}").strip()
        platform = detect_platform(url)
        
        if platform == 'unknown':
            print(f"{COLOR_YELLOW}Unsupported platform!{COLOR_RESET}")
            return

        # Get video info
        video_info = get_video_info(url)
        print(f"\n{COLOR_CYAN}Title:{COLOR_RESET} {video_info['title']}")
        
        # Select download directory
        download_dir = choose_download_dir()
        os.makedirs(download_dir, exist_ok=True)

        # Handle Facebook specially
        if platform == 'facebook':
            format_id = 'best'
            print(f"{COLOR_YELLOW}Facebook: Using best available format{COLOR_RESET}")
        else:
            format_id = select_format(video_info['formats'], platform)

        # Download configuration
        ydl_opts = {
            'format': format_id,
            'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
            'progress_hooks': [lambda d: print(f"\r{COLOR_YELLOW}Downloading... {d.get('_percent_str', '')}{COLOR_RESET}", end='')],
        }

        # Platform-specific adjustments
        if platform == 'facebook':
            ydl_opts.update({
                'format': 'best',
                'cookiefile': 'facebook.com_cookies.txt' if os.path.exists('facebook.com_cookies.txt') else None
            })

        # Start download
        print()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Rename prompt
        if input(f"\n{COLOR_GREEN}Rename file? (y/n): {COLOR_RESET}").lower() == 'y':
            rename_file(download_dir)
        
        print(f"\n{COLOR_GREEN}Download complete!{COLOR_RESET}")

    except Exception as e:
        print(f"\n{COLOR_YELLOW}Error: {str(e)}{COLOR_RESET}")

def main_loop():
    while True:
        download_video()
        
        # Ask to continue
        choice = input(f"\n{COLOR_CYAN}Download another video? (y/n): {COLOR_RESET}").lower()
        if choice != 'y':
            print(f"{COLOR_PINK}Thank you for using the video downloader!{COLOR_RESET}")
            break
        
        # Clear screen for next download
        clear_screen()

if __name__ == "__main__":
    main_loop()
