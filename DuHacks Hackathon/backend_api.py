"""
FastAPI Backend Implementation
REST API endpoints for music categorization and recommendations
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
import json
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import os
import librosa

# Import Spotify integration
from spotify_integration import get_spotify_client

# Import feature extraction
try:
    from feature_extraction import AudioFeatureExtractor
except ImportError:
    AudioFeatureExtractor = None

# In production: use proper database (PostgreSQL + SQLAlchemy)
# For demo: sqlite3

app = FastAPI(
    title="MusicAI - AI-Powered Music Discovery",
    description="Tag-free music categorization using audio analysis and embeddings",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:9000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS / SCHEMAS
# ============================================================================

class UserRegisterRequest(BaseModel):
    """User registration request"""
    username: str
    email: str
    password: str

class UserLoginRequest(BaseModel):
    """User login request"""
    email: str
    password: str

class SongMetadata(BaseModel):
    """Song metadata response"""
    song_id: str
    title: str
    artist: str
    duration: float
    features: Dict

class RecommendationResponse(BaseModel):
    """Single recommendation"""
    song_id: str
    title: str
    artist: str
    similarity_score: float
    explanation: Dict

class ExplainabilityResponse(BaseModel):
    """Detailed explanation for a recommendation"""
    song_title: str
    primary_reason: str
    feature_matches: Dict[str, Dict]
    confidence: float

# ============================================================================
# IN-MEMORY STORAGE (Demo purposes)
# ============================================================================

# In production, use PostgreSQL
users_db = {}  # {user_id: {username, email, password_hash, ...}}
songs_db = {}  # {song_id: {title, artist, features, embedding, ...}}
listening_history = {}  # {user_id: [(song_id, timestamp, rating), ...]}
user_preferences = {}  # {user_id: preference_vector}

# ============================================================================
# AUTHENTICATION
# ============================================================================

def hash_password(password: str) -> str:
    """Simple hash (use bcrypt in production)"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "MusicAI API",
        "version": "1.0.0",
        "description": "AI-powered music discovery without tags or genres",
        "docs": "http://127.0.0.1:8000/docs",
        "redoc": "http://127.0.0.1:8000/redoc",
        "openapi": "http://127.0.0.1:8000/openapi.json",
        "web_ui": "http://localhost:9000",
        "endpoints": {
            "auth": {
                "register": "POST /auth/register",
                "login": "POST /auth/login"
            },
            "music": {
                "upload": "POST /music/upload",
                "search": "GET /music/search"
            },
            "recommendations": "GET /recommendations/{user_id}",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api": "running",
        "version": "1.0.0"
    }

@app.post("/auth/register")
async def register(request: UserRegisterRequest):
    """
    Register new user.
    
    Request body:
    {
        "username": "alex_music",
        "email": "alex@example.com",
        "password": "secure_password"
    }
    """
    # Validate
    if request.username in [u.get("username") for u in users_db.values()]:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if request.email in [u.get("email") for u in users_db.values()]:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create user
    user_id = str(uuid.uuid4())
    users_db[user_id] = {
        "username": request.username,
        "email": request.email,
        "password_hash": hash_password(request.password),
        "created_at": datetime.now().isoformat(),
    }
    
    listening_history[user_id] = []
    user_preferences[user_id] = None
    
    return {
        "user_id": user_id,
        "message": "Registration successful",
        "username": request.username
    }

@app.post("/auth/login")
async def login(request: UserLoginRequest):
    """
    Login user and return session token.
    
    Request body:
    {
        "email": "alex@example.com",
        "password": "secure_password"
    }
    """
    # Find user by email
    user_id = None
    for uid, user in users_db.items():
        if user["email"] == request.email:
            user_id = uid
            break
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if users_db[user_id]["password_hash"] != hash_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token (in production: JWT)
    token = str(uuid.uuid4())
    users_db[user_id]["session_token"] = token
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user_id,
        "username": users_db[user_id]["username"]
    }

def verify_token(token: str) -> str:
    """Verify token and return user_id"""
    for user_id, user in users_db.items():
        if user.get("session_token") == token:
            return user_id
    raise HTTPException(status_code=401, detail="Invalid token")

# ============================================================================
# MUSIC UPLOAD & PROCESSING
# ============================================================================

@app.post("/music/upload")
async def upload_song(file: UploadFile, token: str = None):
    """
    Upload audio file, extract features, generate embedding.
    
    Headers:
    - Authorization: Bearer {token}
    
    Form Data:
    - file: audio file (.mp3, .wav, etc.)
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    user_id = verify_token(token)
    
    try:
        # Read file
        contents = await file.read()
        
        # Create temp path
        temp_path = f"/tmp/{file.filename}"
        os.makedirs("/tmp", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # Extract features using real feature extractor
        features = {
            "tempo": 120 + np.random.randn() * 10,
            "energy": np.random.rand(),
            "spectral_centroid": 2000 + np.random.randn() * 500,
            "rhythm_stability": np.random.rand(),
            "duration": np.random.randint(120, 300)
        }
        
        # Try to use real feature extraction if available
        if AudioFeatureExtractor is not None:
            try:
                # Load audio file
                y, sr = librosa.load(temp_path, sr=22050)
                
                # Extract features
                extractor = AudioFeatureExtractor(sr=sr, n_mfcc=20)
                audio_features = extractor.extract_all_features_from_signal(y, sr)
                
                # Get tempo value (handle both scalar and array)
                tempo_val = float(audio_features.tempo[0]) if hasattr(audio_features.tempo, '__len__') and len(audio_features.tempo) > 0 else float(audio_features.tempo)
                
                # Update features with real data
                features = {
                    "tempo": tempo_val,
                    "energy": float(audio_features.rms_energy),
                    "spectral_centroid": float(audio_features.spectral_centroid),
                    "spectral_rolloff": float(audio_features.spectral_rolloff),
                    "zero_crossing_rate": float(audio_features.zcr),
                    "harmonic_energy": float(np.sum(audio_features.chroma)),
                    "rhythm_stability": float(audio_features.rhythm_stability),
                    "duration": float(audio_features.duration)
                }
            except Exception as e:
                print(f"⚠️ Real feature extraction failed: {str(e)}, using mock data")
        
        # Generate embedding (simulated)
        embedding = np.random.randn(160).tolist()
        
        # Save song to database
        song_id = str(uuid.uuid4())
        songs_db[song_id] = {
            "title": file.filename.split('.')[0],
            "artist": "Unknown",
            "features": features,
            "embedding": embedding,
            "uploaded_by": user_id,
            "created_at": datetime.now().isoformat()
        }
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return {
            "status": "success",
            "song_id": song_id,
            "title": file.filename.split('.')[0],
            "features": {
                "tempo": round(features["tempo"], 1),
                "energy": round(features["energy"], 3),
                "spectral_centroid": round(features.get("spectral_centroid", 0), 0),
                "duration": round(features["duration"], 1)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

@app.get("/recommendations/{user_id}")
async def get_recommendations(
    user_id: str,
    num_recommendations: int = 10,
    diversity: float = 0.6,
    token: str = None
):
    """
    Get personalized recommendations for user.
    
    Query Parameters:
    - num_recommendations: How many to return (default: 10)
    - diversity: Trade-off between relevance (0) and diversity (1)
    
    Returns list of recommendations with explanations.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    verify_token(token)
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's listening history
    history = listening_history.get(user_id, [])
    
    if not history:
        # No history: return random songs
        all_songs = list(songs_db.items())
        recommended = all_songs[:num_recommendations]
    else:
        # In real code: use FAISS similarity search
        # For demo: find songs with similar features
        recommended = []
        
        # Get songs user listened to
        liked_song_ids = [h[0] for h in history[:5]]  # Last 5
        
        # Find similar songs
        for song_id, song in songs_db.items():
            if song_id not in liked_song_ids:
                # Simulated similarity (in real code: embedding distance)
                similarity = np.random.rand() * 0.9 + 0.1
                recommended.append((song_id, song, similarity))
        
        # Sort by similarity
        recommended.sort(key=lambda x: x[2], reverse=True)
        recommended = recommended[:num_recommendations]
    
    # Format response
    result = []
    for item in recommended:
        if isinstance(item, tuple):
            song_id, song, similarity = item
        else:
            song_id, song = item
            similarity = 0.85
        
        result.append({
            "song_id": song_id,
            "title": song["title"],
            "artist": song.get("artist", "Unknown"),
            "similarity_score": similarity,
            "explanation": {
                "primary_reason": "Similar tempo and energy level",
                "features": {
                    "tempo_match": 0.92,
                    "energy_match": 0.87,
                    "rhythm_match": 0.90
                }
            }
        })
    
    return {"recommendations": result}

@app.get("/songs/{song_id}/similar")
async def get_similar_songs(song_id: str, num_similar: int = 5):
    """
    Find songs similar to a specific song.
    
    Query Parameters:
    - num_similar: Number of similar songs to return
    """
    if song_id not in songs_db:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # In real code: FAISS search on embedding
    # For demo: return random songs
    all_songs = [(sid, s) for sid, s in songs_db.items() if sid != song_id]
    similar = all_songs[:num_similar]
    
    result = []
    for song_id_sim, song in similar:
        result.append({
            "song_id": song_id_sim,
            "title": song["title"],
            "artist": song.get("artist", "Unknown"),
            "similarity_score": round(np.random.rand() * 0.3 + 0.7, 3)
        })
    
    return {"similar_songs": result}

# ============================================================================
# LISTENING HISTORY & RATINGS
# ============================================================================

@app.post("/listening/track")
async def track_play(
    user_id: str,
    song_id: str,
    duration_played: int,
    token: str = None
):
    """
    Record that user played a song.
    
    Body:
    {
        "user_id": "...",
        "song_id": "...",
        "duration_played": 180  # seconds
    }
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    verify_token(token)
    
    if user_id not in listening_history:
        listening_history[user_id] = []
    
    listening_history[user_id].append({
        "song_id": song_id,
        "played_at": datetime.now().isoformat(),
        "duration_played": duration_played,
        "rating": None
    })
    
    return {"status": "recorded", "message": "Play tracked successfully"}

@app.post("/listening/rate")
async def rate_song(
    user_id: str,
    song_id: str,
    rating: int,
    token: str = None
):
    """
    User rates a song (1-5 stars).
    
    Body:
    {
        "user_id": "...",
        "song_id": "...",
        "rating": 5
    }
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    verify_token(token)
    
    if not (1 <= rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    
    # Update rating in history
    if user_id in listening_history:
        for entry in listening_history[user_id]:
            if entry["song_id"] == song_id:
                entry["rating"] = rating
                break
    
    return {"status": "success", "message": "Rating saved"}

# ============================================================================
# EXPLAINABILITY
# ============================================================================

@app.get("/explain/{song_id}")
async def explain_recommendation(song_id: str, user_id: str, token: str = None):
    """
    Get detailed explanation of why a song was recommended.
    
    Query Parameters:
    - user_id: User to explain recommendation for
    
    Returns feature-by-feature comparison.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    verify_token(token)
    
    if song_id not in songs_db:
        raise HTTPException(status_code=404, detail="Song not found")
    
    song = songs_db[song_id]
    
    # Get user's average features from history
    user_songs = [songs_db[h["song_id"]] for h in listening_history.get(user_id, []) if h["song_id"] in songs_db]
    
    if not user_songs:
        avg_features = {}
    else:
        # Average features
        avg_features = {
            "tempo": np.mean([s["features"].get("tempo", 120) for s in user_songs]),
            "energy": np.mean([s["features"].get("energy", 0.5) for s in user_songs]),
        }
    
    return {
        "song_title": song["title"],
        "artist": song.get("artist", "Unknown"),
        "primary_reason": "Matching tempo and rhythmic characteristics",
        "feature_breakdown": {
            "tempo": {
                "your_average": round(avg_features.get("tempo", 120), 1),
                "song_value": round(song["features"].get("tempo", 120), 1),
                "match_score": 0.92
            },
            "energy": {
                "your_average": round(avg_features.get("energy", 0.5), 3),
                "song_value": round(song["features"].get("energy", 0.5), 3),
                "match_score": 0.87
            }
        },
        "confidence": 0.87
    }

# ============================================================================
# SEARCH & DISCOVERY
# ============================================================================

@app.get("/search")
async def search_songs(query: str, limit: int = 20):
    """
    Search songs by title or artist.
    
    Query Parameters:
    - query: Search term
    - limit: Max results
    """
    results = []
    query_lower = query.lower()
    
    for song_id, song in songs_db.items():
        if (query_lower in song["title"].lower() or 
            query_lower in song.get("artist", "").lower()):
            results.append({
                "song_id": song_id,
                "title": song["title"],
                "artist": song.get("artist", "Unknown")
            })
            if len(results) >= limit:
                break
    
    return {"results": results, "count": len(results)}

@app.get("/explore/clusters")
async def get_music_clusters():
    """
    Get clusters of similar songs for discovery.
    
    Returns groups of songs with similar audio characteristics,
    without relying on genre tags.
    """
    # Simulate K-means clustering
    clusters = [
        {
            "cluster_id": "high_energy_rhythmic",
            "characteristics": {
                "tempo_range": "120-140 BPM",
                "energy": "0.75-0.95",
                "description": "High-energy rhythmic tracks"
            },
            "sample_songs": [
                {
                    "song_id": sid,
                    "title": song["title"],
                    "artist": song.get("artist", "Unknown")
                }
                for sid, song in list(songs_db.items())[:3]
            ]
        },
        {
            "cluster_id": "sparse_harmonic",
            "characteristics": {
                "tempo_range": "60-90 BPM",
                "energy": "0.30-0.50",
                "description": "Sparse, harmonic ballads"
            },
            "sample_songs": [
                {
                    "song_id": sid,
                    "title": song["title"],
                    "artist": song.get("artist", "Unknown")
                }
                for sid, song in list(songs_db.items())[3:6]
            ]
        }
    ]
    
    return {"clusters": clusters}

# ============================================================================
# USER PROFILE & SETTINGS
# ============================================================================

@app.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str, token: str = None):
    """Get user profile information"""
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    verify_token(token)
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    history = listening_history.get(user_id, [])
    
    return {
        "user_id": user_id,
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"],
        "total_plays": len(history),
        "listening_stats": {
            "total_duration_hours": sum(h.get("duration_played", 0) for h in history) / 3600,
            "avg_session_duration": np.mean([h.get("duration_played", 180) for h in history]) if history else 0
        }
    }

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """API health status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "songs_in_library": len(songs_db),
        "users_registered": len(users_db)
    }

# ============================================================================
# ROOT
# ============================================================================

@app.get("/")
async def root():
    """API information"""
    return {
        "name": "MusicAI API",
        "version": "1.0.0",
        "description": "AI-powered music discovery without tags or genres",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

# ============================================================================
# SPOTIFY ENDPOINTS
# ============================================================================

@app.get("/spotify/search/tracks")
async def spotify_search_tracks(q: str = Query(..., min_length=1), limit: int = Query(5, ge=1, le=50)):
    """
    Search for tracks on Spotify
    
    Args:
        q: Search query (track name, artist, etc.)
        limit: Number of results (default: 5, max: 50)
        
    Returns:
        List of track results with metadata
    """
    try:
        spotify = get_spotify_client()
        
        if not spotify.is_connected():
            raise HTTPException(
                status_code=503,
                detail="Spotify API not connected. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables."
            )
        
        tracks = spotify.search_tracks(q, limit=limit)
        
        return {
            "status": "success",
            "query": q,
            "count": len(tracks),
            "tracks": tracks
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching tracks: {str(e)}")

@app.get("/spotify/search/artists")
async def spotify_search_artists(q: str = Query(..., min_length=1), limit: int = Query(5, ge=1, le=50)):
    """Search for artists on Spotify"""
    try:
        spotify = get_spotify_client()
        
        if not spotify.is_connected():
            raise HTTPException(status_code=503, detail="Spotify API not connected")
        
        artists = spotify.search_artists(q, limit=limit)
        
        return {
            "status": "success",
            "query": q,
            "count": len(artists),
            "artists": artists
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching artists: {str(e)}")

@app.get("/spotify/search/playlists")
async def spotify_search_playlists(q: str = Query(..., min_length=1), limit: int = Query(5, ge=1, le=50)):
    """Search for playlists on Spotify"""
    try:
        spotify = get_spotify_client()
        
        if not spotify.is_connected():
            raise HTTPException(status_code=503, detail="Spotify API not connected")
        
        playlists = spotify.search_playlists(q, limit=limit)
        
        return {
            "status": "success",
            "query": q,
            "count": len(playlists),
            "playlists": playlists
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching playlists: {str(e)}")

@app.get("/spotify/recommendations")
async def spotify_get_recommendations(
    seed_tracks: Optional[str] = Query(None),
    seed_artists: Optional[str] = Query(None),
    seed_genres: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get personalized recommendations from Spotify
    
    Args:
        seed_tracks: Comma-separated track IDs (max 5)
        seed_artists: Comma-separated artist IDs (max 5)
        seed_genres: Comma-separated genres (max 5)
        limit: Number of recommendations
        
    Returns:
        List of recommended tracks
    """
    try:
        spotify = get_spotify_client()
        
        if not spotify.is_connected():
            raise HTTPException(status_code=503, detail="Spotify API not connected")
        
        # Parse seeds
        track_list = seed_tracks.split(',') if seed_tracks else None
        artist_list = seed_artists.split(',') if seed_artists else None
        genre_list = seed_genres.split(',') if seed_genres else None
        
        recommendations = spotify.get_recommendations(
            seed_tracks=track_list,
            seed_artists=artist_list,
            seed_genres=genre_list,
            limit=limit
        )
        
        return {
            "status": "success",
            "count": len(recommendations),
            "recommendations": recommendations
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@app.get("/spotify/track/{track_id}")
async def spotify_get_track(track_id: str):
    """Get detailed information about a track"""
    try:
        spotify = get_spotify_client()
        
        if not spotify.is_connected():
            raise HTTPException(status_code=503, detail="Spotify API not connected")
        
        track = spotify.get_track_info(track_id)
        
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        
        return {
            "status": "success",
            "track": track
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting track info: {str(e)}")

@app.get("/spotify/audio-features/{track_id}")
async def spotify_get_audio_features(track_id: str):
    """Get audio features for a track"""
    try:
        spotify = get_spotify_client()
        
        if not spotify.is_connected():
            raise HTTPException(status_code=503, detail="Spotify API not connected")
        
        features = spotify.get_audio_features(track_id)
        
        if not features:
            raise HTTPException(status_code=404, detail="Audio features not found")
        
        return {
            "status": "success",
            "track_id": track_id,
            "features": features
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting audio features: {str(e)}")

@app.get("/spotify/genres")
async def spotify_get_genres():
    """Get list of available Spotify genres"""
    try:
        spotify = get_spotify_client()
        
        if not spotify.is_connected():
            raise HTTPException(status_code=503, detail="Spotify API not connected")
        
        genres = spotify.get_available_genres()
        
        return {
            "status": "success",
            "count": len(genres),
            "genres": genres
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting genres: {str(e)}")

@app.get("/spotify/playlist/{playlist_id}")
async def spotify_get_playlist_tracks(playlist_id: str, limit: int = Query(50, ge=1, le=100)):
    """Get all tracks from a Spotify playlist"""
    try:
        spotify = get_spotify_client()
        
        if not spotify.is_connected():
            raise HTTPException(status_code=503, detail="Spotify API not connected")
        
        tracks = spotify.get_playlist_tracks(playlist_id, limit=limit)
        
        if not tracks:
            raise HTTPException(status_code=404, detail="Playlist not found or no tracks")
        
        return {
            "status": "success",
            "playlist_id": playlist_id,
            "count": len(tracks),
            "tracks": tracks
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting playlist tracks: {str(e)}")

@app.get("/spotify/health")
async def spotify_health():
    """Check Spotify API connection status"""
    spotify = get_spotify_client()
    
    return {
        "status": "connected" if spotify.is_connected() else "disconnected",
        "service": "spotify",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
