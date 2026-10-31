import os
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TCON, ID3NoHeaderError


def process_mp3(mp3_path, genre, artist, album, title):
    base_path_no_ext = os.path.splitext(mp3_path)[0]
    image_path = None
    mime_type = None

    for ext, mime in [(".jpg", "image/jpeg"), (".jpeg", "image/jpeg"), (".png", "image/png")]:
        test_path = base_path_no_ext + ext
        if os.path.exists(test_path):
            image_path = test_path
            mime_type = mime
            break
        elif os.path.exists(base_path_no_ext + ext.upper()):
            image_path = base_path_no_ext + ext.upper()
            mime_type = mime
            break

    try:
        try:
            tags = ID3(mp3_path)
        except ID3NoHeaderError:
            tags = ID3()

        tags.add(TIT2(encoding=3, text=[title]))
        tags.add(TPE1(encoding=3, text=[artist]))
        tags.add(TALB(encoding=3, text=[album]))
        tags.add(TCON(encoding=3, text=[genre]))

        if image_path:
            with open(image_path, 'rb') as img_file:
                cover_data = img_file.read()
            tags.add(APIC(
                encoding=3,
                mime=mime_type,
                type=3,
                desc='Cover',
                data=cover_data
            ))

        tags.save(mp3_path, v2_version=3)

        if image_path:
            try:
                os.remove(image_path)
                print(f"    [-] Embedded and removed external artwork: {os.path.basename(image_path)}")
            except Exception as e:
                print(f"    [!] Warning: Could not delete image file -> {e}")

    except Exception as e:
        print(f"[X] Failed to process {os.path.basename(mp3_path)} -> {e}")

def main(music_root):
    if not os.path.isdir(music_root):
        raise ValueError(f"Music library directory does not exist: {music_root}")

    print(f"[*] Starting metadata sync inside: {music_root}\n")

    missing_artist_image = []
    missing_album_image = []

    for genre in os.listdir(music_root):
        genre_path = os.path.join(music_root, genre)
        if not os.path.isdir(genre_path):
            continue

        for artist in os.listdir(genre_path):
            artist_path = os.path.join(genre_path, artist)
            if not os.path.isdir(artist_path):
                continue

            has_artist_image = any(
                f.lower().startswith("artist.") for f in os.listdir(artist_path)
            )
            if not has_artist_image:
                missing_artist_image.append(artist_path)

            for filename in os.listdir(artist_path):
                if filename.lower().endswith('.mp3'):
                    mp3_path = os.path.join(artist_path, filename)
                    track_title = os.path.splitext(filename)[0]
                    album_name = artist

                    process_mp3(
                        mp3_path=mp3_path,
                        genre=genre,
                        artist=artist,
                        album=album_name,
                        title=track_title
                    )
                    try:
                        tags = ID3(mp3_path)
                        if not tags.getall("APIC"):
                            missing_album_image.append(mp3_path)
                    except Exception:
                        missing_album_image.append(mp3_path)

    print("\n[✓] Music library sync completed.")

    if missing_album_image:
        print(f"\n[!] {len(missing_album_image)} song(s) missing album artwork:")
        for path in sorted(missing_album_image):
            print(f"    {path}")

    if missing_artist_image:
        print(f"\n[!] {len(missing_artist_image)} artist folder(s) missing artist image:")
        for path in sorted(missing_artist_image):
            print(f"    {path}")

