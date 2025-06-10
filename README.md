# Spotify to MP3 Downloader

This project allows you to download and tag songs, albums, or playlists from Spotify as MP3 files. The script fetches metadata from Spotify, searches for the corresponding songs on YouTube Music, and downloads them using `yt-dlp`. Additionally, it tags the MP3 files with the appropriate metadata and album cover art.

## Features

- Download tracks from Spotify playlists, albums, or individual tracks.
- Search and download corresponding tracks from YouTube Music.
- Tag downloaded MP3 files with metadata (title, artist, album, year, track number) and album cover art.
- Concurrent downloads to save time.

## Requirements

- Python 3.7 or higher
- `requests`
- `yt-dlp`
- `mutagen`
- `odesli`

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/josuloo99/Spotify2MP3.git
   cd Spotify2MP3
   ```

2. Install the required packages:
   ```bash
   pip install requests yt-dlp mutagen odesli
   ```

## Usage

1. Set your Spotify and YouTube API credentials:
   ```python
   SPOTIFY_CLIENT_ID = 'your_spotify_client_id'
   SPOTIFY_CLIENT_SECRET = 'your_spotify_client_secret'
   YOUTUBE_API_KEY = 'your_youtube_api_key'
   ```

2. Run the script with the link to a Spotify track, album, or playlist you want to download:
   ```bash
   python main.py <link>
   ```

## How It Works

1. **Spotify Metadata Fetching**: The script fetches metadata for the specified track, album, or playlist using the Spotify API.
2. **YouTube Music Search**: It searches for the corresponding tracks on YouTube Music using the Odesli (Songlink) API and the YouTube Data API.
3. **Download and Tagging**: The script downloads the tracks as MP3 files using `yt-dlp` and tags them with the fetched metadata and album cover art.

## Customization

- **Output Folder**: By default, the downloaded files are saved in the `Downloads` folder. You can change this by updating the `OUTPUT_FOLDER` variable.
- **Max Workers**: Adjust the `MAX_WORKERS` variable to control the number of concurrent downloads.

## Troubleshooting

- Ensure your API keys and client secrets are correct.
- Make sure you have a stable internet connection.
- Check for any errors in the console output for specific issues.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Acknowledgements

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Mutagen](https://mutagen.readthedocs.io/en/latest/)
- [Odesli (Songlink)](https://odesli.co/)
