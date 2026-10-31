![music-organizer](https://capsule-render.vercel.app/api?type=rect&color=374151&height=180&text=music-organizer&fontSize=60&fontColor=ffffff)

![version](https://img.shields.io/badge/version-0.1.0-b07b8d.svg?style=flat-square&labelColor=374151)

A Linux command-line tool for downloading music and syncing a music library.

## Installation

Install Python 3.11 or newer, [uv](https://docs.astral.sh/uv/), and `xdg-user-dirs`. Clone the repository, then run from its directory:

```sh
uv tool install --editable .
uv tool update-shell
touch download.txt
```

## Usage

- `music --download` processes links in `download.txt`, removing each successful link.
- `music --download LINK` downloads one link without changing the queue.
- `music --sync` updates metadata in the system Music folder and reports missing album artwork and artist images. It embeds and removes matching external song artwork.

The sync folder is the Music directory configured by the desktop's XDG user directories (`xdg-user-dir MUSIC`). Change it in your desktop settings or `~/.config/user-dirs.dirs`.

## Music organization

Organize the Music folder by genre, with artist folders containing their songs:

```text
Music/
└── Genre/
    └── Artist/
        ├── artist.jpg
        └── Song.mp3
```

Sync uses the folder and file names for genre, artist, album, and song metadata. The artist name is also used as the album name.

Downloads require `ffmpeg`, Node.js, and Brave browser cookies to be available. `yt-dlp` is installed with the project.
