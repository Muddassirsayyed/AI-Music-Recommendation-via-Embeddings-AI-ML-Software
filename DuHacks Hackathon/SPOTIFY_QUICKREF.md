# 🎵 Spotify API Integration - Quick Reference

## What Was Added

### New Files
- **`spotify_integration.py`** - Core Spotify API client and functions
- **`spotify_demo.py`** - Demo script to test Spotify integration
- **`SPOTIFY_SETUP.md`** - Complete setup and reference guide

### Updated Files
- **`backend_api.py`** - Added 10+ Spotify endpoints
- **`script.js`** - Added Spotify search functions
- **`requirements.txt`** - Added `spotipy==2.22.1`

## Quick Start (3 Steps)

### Step 1: Get Spotify Credentials
1. Go to https://developer.spotify.com/dashboard
2. Create an app
3. Copy `Client ID` and `Client Secret`

### Step 2: Set Environment Variables
```powershell
# Windows PowerShell
$env:SPOTIFY_CLIENT_ID="your_client_id"
$env:SPOTIFY_CLIENT_SECRET="your_client_secret"
```

### Step 3: Install & Test
```bash
# Install spotipy
pip install spotipy

# Run demo
python spotify_demo.py
```

## Available Features

### ✅ Backend API Endpoints (http://localhost:8000)

| Endpoint | Description |
|----------|-------------|
| `GET /spotify/search/tracks` | Search for tracks |
| `GET /spotify/search/artists` | Search for artists |
| `GET /spotify/search/playlists` | Search for playlists |
| `GET /spotify/recommendations` | Get recommendations |
| `GET /spotify/track/{id}` | Get track details |
| `GET /spotify/audio-features/{id}` | Get audio features |
| `GET /spotify/genres` | List all genres |
| `GET /spotify/playlist/{id}` | Get playlist tracks |
| `GET /spotify/health` | Check Spotify connection |

### ✅ JavaScript Functions (Frontend)

```javascript
// Search
await spotifySearchTracks('query', limit)
await spotifySearchArtists('query', limit)

// Recommendations
await spotifyGetRecommendations(trackIds, artistIds, genres, limit)

// Analysis
await spotifyGetAudioFeatures(trackId)
await spotifyGetGenres()

// Status
await spotifyCheckHealth()
```

### ✅ Python Client

```python
from spotify_integration import get_spotify_client

spotify = get_spotify_client()

# Search
spotify.search_tracks('query', limit=5)
spotify.search_artists('query', limit=5)
spotify.search_playlists('query', limit=5)

# Recommendations
spotify.get_recommendations(seed_tracks, seed_artists, seed_genres, limit)

# Audio Analysis
spotify.get_audio_features(track_id)
spotify.get_multiple_audio_features([track_ids])

# Browse
spotify.get_available_genres()
spotify.get_playlist_tracks(playlist_id)
```

## Example Usage

### Python: Search and Get Recommendations

```python
from spotify_integration import get_spotify_client

spotify = get_spotify_client()

# Search for tracks
tracks = spotify.search_tracks("lo-fi", limit=5)
print(f"Found {len(tracks)} tracks")

# Get recommendations based on first track
recs = spotify.get_recommendations(
    seed_tracks=[tracks[0]['id']],
    limit=10
)

# Analyze audio features
for track in recs:
    features = spotify.get_audio_features(track['id'])
    print(f"{track['name']}: Energy={features['energy']:.2f}")
```

### JavaScript: Search and Display

```javascript
// Search for tracks
const tracks = await spotifySearchTracks('ambient', 5);

// Display results
tracks.forEach(track => {
    console.log(`${track.name} by ${track.artist}`);
    console.log(`Popularity: ${track.popularity}/100`);
});

// Get recommendations
const recs = await spotifyGetRecommendations(
    [tracks[0].id],  // seed tracks
    [],              // seed artists
    ['ambient'],     // seed genres
    10
);
```

### cURL: Test API Endpoints

```bash
# Search tracks
curl "http://localhost:8000/spotify/search/tracks?q=lo-fi&limit=5"

# Get recommendations
curl "http://localhost:8000/spotify/recommendations?seed_genres=lo-fi&limit=10"

# Get genres
curl "http://localhost:8000/spotify/genres"

# Check health
curl "http://localhost:8000/spotify/health"
```

## Audio Features Reference

| Feature | Range | Meaning |
|---------|-------|---------|
| **Energy** | 0-1 | How intense/active (0=calm, 1=intense) |
| **Danceability** | 0-1 | How suitable for dancing |
| **Valence** | 0-1 | Musical positivity (0=sad, 1=happy) |
| **Acousticness** | 0-1 | Acoustic vs electronic (0=electronic, 1=acoustic) |
| **Instrumentalness** | 0-1 | Presence of vocals (0=vocals, 1=instrumental) |
| **Liveness** | 0-1 | Audience presence (0=studio, 1=live) |
| **Speechiness** | 0-1 | Amount of spoken words (0=music, 1=spoken) |
| **Tempo** | BPM | Beats per minute (speed) |
| **Key** | 0-11 | Pitch standard (0=C, 1=C#, etc.) |
| **Mode** | 0-1 | Major (1) or Minor (0) scale |

## Use Cases

### 1. **Discover Similar Music**
```python
# Find music similar to a track
track = spotify.search_tracks("Blinding Lights")[0]
similar = spotify.get_recommendations(
    seed_tracks=[track['id']],
    limit=20
)
```

### 2. **Mood-Based Playlist**
```python
# Get happy, danceable songs
happy_music = spotify.get_recommendations(
    seed_genres=['pop', 'dance'],
    limit=30
)
```

### 3. **Analyze Music Characteristics**
```python
# Get all features for analysis
tracks = spotify.search_tracks('lo-fi', 10)
all_features = spotify.get_multiple_audio_features(
    [t['id'] for t in tracks]
)

# Average energy
avg_energy = sum(f['energy'] for f in all_features) / len(all_features)
```

### 4. **Genre Exploration**
```python
# Get all genres
genres = spotify.get_available_genres()

# Recommend from specific genre
jazz_recs = spotify.get_recommendations(
    seed_genres=['jazz'],
    limit=10
)
```

## Troubleshooting

### "Spotify client not connected"
- Check environment variables are set
- Verify Client ID and Secret are correct
- Ensure internet connection works

### "No results found"
- Try different search terms
- Check spelling
- Use more generic keywords

### Rate Limit (429 Error)
- Wait before retrying
- The library handles this automatically
- Typically no issues for normal usage

## Files Summary

| File | Purpose |
|------|---------|
| `spotify_integration.py` | Main Spotify API client (300+ lines) |
| `spotify_demo.py` | Interactive demo and testing |
| `backend_api.py` | FastAPI endpoints for Spotify |
| `script.js` | Frontend JavaScript integration |
| `SPOTIFY_SETUP.md` | Detailed setup and API reference |
| `requirements.txt` | Updated with `spotipy==2.22.1` |

## Architecture

```
Frontend (JavaScript)
    ↓
Web Server (http://localhost:9000)
    ↓
Backend API (http://localhost:8000)
    ↓
Spotify Integration Module
    ↓
Spotify Web API
    ↓
Spotify Database
```

## Next Steps

1. ✅ Set Spotify environment variables
2. ✅ Run `python spotify_demo.py`
3. ✅ Start backend: `python backend_api.py`
4. ✅ Test endpoints with cURL or browser
5. ✅ Integrate into frontend features

## Resources

- [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- [Spotipy Documentation](https://spotipy.readthedocs.io/)
- [Spotify API Reference](https://developer.spotify.com/documentation/web-api)
- [Audio Features Guide](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)

---

**Spotify API is now fully integrated into your Music AI system!** 🎵
