"""
Example: Integrating Spotify Data with Music AI Recommendations
Shows how to combine Spotify tracks with your audio feature extraction
"""

from spotify_integration import get_spotify_client
from feature_extraction import extract_features  # Your feature extraction
import json

def spotify_powered_recommendations():
    """
    Complete workflow: Search Spotify → Get Audio Features → Generate Recommendations
    """
    
    print("=" * 70)
    print("🎵 SPOTIFY + MUSIC AI RECOMMENDATION WORKFLOW")
    print("=" * 70)
    
    # Initialize Spotify client
    spotify = get_spotify_client()
    
    if not spotify.is_connected():
        print("\n❌ Spotify API not connected!")
        print("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables")
        return
    
    print("\n✅ Spotify API connected\n")
    
    # Step 1: Search for seed tracks
    print("Step 1: Searching for seed tracks...")
    search_query = "lo-fi beats"
    seed_tracks = spotify.search_tracks(search_query, limit=5)
    
    print(f"Found {len(seed_tracks)} tracks matching '{search_query}'")
    for i, track in enumerate(seed_tracks, 1):
        print(f"  {i}. {track['name']} by {track['artist']}")
    
    # Step 2: Get audio features for seed tracks
    print("\nStep 2: Analyzing audio features of seed tracks...")
    seed_features = {}
    
    for track in seed_tracks:
        features = spotify.get_audio_features(track['id'])
        if features:
            seed_features[track['id']] = {
                'name': track['name'],
                'artist': track['artist'],
                'features': features
            }
            
            print(f"\n  📊 {track['name']}")
            print(f"     Energy: {features['energy']:.2f}")
            print(f"     Danceability: {features['danceability']:.2f}")
            print(f"     Valence: {features['valence']:.2f}")
    
    # Step 3: Calculate average audio features
    print("\nStep 3: Calculating average audio characteristics...")
    avg_features = calculate_average_features(seed_features)
    
    print("\nAverage characteristics of seed tracks:")
    print(f"  Energy: {avg_features['energy']:.2f}")
    print(f"  Danceability: {avg_features['danceability']:.2f}")
    print(f"  Valence: {avg_features['valence']:.2f}")
    print(f"  Acousticness: {avg_features['acousticness']:.2f}")
    print(f"  Tempo: {avg_features['tempo']:.0f} BPM")
    
    # Step 4: Get recommendations from Spotify
    print("\nStep 4: Getting personalized recommendations from Spotify...")
    recommendations = spotify.get_recommendations(
        seed_tracks=[t['id'] for t in seed_tracks[:2]],  # Use first 2 as seeds
        limit=10
    )
    
    print(f"Found {len(recommendations)} recommendations:")
    
    # Step 5: Analyze recommended tracks
    print("\nStep 5: Analyzing recommended tracks...")
    recommendation_analysis = []
    
    for i, track in enumerate(recommendations, 1):
        features = spotify.get_audio_features(track['id'])
        
        if features:
            # Calculate similarity to seed characteristics
            similarity = calculate_similarity(features, avg_features)
            
            recommendation_analysis.append({
                'rank': i,
                'track': track['name'],
                'artist': track['artist'],
                'popularity': track['popularity'],
                'similarity': similarity,
                'features': features
            })
            
            print(f"\n  {i}. {track['name']} by {track['artist']}")
            print(f"     Popularity: {track['popularity']}/100")
            print(f"     Similarity: {similarity:.2%}")
    
    # Step 6: Rank recommendations by similarity
    print("\nStep 6: Ranking recommendations by similarity...")
    recommendation_analysis.sort(key=lambda x: x['similarity'], reverse=True)
    
    print("\nTop recommendations (by similarity to seed tracks):")
    for rec in recommendation_analysis[:5]:
        print(f"  {rec['rank']}. {rec['track']} - {rec['similarity']:.2%} match")
    
    # Step 7: Export results
    print("\nStep 7: Exporting results...")
    export_recommendations(recommendation_analysis, avg_features)
    
    print("\n✅ Workflow complete!")
    print("Results saved to 'spotify_recommendations_output.json'")

def calculate_average_features(seed_features_dict):
    """Calculate average audio features from seed tracks"""
    
    if not seed_features_dict:
        return {}
    
    feature_keys = ['energy', 'danceability', 'valence', 'acousticness', 
                   'instrumentalness', 'liveness', 'speechiness', 'tempo']
    
    averages = {}
    
    for key in feature_keys:
        values = []
        for track_data in seed_features_dict.values():
            if key in track_data['features']:
                values.append(track_data['features'][key])
        
        if values:
            averages[key] = sum(values) / len(values)
    
    return averages

def calculate_similarity(track_features, target_features):
    """
    Calculate similarity between track and target features (0-1)
    Based on Euclidean distance
    """
    
    feature_keys = ['energy', 'danceability', 'valence', 'acousticness']
    
    sum_squared_diff = 0
    count = 0
    
    for key in feature_keys:
        if key in track_features and key in target_features:
            diff = track_features[key] - target_features[key]
            sum_squared_diff += diff ** 2
            count += 1
    
    if count == 0:
        return 0
    
    # Normalize to 0-1 range
    mse = sum_squared_diff / count
    distance = mse ** 0.5  # RMSE
    similarity = max(0, 1 - distance)
    
    return similarity

def export_recommendations(recommendations, avg_features):
    """Export recommendations to JSON file"""
    
    export_data = {
        'seed_characteristics': avg_features,
        'recommendations': recommendations,
        'total_count': len(recommendations),
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }
    
    with open('spotify_recommendations_output.json', 'w') as f:
        json.dump(export_data, f, indent=2)

def spotify_to_recommendation_pipeline(user_input):
    """
    Full pipeline: User input → Spotify search → Feature analysis → Recommendations
    
    Args:
        user_input: String (e.g., "lo-fi", "happy music", "workout songs")
    """
    
    print(f"\n🎵 Creating recommendation playlist for: '{user_input}'")
    print("=" * 70)
    
    spotify = get_spotify_client()
    
    if not spotify.is_connected():
        print("❌ Spotify not connected")
        return
    
    # Search for initial tracks
    initial_tracks = spotify.search_tracks(user_input, limit=3)
    
    if not initial_tracks:
        print(f"No tracks found for '{user_input}'")
        return
    
    print(f"\n✅ Found {len(initial_tracks)} initial tracks")
    
    # Get features and recommendations
    recommendations = spotify.get_recommendations(
        seed_tracks=[t['id'] for t in initial_tracks],
        limit=20
    )
    
    print(f"✅ Generated {len(recommendations)} recommendations")
    
    # Display results
    print("\n📋 Recommended Playlist:")
    print("-" * 70)
    for i, track in enumerate(recommendations, 1):
        print(f"{i:2d}. {track['name']:<40} | {track['artist']}")
    
    return recommendations

def create_mixed_recommendation(genres, artists, tracks):
    """
    Create recommendations using multiple seed types
    
    Args:
        genres: List of genre strings (max 5)
        artists: List of artist search terms (max 5, will use first one's ID)
        tracks: List of track search terms (max 5, will use first one's ID)
    """
    
    spotify = get_spotify_client()
    
    if not spotify.is_connected():
        print("❌ Spotify not connected")
        return
    
    seed_track_ids = []
    seed_artist_ids = []
    
    # Get IDs for tracks
    for track_name in tracks[:5]:
        found_tracks = spotify.search_tracks(track_name, limit=1)
        if found_tracks:
            seed_track_ids.append(found_tracks[0]['id'])
    
    # Get IDs for artists
    for artist_name in artists[:5]:
        found_artists = spotify.search_artists(artist_name, limit=1)
        if found_artists:
            seed_artist_ids.append(found_artists[0]['id'])
    
    # Get recommendations
    recommendations = spotify.get_recommendations(
        seed_tracks=seed_track_ids if seed_track_ids else None,
        seed_artists=seed_artist_ids if seed_artist_ids else None,
        seed_genres=genres[:5] if genres else None,
        limit=20
    )
    
    print(f"\n✅ Generated {len(recommendations)} mixed recommendations")
    print(f"   Genres: {', '.join(genres[:3])}")
    print(f"   Artists: {', '.join(artists[:2])}")
    print(f"   Seed Tracks: {len(seed_track_ids)}")
    print(f"   Seed Artists: {len(seed_artist_ids)}")
    
    return recommendations

# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "=" * 70)
    print("🎵 SPOTIFY + MUSIC AI INTEGRATION EXAMPLES")
    print("=" * 70)
    
    # Example 1: Full workflow
    print("\n--- Example 1: Full Workflow ---")
    spotify_powered_recommendations()
    
    # Example 2: User input pipeline
    print("\n\n--- Example 2: User Input Pipeline ---")
    spotify_to_recommendation_pipeline("ambient chill")
    
    # Example 3: Mixed recommendation
    print("\n\n--- Example 3: Mixed Recommendation ---")
    mixed_recs = create_mixed_recommendation(
        genres=['lo-fi', 'ambient'],
        artists=['Dua Lipa'],
        tracks=['Blinding Lights']
    )
    
    if mixed_recs:
        print("\nTop 5 recommendations:")
        for i, track in enumerate(mixed_recs[:5], 1):
            print(f"  {i}. {track['name']} by {track['artist']}")
    
    print("\n" + "=" * 70)
    print("✅ Examples complete!")
    print("=" * 70 + "\n")
