# music-organizer

A Linux command-line tool for downloading music and syncing a music library.

## Installation

Install Python 3.11 or newer, [uv](https://docs.astral.sh/uv/), and `xdg-user-dirs`. Clone the repository, then run from its directory:

```sh
uv tool install --editable .
uv tool update-shell
touch download.txt
```

Open a new terminal if needed. The editable installation uses `download.txt` and `downloads/` in the project directory; reinstall if you move the project.

## Usage

- `music --download` processes links in `download.txt`, removing each successful link.
- `music --download LINK` downloads one link without changing the queue.
- `music --sync` updates metadata in the system Music folder and reports missing album artwork and artist images. It embeds and removes matching external song artwork.

The sync folder is the Music directory configured by the desktop's XDG user directories (`xdg-user-dir MUSIC`). Change it in your desktop settings or `~/.config/user-dirs.dirs`.

Downloads require `ffmpeg`, Node.js, and Brave browser cookies to be available. `yt-dlp` is installed with the project.
