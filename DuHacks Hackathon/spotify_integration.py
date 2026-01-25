"""
Spotify API Integration for Music AI Recommendation System
Handles Spotify authentication, search, and recommendations
"""

import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# SPOTIFY CLIENT CONFIGURATION
# ============================================================================

class SpotifyClient:
    """Manages Spotify API connection and operations"""
    
    def __init__(self, client_id=None, client_secret=None):
        """
        Initialize Spotify client with credentials
        
        Args:
            client_id: Spotify Client ID (env var: SPOTIFY_CLIENT_ID)
            client_secret: Spotify Client Secret (env var: SPOTIFY_CLIENT_SECRET)
        """
        self.client_id = client_id or os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            logger.warning('⚠️  Spotify credentials not found. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables.')
            self.sp = None
            return
        
        try:
            auth_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            logger.info('✅ Spotify client initialized successfully')
        except Exception as e:
            logger.error(f'❌ Error initializing Spotify client: {e}')
            self.sp = None
    
    def is_connected(self):
        """Check if Spotify client is connected"""
        return self.sp is not None
    
    # ====================================================================
    # SEARCH METHODS
    # ====================================================================
    
    def search_tracks(self, query, limit=5):
        """
        Search for tracks on Spotify
        
        Args:
            query: Search query (artist, track name, etc.)
            limit: Maximum number of results (default: 5)
            
        Returns:
            List of track dictionaries with metadata
        """
        if not self.is_connected():
            logger.error('Spotify client not connected')
            return []
        
        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []
            
            for item in results['tracks']['items']:
                track = {
                    'id': item['id'],
                    'name': item['name'],
                    'artist': item['artists'][0]['name'] if item['artists'] else 'Unknown',
                    'album': item['album']['name'],
                    'image': item['album']['images'][0]['url'] if item['album']['images'] else None,
                    'preview_url': item['preview_url'],
                    'external_url': item['external_urls']['spotify'],
                    'duration_ms': item['duration_ms'],
                    'popularity': item['popularity'],
                    'explicit': item['explicit']
                }
                tracks.append(track)
            
            logger.info(f'✅ Found {len(tracks)} tracks for query: {query}')
            return tracks
        
        except Exception as e:
            logger.error(f'❌ Error searching tracks: {e}')
            return []
    
    def search_artists(self, query, limit=5):
        """
        Search for artists on Spotify
        
        Args:
            query: Artist name or keywords
            limit: Maximum number of results (default: 5)
            
        Returns:
            List of artist dictionaries
        """
        if not self.is_connected():
            return []
        
        try:
            results = self.sp.search(q=query, type='artist', limit=limit)
            artists = []
            
            for item in results['artists']['items']:
                artist = {
                    'id': item['id'],
                    'name': item['name'],
                    'image': item['images'][0]['url'] if item['images'] else None,
                    'genres': item['genres'],
                    'popularity': item['popularity'],
                    'followers': item['followers']['total'],
                    'external_url': item['external_urls']['spotify']
                }
                artists.append(artist)
            
            logger.info(f'✅ Found {len(artists)} artists for query: {query}')
            return artists
        
        except Exception as e:
            logger.error(f'❌ Error searching artists: {e}')
            return []
    
    def search_playlists(self, query, limit=5):
        """
        Search for playlists on Spotify
        
        Args:
            query: Playlist keywords
            limit: Maximum number of results (default: 5)
            
        Returns:
            List of playlist dictionaries
        """
        if not self.is_connected():
            return []
        
        try:
            results = self.sp.search(q=query, type='playlist', limit=limit)
            playlists = []
            
            for item in results['playlists']['items']:
                playlist = {
                    'id': item['id'],
                    'name': item['name'],
                    'image': item['images'][0]['url'] if item['images'] else None,
                    'tracks_count': item['tracks']['total'],
                    'description': item['description'],
                    'external_url': item['external_urls']['spotify']
                }
                playlists.append(playlist)
            
            logger.info(f'✅ Found {len(playlists)} playlists for query: {query}')
            return playlists
        
        except Exception as e:
            logger.error(f'❌ Error searching playlists: {e}')
            return []
    
    # ====================================================================
    # RECOMMENDATION METHODS
    # ====================================================================
    
    def get_recommendations(self, seed_tracks=None, seed_artists=None, seed_genres=None, limit=10):
        """
        Get personalized recommendations based on seeds
        
        Args:
            seed_tracks: List of track IDs (max 5)
            seed_artists: List of artist IDs (max 5)
            seed_genres: List of genres (max 5)
            limit: Number of recommendations (default: 10)
            
        Returns:
            List of recommended track dictionaries
        """
        if not self.is_connected():
            return []
        
        try:
            # Ensure we have valid seeds
            if not seed_tracks and not seed_artists and not seed_genres:
                logger.warning('No seeds provided for recommendations')
                return []
            
            recommendations = self.sp.recommendations(
                seed_tracks=seed_tracks,
                seed_artists=seed_artists,
                seed_genres=seed_genres,
                limit=limit
            )
            
            tracks = []
            for item in recommendations['tracks']:
                track = {
                    'id': item['id'],
                    'name': item['name'],
                    'artist': item['artists'][0]['name'] if item['artists'] else 'Unknown',
                    'album': item['album']['name'],
                    'image': item['album']['images'][0]['url'] if item['album']['images'] else None,
                    'preview_url': item['preview_url'],
                    'external_url': item['external_urls']['spotify'],
                    'duration_ms': item['duration_ms'],
                    'popularity': item['popularity']
                }
                tracks.append(track)
            
            logger.info(f'✅ Generated {len(tracks)} recommendations')
            return tracks
        
        except Exception as e:
            logger.error(f'❌ Error getting recommendations: {e}')
            return []
    
    # ====================================================================
    # AUDIO FEATURES METHODS
    # ====================================================================
    
    def get_audio_features(self, track_id):
        """
        Get audio features for a track
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Dictionary with audio feature data
        """
        if not self.is_connected():
            return None
        
        try:
            features = self.sp.audio_features(track_id)[0]
            
            audio_data = {
                'energy': features.get('energy', 0),
                'danceability': features.get('danceability', 0),
                'valence': features.get('valence', 0),
                'acousticness': features.get('acousticness', 0),
                'instrumentalness': features.get('instrumentalness', 0),
                'liveness': features.get('liveness', 0),
                'speechiness': features.get('speechiness', 0),
                'tempo': features.get('tempo', 0),
                'key': features.get('key', 0),
                'mode': features.get('mode', 0),
                'time_signature': features.get('time_signature', 4)
            }
            
            logger.info(f'✅ Retrieved audio features for track: {track_id}')
            return audio_data
        
        except Exception as e:
            logger.error(f'❌ Error getting audio features: {e}')
            return None
    
    def get_multiple_audio_features(self, track_ids):
        """
        Get audio features for multiple tracks
        
        Args:
            track_ids: List of Spotify track IDs (max 100)
            
        Returns:
            List of audio feature dictionaries
        """
        if not self.is_connected():
            return []
        
        try:
            features_list = self.sp.audio_features(track_ids)
            
            results = []
            for features in features_list:
                if features:
                    audio_data = {
                        'track_id': features.get('id'),
                        'energy': features.get('energy', 0),
                        'danceability': features.get('danceability', 0),
                        'valence': features.get('valence', 0),
                        'acousticness': features.get('acousticness', 0),
                        'instrumentalness': features.get('instrumentalness', 0),
                        'liveness': features.get('liveness', 0),
                        'speechiness': features.get('speechiness', 0),
                        'tempo': features.get('tempo', 0)
                    }
                    results.append(audio_data)
            
            logger.info(f'✅ Retrieved features for {len(results)} tracks')
            return results
        
        except Exception as e:
            logger.error(f'❌ Error getting multiple audio features: {e}')
            return []
    
    # ====================================================================
    # PLAYLIST & TRACK METHODS
    # ====================================================================
    
    def get_track_info(self, track_id):
        """Get detailed information about a track"""
        if not self.is_connected():
            return None
        
        try:
            track = self.sp.track(track_id)
            
            return {
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                'album': track['album']['name'],
                'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'preview_url': track['preview_url'],
                'external_url': track['external_urls']['spotify'],
                'duration_ms': track['duration_ms'],
                'popularity': track['popularity'],
                'release_date': track['album']['release_date'],
                'explicit': track['explicit'],
                'isrc': track.get('external_ids', {}).get('isrc')
            }
        
        except Exception as e:
            logger.error(f'❌ Error getting track info: {e}')
            return None
    
    def get_playlist_tracks(self, playlist_id, limit=50):
        """Get all tracks from a playlist"""
        if not self.is_connected():
            return []
        
        try:
            results = self.sp.playlist_tracks(playlist_id, limit=limit)
            tracks = []
            
            for item in results['items']:
                track = item['track']
                if track:
                    tracks.append({
                        'id': track['id'],
                        'name': track['name'],
                        'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                        'album': track['album']['name'],
                        'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                        'external_url': track['external_urls']['spotify']
                    })
            
            logger.info(f'✅ Retrieved {len(tracks)} tracks from playlist')
            return tracks
        
        except Exception as e:
            logger.error(f'❌ Error getting playlist tracks: {e}')
            return []
    
    # ====================================================================
    # GENRE METHODS
    # ====================================================================
    
    def get_available_genres(self):
        """Get list of available genres"""
        if not self.is_connected():
            return []
        
        try:
            genres = self.sp.recommendation_genre_seeds()['genres']
            logger.info(f'✅ Retrieved {len(genres)} available genres')
            return sorted(genres)
        
        except Exception as e:
            logger.error(f'❌ Error getting genres: {e}')
            return []


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_spotify_client = None

def get_spotify_client(client_id=None, client_secret=None):
    """
    Get or create a Spotify client instance
    
    Args:
        client_id: Optional Spotify Client ID
        client_secret: Optional Spotify Client Secret
        
    Returns:
        SpotifyClient instance
    """
    global _spotify_client
    
    if _spotify_client is None:
        _spotify_client = SpotifyClient(client_id, client_secret)
    
    return _spotify_client

# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == '__main__':
    """Test the Spotify integration"""
    
    print("\n" + "="*70)
    print("🎵 SPOTIFY API INTEGRATION TEST")
    print("="*70)
    
    # Initialize client
    spotify = get_spotify_client()
    
    if not spotify.is_connected():
        print("\n⚠️  Spotify client not connected. Set these environment variables:")
        print("   - SPOTIFY_CLIENT_ID")
        print("   - SPOTIFY_CLIENT_SECRET")
        print("\nGet credentials from: https://developer.spotify.com/dashboard")
    else:
        # Test searches
        print("\n📍 Testing searches...")
        
        # Search tracks
        tracks = spotify.search_tracks("lo-fi", limit=3)
        print(f"\n🎵 Found {len(tracks)} tracks for 'lo-fi':")
        for track in tracks:
            print(f"   - {track['name']} by {track['artist']}")
        
        # Search artists
        artists = spotify.search_artists("Dua Lipa", limit=2)
        print(f"\n👤 Found {len(artists)} artists for 'Dua Lipa':")
        for artist in artists:
            print(f"   - {artist['name']} ({artist['popularity']}% popularity)")
        
        # Get available genres
        genres = spotify.get_available_genres()
        print(f"\n🎼 Available genres (first 10): {genres[:10]}")
        
        # Get recommendations
        if tracks:
            print(f"\n🎯 Getting recommendations based on '{tracks[0]['name']}'...")
            recs = spotify.get_recommendations(seed_tracks=[tracks[0]['id']], limit=3)
            print(f"   Found {len(recs)} recommendations:")
            for rec in recs:
                print(f"   - {rec['name']} by {rec['artist']}")
    
    print("\n" + "="*70)
