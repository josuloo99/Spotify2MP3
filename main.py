import requests
import base64
import os
from dotenv import load_dotenv
from yt_dlp import YoutubeDL
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3
from odesli.Odesli import Odesli
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
OUTPUT_FOLDER = 'Downloads'
MAX_WORKERS = 3  # Adjust as needed

def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    response = requests.post(auth_url, headers=headers, data=data)
    response_data = response.json()
    return response_data['access_token']

def get_spotify_info(link, client_id, client_secret):
    token = get_spotify_token(client_id, client_secret)
    headers = {'Authorization': f'Bearer {token}'}

    item_type = ''
    if 'track' in link:
        item_type = 'track'
    elif 'album' in link:
        item_type = 'album'
    elif 'playlist' in link:
        item_type = 'playlist'
    else:
        raise ValueError("Invalid Spotify link. The link must be for a track, an album, or a playlist.")

    item_id = link.split('/')[-1].split('?')[0]
    url = f'https://api.spotify.com/v1/{item_type}s/{item_id}'

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Spotify API request failed with status code {response.status_code}")

    data = response.json()
    if 'error' in data:
        raise ValueError(f"Error from Spotify API: {data['error']['message']}")

    if item_type == 'track':
        song_info = {
            'Song name': data['name'],
            'Artists name': ', '.join(artist['name'] for artist in data['artists']),
            'Album name': data['album']['name'],
            'Year': data['album']['release_date'][:4],
            'Track number': data['track_number'],
            'Cover picture link': data['album']['images'][0]['url'],
            'Track URL': data['external_urls']['spotify']
        }
        return [song_info], None
    elif item_type == 'album':
        album_info = {
            'Album name': data['name'],
            'Artists name': ', '.join(artist['name'] for artist in data['artists']),
            'Year': data['release_date'][:4],
            'Cover picture link': data['images'][0]['url']
        }
        tracks_info = []
        for track in data['tracks']['items']:
            track_info = {
                'Song name': track['name'],
                'Artists name': ', '.join(artist['name'] for artist in track['artists']),
                'Album name': album_info['Album name'],
                'Year': album_info['Year'],
                'Track number': track['track_number'],
                'Cover picture link': album_info['Cover picture link'],
                'Track URL': track['external_urls']['spotify']
            }
            tracks_info.append(track_info)
        return tracks_info, album_info['Album name']
    elif item_type == 'playlist':
        playlist_name = data['name']
        tracks_info = []
        track_number = 1
        for item in data['tracks']['items']:
            track = item['track']
            track_info = {
                'Song name': track['name'],
                'Artists name': ', '.join(artist['name'] for artist in track['artists']),
                'Album name': track['album']['name'],
                'Year': track['album']['release_date'][:4],
                'Track number': track_number,
                'Cover picture link': track['album']['images'][0]['url'],
                'Track URL': track['external_urls']['spotify']
            }
            tracks_info.append(track_info)
            track_number += 1
        return tracks_info, playlist_name

def get_direct_link(link):
    odesli = Odesli()
    ytmusic_link = ''

    try:
        result = odesli.getByUrl(link)
        ytmusic_link = result.songsByProvider['youtube'].linksByPlatform['youtubeMusic']
    except Exception as e:
        print("URL not found in YTMusic. Error details: " + str(e))

    return ytmusic_link

def search_youtube_music(track_name, artist_name):
    if YOUTUBE_API_KEY:
        search_url = "https://www.googleapis.com/youtube/v3/search"
        query = f"{track_name} {artist_name}"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'key': YOUTUBE_API_KEY
        }
        response = requests.get(search_url, params=params)
        results = response.json().get('items', [])
        if results:
            return f"https://www.youtube.com/watch?v={results[0]['id']['videoId']}"

    return None

def get_ytmusic_link(track):
    base_link = track['Track URL']
    if not base_link:
        print(f"No URL available for {track['Song name']}. Skipping...")
        return
    ytmusic_link = get_direct_link(base_link)

    if not ytmusic_link:
        ytmusic_link = search_youtube_music(track['Song name'], track['Artists name'])

    return ytmusic_link

def correct_conflictive_characters(name: str):
    if name:
        if name.endswith('.') or name.endswith(','):
            name = name[:-1]

        name = name.replace(':','_')
    else:
        name =''
    return name

def download_and_tag_track(track, output_folder):
    file_path = os.path.join(
        output_folder,
        correct_conflictive_characters(
            f"{track['Track number']:02d}. {track['Artists name']} - {track['Song name']}"))

    if not os.path.exists(file_path + '.mp3'):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': file_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }

        ytmusic_url = get_ytmusic_link(track)
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([ytmusic_url])

        file_path = file_path + '.mp3'
        try:
            audio = EasyID3(file_path)
        except Exception:
            audio = MP3(file_path, ID3=ID3)
            audio.add_tags()
            audio = EasyID3(file_path)

        audio['title'] = track['Song name']
        audio['artist'] = track['Artists name']
        audio['album'] = track['Album name']
        audio['date'] = track['Year']
        audio['tracknumber'] = str(track['Track number'])
        audio.save()

        cover_url = track['Cover picture link']
        cover_data = requests.get(cover_url).content
        audio = MP3(file_path, ID3=ID3)
        audio.tags.add(
            APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc=u'Cover',
                data=cover_data
            )
        )
        audio.save()
        print(f"{file_path} downloaded correctly!")
    else:
        print(f"{file_path} already exists!")

def download_and_tag_tracks(tracks_info, folder_name):
    output_folder = os.path.join(OUTPUT_FOLDER, correct_conflictive_characters(folder_name))
    os.makedirs(output_folder, exist_ok=True)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(download_and_tag_track, track, output_folder) for track in tracks_info]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python main.py <spotify_link>")
        sys.exit(1)

    link = sys.argv[1]

    try:
        tracks_info, folder_name = get_spotify_info(link, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        download_and_tag_tracks(tracks_info, folder_name)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
