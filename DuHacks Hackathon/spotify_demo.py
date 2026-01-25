"""
Quick Start Guide - Spotify Integration
Run this file to test Spotify API integration
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spotify_integration import get_spotify_client

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def main():
    """Main demo function"""
    
    print_section("🎵 SPOTIFY INTEGRATION QUICK START")
    
    # Initialize client
    print("📍 Initializing Spotify client...")
    spotify = get_spotify_client()
    
    # Check connection
    if not spotify.is_connected():
        print("\n⚠️  ERROR: Spotify client not connected!")
        print("\nPlease set these environment variables:")
        print("  Windows (PowerShell):")
        print("    $env:SPOTIFY_CLIENT_ID='your_client_id'")
        print("    $env:SPOTIFY_CLIENT_SECRET='your_client_secret'")
        print("\n  Linux/Mac:")
        print("    export SPOTIFY_CLIENT_ID='your_client_id'")
        print("    export SPOTIFY_CLIENT_SECRET='your_client_secret'")
        print("\nGet credentials from: https://developer.spotify.com/dashboard")
        return
    
    print("✅ Spotify client connected!\n")
    
    # Demo 1: Search Tracks
    print_section("DEMO 1: Search for Tracks")
    print("Searching for 'lo-fi' tracks...")
    
    tracks = spotify.search_tracks("lo-fi", limit=3)
    
    if tracks:
        print(f"\nFound {len(tracks)} tracks:\n")
        for i, track in enumerate(tracks, 1):
            print(f"{i}. {track['name']}")
            print(f"   Artist: {track['artist']}")
            print(f"   Album: {track['album']}")
            print(f"   Popularity: {track['popularity']}/100")
            print()
    else:
        print("No tracks found.")
    
    # Demo 2: Search Artists
    print_section("DEMO 2: Search for Artists")
    print("Searching for 'The Weeknd'...")
    
    artists = spotify.search_artists("The Weeknd", limit=2)
    
    if artists:
        print(f"\nFound {len(artists)} artists:\n")
        for i, artist in enumerate(artists, 1):
            print(f"{i}. {artist['name']}")
            print(f"   Genres: {', '.join(artist['genres'][:3])}")
            print(f"   Popularity: {artist['popularity']}/100")
            print(f"   Followers: {artist['followers']:,}")
            print()
    else:
        print("No artists found.")
    
    # Demo 3: Get Audio Features
    if tracks:
        print_section("DEMO 3: Get Audio Features")
        track = tracks[0]
        print(f"Analyzing audio features for: {track['name']}")
        
        features = spotify.get_audio_features(track['id'])
        
        if features:
            print(f"\nAudio Features:\n")
            print(f"  Energy:           {features['energy']:.2f} (0=calm, 1=intense)")
            print(f"  Danceability:     {features['danceability']:.2f} (0=not danceable, 1=very)")
            print(f"  Valence:          {features['valence']:.2f} (0=sad, 1=happy)")
            print(f"  Acousticness:     {features['acousticness']:.2f} (0=electronic, 1=acoustic)")
            print(f"  Instrumentalness: {features['instrumentalness']:.2f} (0=vocals, 1=instrumental)")
            print(f"  Liveness:         {features['liveness']:.2f} (0=studio, 1=live)")
            print(f"  Speechiness:      {features['speechiness']:.2f} (0=music, 1=spoken)")
            print(f"  Tempo:            {features['tempo']:.0f} BPM")
            print()
        else:
            print("Could not retrieve audio features.")
    
    # Demo 4: Get Recommendations
    if tracks:
        print_section("DEMO 4: Get Recommendations")
        track = tracks[0]
        print(f"Getting recommendations based on: {track['name']}\n")
        
        recommendations = spotify.get_recommendations(
            seed_tracks=[track['id']],
            limit=3
        )
        
        if recommendations:
            print(f"Found {len(recommendations)} recommendations:\n")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['name']}")
                print(f"   Artist: {rec['artist']}")
                print(f"   Popularity: {rec['popularity']}/100")
                print()
        else:
            print("No recommendations found.")
    
    # Demo 5: Browse Genres
    print_section("DEMO 5: Available Genres")
    genres = spotify.get_available_genres()
    
    if genres:
        print(f"Total genres available: {len(genres)}\n")
        print("Sample genres (first 20):")
        for i, genre in enumerate(genres[:20], 1):
            print(f"  {i:2d}. {genre}")
        
        if len(genres) > 20:
            print(f"  ... and {len(genres) - 20} more!")
    else:
        print("Could not retrieve genres.")
    
    # Demo 6: Recommendations by Genre
    print_section("DEMO 6: Recommendations by Genre")
    print("Getting recommendations for 'lo-fi' and 'ambient' genres...\n")
    
    recs = spotify.get_recommendations(
        seed_genres=['lo-fi', 'ambient'],
        limit=3
    )
    
    if recs:
        print(f"Found {len(recs)} recommendations:\n")
        for i, track in enumerate(recs, 1):
            print(f"{i}. {track['name']} by {track['artist']}")
            print(f"   Popularity: {track['popularity']}/100")
            print()
    else:
        print("No recommendations found.")
    
    # End
    print_section("✅ DEMO COMPLETE")
    print("For more features, see SPOTIFY_SETUP.md")
    print("For API endpoints, run: python backend_api.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
