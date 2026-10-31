import os
import glob
import time
import subprocess
import shutil
import sys
from mutagen.id3 import ID3, APIC, TIT2, error
from PIL import Image


def sanitize_filename(name):
    """Replace filesystem-illegal characters with an underscore."""
    if not name:
        return name
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        name = name.replace(char, '_')
    return name.strip()

BROWSER = "brave"
JS_RUNTIME = "node"
PLAYER_CLIENTS = ["web", "android"]
MAX_RETRIES = 3
YT_DLP = shutil.which("yt-dlp") or os.path.join(os.path.dirname(sys.executable), "yt-dlp")

def get_video_info(url):
    """
    Fetches both the safe title and the channel name from the URL using yt-dlp.
    Returns a tuple: (title, channel_name)
    """
    cmd = [
        YT_DLP,
        "--cookies-from-browser", BROWSER,
        "--js-runtime", JS_RUNTIME,
        "--print", "%(title)s ||| %(uploader)s",
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if result.returncode == 0 and result.stdout.strip():
        parts = result.stdout.strip().split(" ||| ")
        if len(parts) == 2:
            title = sanitize_filename(parts[0].strip())
            channel = sanitize_filename(parts[1].strip())
            return title, channel

    return sanitize_filename(f"video_{int(time.time())}"), "Unknown_Channel"

def download_video(url, title, channel, download_root):
    target_dir = os.path.join(download_root, title)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    if channel:
        channel_file_path = os.path.join(target_dir, channel)
        try:
            with open(channel_file_path, 'w', encoding='utf-8') as f:
                pass
            print(f"[+] Created channel marker file: {channel}")
        except Exception as e:
            print(f"[!] Warning: Could not create channel marker file: {e}")

    outtmpl = os.path.join(target_dir, f"{title}.%(ext)s")
    chapter_outtmpl = f"chapter:{os.path.join(target_dir, '%(section_title)s.%(ext)s')}"

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[*] Download attempt {attempt} of {MAX_RETRIES}...")

        client_arg = ",".join(PLAYER_CLIENTS)

        cmd = [
            YT_DLP,
            "--cookies-from-browser", BROWSER,
            "--js-runtime", JS_RUNTIME,
            "--extractor-args", f"youtube:player_client={client_arg};remote_ejs=github",
            "--format", "bestaudio/best",
            "--no-match-filter",
            "--extract-audio", "--audio-format", "mp3", "--audio-quality", "320K",
            "--write-thumbnail",
            "--convert-thumbnails", "jpg",
            "--split-chapters",
            "--output", outtmpl,
            "--output", chapter_outtmpl,
            "--no-mtime",
            url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            return target_dir
        else:
            print(f"[!] Attempt {attempt} failed: {result.stderr.strip()}")
            if attempt < MAX_RETRIES:
                time.sleep(3)

    raise Exception("All download retries exhausted.")

def process_thumbnail(folder_path, title):
    expected_thumb = os.path.join(folder_path, f"{title}.jpg")
    target_thumb = os.path.join(folder_path, "thumb.jpg")

    if not os.path.exists(expected_thumb):
        jpg_files = glob.glob(os.path.join(folder_path, "*.jpg"))
        if jpg_files:
            expected_thumb = jpg_files[0]
        else:
            print("[-] No thumbnail image found to process.")
            return None

    try:
        with Image.open(expected_thumb) as img:
            width, height = img.size
            left = (width - height) // 2
            right = left + height
            top = 0
            bottom = height
            cropped = img.crop((left, top, right, bottom))
            cropped.save(target_thumb, "JPEG")

        if os.path.abspath(expected_thumb) != os.path.abspath(target_thumb):
            os.remove(expected_thumb)

        return target_thumb
    except Exception as e:
        print(f"[!] Thumbnail cropping error: {e}")
        return None

def apply_metadata(folder_path, thumb_path):
    time.sleep(1)
    mp3_files = glob.glob(os.path.join(folder_path, "*.mp3"))

    cover_data = None
    if thumb_path and os.path.exists(thumb_path):
        with open(thumb_path, 'rb') as f:
            cover_data = f.read()

    for mp3_path in mp3_files:
        try:
            filename = os.path.basename(mp3_path)
            track_title = filename.replace('.mp3', '')

            try:
                tags = ID3(mp3_path)
            except error:
                tags = ID3()

            tags.delete(mp3_path)
            tags.add(TIT2(encoding=3, text=[track_title]))

            if cover_data:
                tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=cover_data))

            tags.save(mp3_path, v2_version=3)
            print(f"[+] Successfully metadata-tagged: {filename}")
        except Exception as e:
            print(f"[!] Metadata application error on {os.path.basename(mp3_path)}: {e}")

def main(project_root, url=None):
    links_file = os.path.join(project_root, "download.txt")
    download_root = os.path.join(project_root, "downloads")

    if url is not None:
        print(f"\n--- 🎵 Processing Target Link: {url} ---")
        title, channel = get_video_info(url)
        print(f"[*] Parsed Title: {title}")
        print(f"[*] Parsed Channel: {channel}")
        folder_path = download_video(url, title, channel, download_root)
        thumb_path = process_thumbnail(folder_path, title)
        apply_metadata(folder_path, thumb_path)
        print(f"[✓] Finished Process: {title}")
        return

    if not os.path.exists(links_file) or os.path.getsize(links_file) == 0:
        print("[-] download.txt is empty or missing.")
        return

    with open(links_file, 'r', encoding='utf-8') as f:
        links = [line.strip() for line in f if line.strip()]

    if not links:
        print("[-] No actionable URLs found inside download.txt.")
        return

    remaining_links = list(links)

    for current_url in links:
        print(f"\n--- 🎵 Processing Target Link: {current_url} ---")

        try:
            title, channel = get_video_info(current_url)
            print(f"[*] Parsed Title: {title}")
            print(f"[*] Parsed Channel: {channel}")

            folder_path = download_video(current_url, title, channel, download_root)
            thumb_path = process_thumbnail(folder_path, title)
            apply_metadata(folder_path, thumb_path)
            
            remaining_links.remove(current_url)
            with open(links_file, 'w', encoding='utf-8') as f:
                for remaining_link in remaining_links:
                    f.write(f"{remaining_link}\n")

            print(f"[✓] Finished Process: '{title}' removed from queue.")

        except Exception as e:
            print(f"\n[X] Fatal failure on handling {current_url} -> {e}")
            print("[*] Skipping to next link...")
            continue

    print("\n[✓] All links inside download.txt have been processed.")

if __name__ == "__main__":
    main(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
