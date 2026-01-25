# 🎵 Spotify API Integration Setup Guide

## Overview

The system now includes full Spotify integration for:
- **Track Search** - Find songs by name, artist, or keywords
- **Artist Search** - Discover artists and their information
- **Playlist Search** - Find curated playlists
- **Recommendations** - Get personalized track suggestions
- **Audio Features** - Analyze track characteristics (energy, danceability, etc.)
- **Genre Browsing** - Access all available Spotify genres

## Prerequisites

1. Python 3.8+
2. spotipy library (included in requirements.txt)
3. Spotify Developer Account
4. Spotify API Credentials

## Step 1: Get Spotify API Credentials

### 1.1 Create a Developer Account

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Login or create a free account
3. Accept the terms and create your developer application

### 1.2 Get Your Credentials

1. In the dashboard, click "Create an App"
2. Fill in the app name and accept the terms
3. You'll receive:
   - **Client ID**
   - **Client Secret**

⚠️ **IMPORTANT**: Never share your Client Secret!

## Step 2: Set Environment Variables

### On Windows (PowerShell):

```powershell
$env:SPOTIFY_CLIENT_ID="your_client_id_here"
$env:SPOTIFY_CLIENT_SECRET="your_client_secret_here"
```

### On Windows (Command Prompt):

```cmd
set SPOTIFY_CLIENT_ID=your_client_id_here
set SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

### On Linux/Mac (Bash):

```bash
export SPOTIFY_CLIENT_ID="your_client_id_here"
export SPOTIFY_CLIENT_SECRET="your_client_secret_here"
```

### Using .env file (Recommended for Development):

Create a `.env` file in the project root:

```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

Then load it in Python:

```python
from dotenv import load_dotenv
load_dotenv()
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Or just install spotipy:

```bash
pip install spotipy==2.22.1
```

## Step 4: Test the Integration

### Test Script Mode

```bash
python spotify_integration.py
```

This will run a demo that:
1. Searches for "lo-fi" tracks
2. Searches for "Dua Lipa" artist
3. Gets available genres
4. Gets recommendations

### Test via Backend API

Start the backend server:

```bash
python backend_api.py
```

Then test endpoints:

```bash
# Search tracks
curl "http://localhost:8000/spotify/search/tracks?q=lo-fi&limit=5"

# Get recommendations
curl "http://localhost:8000/spotify/recommendations?seed_genres=lo-fi&limit=10"

# Check health
curl "http://localhost:8000/spotify/health"
```

## Available API Endpoints

### Search Endpoints

#### Search Tracks
```
GET /spotify/search/tracks?q=<query>&limit=<1-50>
```

Response:
```json
{
  "status": "success",
  "query": "lo-fi",
  "count": 5,
  "tracks": [
    {
      "id": "track_id",
      "name": "Track Name",
      "artist": "Artist Name",
      "album": "Album Name",
      "image": "album_cover_url",
      "preview_url": "preview_audio_url",
      "popularity": 85,
      "duration_ms": 180000
    }
  ]
}
```

#### Search Artists
```
GET /spotify/search/artists?q=<query>&limit=<1-50>
```

#### Search Playlists
```
GET /spotify/search/playlists?q=<query>&limit=<1-50>
```

### Recommendation Endpoints

#### Get Recommendations
```
GET /spotify/recommendations?seed_tracks=<ids>&seed_artists=<ids>&seed_genres=<genres>&limit=<1-100>
```

**Parameters:**
- `seed_tracks`: Comma-separated track IDs (max 5)
- `seed_artists`: Comma-separated artist IDs (max 5)
- `seed_genres`: Comma-separated genres (max 5)
- `limit`: Number of recommendations (1-100)

**Example:**
```
GET /spotify/recommendations?seed_genres=lo-fi,ambient,chill&limit=10
```

### Track Information Endpoints

#### Get Track Details
```
GET /spotify/track/<track_id>
```

#### Get Audio Features
```
GET /spotify/audio-features/<track_id>
```

Response:
```json
{
  "energy": 0.5,
  "danceability": 0.7,
  "valence": 0.6,
  "acousticness": 0.8,
  "instrumentalness": 0.9,
  "liveness": 0.3,
  "speechiness": 0.1,
  "tempo": 120,
  "key": 0,
  "mode": 1,
  "time_signature": 4
}
```

### Genre & Playlist Endpoints

#### Get Available Genres
```
GET /spotify/genres
```

#### Get Playlist Tracks
```
GET /spotify/playlist/<playlist_id>?limit=<1-100>
```

### Health Check

#### Check Spotify Connection
```
GET /spotify/health
```

## Using Spotify Integration in JavaScript

### Search for Tracks

```javascript
const tracks = await spotifySearchTracks('lo-fi', 5);
console.log(tracks);
```

### Get Recommendations

```javascript
const recs = await spotifyGetRecommendations(
    ['track_id_1', 'track_id_2'],  // seed tracks
    ['artist_id'],                  // seed artists
    ['lo-fi', 'ambient'],           // seed genres
    10                              // limit
);
```

### Get Audio Features

```javascript
const features = await spotifyGetAudioFeatures('track_id');
console.log(features.energy);  // 0-1
console.log(features.danceability);  // 0-1
```

### Check Spotify Connection

```javascript
const isConnected = await spotifyCheckHealth();
if (isConnected) {
    console.log('Spotify is connected!');
}
```

## Python Integration

### Using the SpotifyClient Class

```python
from spotify_integration import get_spotify_client

# Get client instance
spotify = get_spotify_client()

# Check connection
if not spotify.is_connected():
    print("Spotify not connected!")
    exit()

# Search tracks
tracks = spotify.search_tracks("lo-fi", limit=5)
for track in tracks:
    print(f"{track['name']} by {track['artist']}")

# Get recommendations
recommendations = spotify.get_recommendations(
    seed_genres=['lo-fi', 'ambient'],
    limit=10
)

# Get audio features
features = spotify.get_audio_features('track_id')
print(f"Energy: {features['energy']}")
print(f"Danceability: {features['danceability']}")
```

## Troubleshooting

### "Spotify client not connected"

**Solution:**
1. Check environment variables are set:
   ```bash
   # PowerShell
   $env:SPOTIFY_CLIENT_ID
   $env:SPOTIFY_CLIENT_SECRET
   ```

2. Verify credentials are correct in Spotify Dashboard

3. Check internet connection

### "Unauthorized" (401 Error)

**Solution:**
- Verify Client ID and Secret are correct
- Check they haven't been rotated in Spotify Dashboard
- Try creating a new app

### Rate Limiting

**Note:** Spotify API has rate limits:
- 429 error = Rate limited
- Wait and retry after the specified time
- The client will automatically handle retries

### Search Returns Empty Results

**Solution:**
- Try different search queries
- Check spelling
- Use generic terms (e.g., "lo-fi" instead of "lo fi")

## Audio Features Explained

| Feature | Range | Meaning |
|---------|-------|---------|
| **Energy** | 0-1 | Intensity and activity (0=calm, 1=intense) |
| **Danceability** | 0-1 | How suitable for dancing |
| **Valence** | 0-1 | Musical positivity (0=sad, 1=happy) |
| **Acousticness** | 0-1 | Acoustic vs electronic |
| **Instrumentalness** | 0-1 | Lack of vocals |
| **Liveness** | 0-1 | Presence of audience (0=studio, 1=live) |
| **Speechiness** | 0-1 | Amount of spoken words |
| **Tempo** | BPM | Speed of the track |

## Integration with Music AI Recommendations

Combine Spotify data with your audio feature extraction:

```python
# Get Spotify track
spotify_track = spotify.search_tracks("lo-fi")[0]

# Get Spotify audio features
spotify_features = spotify.get_audio_features(spotify_track['id'])

# Compare with your extracted features
your_features = extract_features_from_file('audio.mp3')

# Use both for hybrid recommendations
```

## API Rate Limits

- **Spotify API**: 
  - No strict rate limit for app credentials
  - Fair use policy applies
  - Generally 20+ requests per second allowed

## Next Steps

1. ✅ Set environment variables
2. ✅ Install spotipy
3. ✅ Test `spotify_integration.py`
4. ✅ Start backend API
5. ✅ Test endpoints with curl or browser
6. ✅ Use in frontend via JavaScript functions

## Resources

- [Spotify Developer Documentation](https://developer.spotify.com/documentation/web-api)
- [Spotipy Documentation](https://spotipy.readthedocs.io/)
- [Spotify API Reference](https://developer.spotify.com/documentation/web-api/reference)
- [Audio Features Guide](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)

## Support

For issues with:
- **Spotify Credentials**: Check [Spotify Dashboard](https://developer.spotify.com/dashboard)
- **Spotipy Library**: See [Spotipy GitHub](https://github.com/plamere/spotipy)
- **API Integration**: Check `backend_api.py` for endpoint implementation
