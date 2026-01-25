"""
Embedding Generation & Recommendation Engine
Hybrid approach: hand-crafted features + pre-trained neural components
"""

import numpy as np
import torch
import torch.nn as nn
from typing import List, Tuple, Dict
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import faiss


# ============================================================================
# PART A: FEATURE-BASED EMBEDDINGS (Interpretable)
# ============================================================================

class FeatureBasedEmbedding:
    """
    Converts hand-crafted audio features to dense embeddings via PCA.
    Fully interpretable: you can see which features contributed.
    """
    
    def __init__(self, n_components: int = 32):
        """
        Args:
            n_components: Embedding dimensionality (32-128 typical)
        """
        self.n_components = n_components
        self.pca = None
        self.scaler = StandardScaler()
        self.feature_names = [
            "MFCC_0", "MFCC_1", "MFCC_2", "MFCC_3", "MFCC_4", "MFCC_5",
            "MFCC_6", "MFCC_7", "MFCC_8", "MFCC_9", "MFCC_10", "MFCC_11",
            "MFCC_12", "MFCC_13", "MFCC_14", "MFCC_15", "MFCC_16", "MFCC_17",
            "MFCC_18", "MFCC_19", "MFCC_STD_0", "MFCC_STD_1", "MFCC_STD_2",
            "MFCC_STD_3", "MFCC_STD_4", "MFCC_STD_5", "MFCC_STD_6",
            "MFCC_STD_7", "MFCC_STD_8", "MFCC_STD_9", "MFCC_STD_10",
            "MFCC_STD_11", "MFCC_STD_12", "MFCC_STD_13", "MFCC_STD_14",
            "MFCC_STD_15", "MFCC_STD_16", "MFCC_STD_17", "MFCC_STD_18",
            "MFCC_STD_19", "Chroma_0", "Chroma_1", "Chroma_2", "Chroma_3",
            "Chroma_4", "Chroma_5", "Chroma_6", "Chroma_7", "Chroma_8",
            "Chroma_9", "Chroma_10", "Chroma_11", "Spectral_Centroid",
            "Spectral_Rolloff", "RMS_Mean", "RMS_Std", "ZCR", "Tempo",
            "Rhythm_Stability", "Spectral_Contrast_0", "Spectral_Contrast_1",
            "Spectral_Contrast_2", "Spectral_Contrast_3", "Spectral_Contrast_4",
            "Spectral_Contrast_5", "Spectral_Contrast_6"
        ]
    
    def fit(self, features_array: np.ndarray) -> 'FeatureBasedEmbedding':
        """
        Fit PCA on training data.
        
        Args:
            features_array: Array of shape (n_songs, n_features)
        """
        # Normalize
        features_normalized = self.scaler.fit_transform(features_array)
        
        # Fit PCA
        self.pca = PCA(n_components=self.n_components)
        self.pca.fit(features_normalized)
        
        explained_var = np.sum(self.pca.explained_variance_ratio_)
        print(f"PCA: {self.n_components} components explain {explained_var:.1%} variance")
        
        return self
    
    def transform(self, features_array: np.ndarray) -> np.ndarray:
        """
        Convert features to embeddings.
        
        Args:
            features_array: Shape (n_songs, n_features)
            
        Returns:
            embeddings: Shape (n_songs, n_components)
        """
        features_normalized = self.scaler.transform(features_array)
        embeddings = self.pca.transform(features_normalized)
        return embeddings
    
    def get_feature_importance(self, embedding_index: int) -> List[Tuple[str, float]]:
        """
        Which original features contributed most to this embedding component?
        
        Args:
            embedding_index: Which embedding dimension (0 to n_components-1)
            
        Returns:
            List of (feature_name, importance) tuples, sorted by importance
        """
        loadings = np.abs(self.pca.components_[embedding_index])
        importance = list(zip(self.feature_names, loadings))
        importance.sort(key=lambda x: x[1], reverse=True)
        return importance


# ============================================================================
# PART B: NEURAL EMBEDDINGS (Pre-trained)
# ============================================================================

class MusicEmbeddingNetwork(nn.Module):
    """
    Pre-trained neural network for music embeddings.
    Uses Mel-spectrogram as input (similar to what audio models see).
    """
    
    def __init__(self, embedding_dim: int = 128):
        super().__init__()
        
        # CNN layers to process mel-spectrogram
        self.conv_layers = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1)  # Global average pooling
        )
        
        # Embedding projection
        self.embedding_layer = nn.Linear(128, embedding_dim)
        self.embedding_dim = embedding_dim
    
    def forward(self, mel_spec: torch.Tensor) -> torch.Tensor:
        """
        Args:
            mel_spec: Mel-spectrogram of shape (batch, 1, n_mels, n_frames)
                      e.g., (32, 1, 128, 2048)
        
        Returns:
            embedding: Shape (batch, embedding_dim)
        """
        # CNN feature extraction
        features = self.conv_layers(mel_spec)  # (batch, 128, 1, 1)
        features = features.view(features.size(0), -1)  # (batch, 128)
        
        # Project to embedding space
        embedding = self.embedding_layer(features)  # (batch, embedding_dim)
        
        # L2 normalize for cosine similarity
        embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)
        
        return embedding


# ============================================================================
# PART C: HYBRID EMBEDDING SYSTEM
# ============================================================================

class HybridMusicEmbedding:
    """
    Combines:
    1. Hand-crafted features (interpretable) → PCA → 32D
    2. Neural embeddings (semantic) → 128D
    Total: 160D embedding
    
    This gives both interpretability and deep semantic understanding.
    """
    
    def __init__(self, 
                 hand_crafted_dim: int = 32,
                 neural_dim: int = 128,
                 device: str = "cpu"):
        """
        Args:
            hand_crafted_dim: Dimensionality of hand-crafted component
            neural_dim: Dimensionality of neural component
            device: "cpu" or "cuda"
        """
        self.hand_crafted_dim = hand_crafted_dim
        self.neural_dim = neural_dim
        self.device = device
        self.total_dim = hand_crafted_dim + neural_dim
        
        # Initialize components
        self.hand_crafted = FeatureBasedEmbedding(hand_crafted_dim)
        self.neural_network = MusicEmbeddingNetwork(neural_dim).to(device)
        self.neural_network.eval()  # Evaluation mode
        
        self.is_fitted = False
    
    def fit(self, features_array: np.ndarray) -> 'HybridMusicEmbedding':
        """
        Fit hand-crafted component.
        Neural network is assumed to be pre-trained.
        
        Args:
            features_array: Shape (n_songs, n_features)
        """
        self.hand_crafted.fit(features_array)
        self.is_fitted = True
        return self
    
    def embed(self, 
              features_array: np.ndarray,
              mel_spectrograms: List[np.ndarray] = None) -> np.ndarray:
        """
        Generate hybrid embeddings.
        
        Args:
            features_array: Hand-crafted features (n_songs, n_features)
            mel_spectrograms: Optional mel-spectrograms for neural component
                            Each shape (n_mels, n_frames), e.g., (128, 2048)
        
        Returns:
            embeddings: Shape (n_songs, total_dim)
        """
        if not self.is_fitted:
            raise RuntimeError("Must call fit() first")
        
        # Hand-crafted component
        hand_crafted_emb = self.hand_crafted.transform(features_array)
        # Shape: (n_songs, hand_crafted_dim)
        
        # Neural component
        if mel_spectrograms is not None:
            neural_emb = self._embed_spectrograms(mel_spectrograms)
        else:
            # Fallback: use zeros (in production, spectrograms should be provided)
            neural_emb = np.zeros((features_array.shape[0], self.neural_dim))
        
        # Concatenate
        hybrid_emb = np.hstack([hand_crafted_emb, neural_emb])
        
        return hybrid_emb
    
    def _embed_spectrograms(self, mel_specs: List[np.ndarray]) -> np.ndarray:
        """
        Get neural embeddings from mel-spectrograms.
        
        Args:
            mel_specs: List of mel-spectrograms
        
        Returns:
            embeddings: Shape (n_songs, neural_dim)
        """
        embeddings = []
        
        with torch.no_grad():
            for mel_spec in mel_specs:
                # Prepare input: (1, n_mels, n_frames) → (1, 1, n_mels, n_frames)
                mel_tensor = torch.tensor(mel_spec, dtype=torch.float32)
                mel_tensor = mel_tensor.unsqueeze(0).unsqueeze(0)  # Add batch and channel dims
                mel_tensor = mel_tensor.to(self.device)
                
                # Forward pass
                embedding = self.neural_network(mel_tensor).cpu().numpy()
                embeddings.append(embedding.squeeze())
        
        return np.array(embeddings)


# ============================================================================
# PART D: FAISS INDEX FOR SIMILARITY SEARCH
# ============================================================================

class FAISSIndex:
    """
    Fast similarity search using Facebook's FAISS library.
    Enables finding k nearest neighbors in O(log n) time.
    """
    
    def __init__(self, embedding_dim: int = 160):
        """
        Args:
            embedding_dim: Dimensionality of embeddings
        """
        self.embedding_dim = embedding_dim
        # IndexFlatIP: Inner Product (equivalent to cosine similarity after normalization)
        self.index = faiss.IndexFlatIP(embedding_dim)
        self.song_ids = []  # Track which song is at which index
    
    def add_embeddings(self, embeddings: np.ndarray, song_ids: List[str]) -> None:
        """
        Add embeddings to index.
        
        Args:
            embeddings: Shape (n_songs, embedding_dim), already normalized
            song_ids: List of song identifiers
        """
        # Ensure float32 and normalize for cosine similarity
        embeddings = embeddings.astype(np.float32)
        faiss.normalize_L2(embeddings)
        
        self.index.add(embeddings)
        self.song_ids.extend(song_ids)
    
    def search(self, query_embedding: np.ndarray, k: int = 10) -> Tuple[np.ndarray, List[str]]:
        """
        Find k nearest neighbors.
        
        Args:
            query_embedding: Shape (1, embedding_dim)
            k: Number of neighbors to return
        
        Returns:
            distances: Array of shape (1, k) with similarity scores [0, 1]
            song_ids: List of k nearest song IDs
        """
        query = query_embedding.astype(np.float32).reshape(1, -1)
        faiss.normalize_L2(query)
        
        distances, indices = self.index.search(query, k)
        
        nearest_song_ids = [self.song_ids[idx] for idx in indices[0]]
        
        return distances[0], nearest_song_ids
    
    def save(self, path: str) -> None:
        """Save index to disk"""
        faiss.write_index(self.index, path)
    
    def load(self, path: str) -> None:
        """Load index from disk"""
        self.index = faiss.read_index(path)


# ============================================================================
# PART E: RECOMMENDATION ENGINE
# ============================================================================

class RecommendationEngine:
    """
    Generates personalized recommendations using embedding similarity.
    Implements:
    - Content-based filtering (similar to songs user liked)
    - Collaborative filtering (user preference vector)
    - Diversity via Maximum Marginal Relevance (MMR)
    """
    
    def __init__(self, faiss_index: FAISSIndex):
        """
        Args:
            faiss_index: Initialized FAISS index with all song embeddings
        """
        self.faiss_index = faiss_index
    
    def get_user_preference_vector(self,
                                   liked_song_embeddings: List[np.ndarray],
                                   weights: List[float] = None) -> np.ndarray:
        """
        Compute user preference as weighted average of liked songs.
        
        Args:
            liked_song_embeddings: Embeddings of songs user liked
            weights: Optional weights (e.g., by rating or recency)
                    Default: equal weight
        
        Returns:
            preference_vector: Synthetic embedding representing user taste
        """
        liked_songs = np.array(liked_song_embeddings)
        
        if weights is None:
            preference = np.mean(liked_songs, axis=0)
        else:
            weights = np.array(weights) / np.sum(weights)  # Normalize
            preference = np.average(liked_songs, axis=0, weights=weights)
        
        # Normalize
        preference = preference / np.linalg.norm(preference)
        
        return preference
    
    def recommend_content_based(self,
                               user_preference: np.ndarray,
                               num_recommendations: int = 10,
                               exclude_song_ids: List[str] = None) -> List[Dict]:
        """
        Recommend songs similar to user preference.
        
        Args:
            user_preference: User preference embedding (160D)
            num_recommendations: How many to return
            exclude_song_ids: Song IDs to exclude (already liked)
        
        Returns:
            recommendations: List of dicts with song_id and similarity_score
        """
        exclude_set = set(exclude_song_ids or [])
        
        # Search FAISS (get more to filter)
        distances, song_ids = self.faiss_index.search(
            user_preference.reshape(1, -1),
            k=num_recommendations * 3
        )
        
        recommendations = []
        for dist, song_id in zip(distances, song_ids):
            if song_id not in exclude_set:
                recommendations.append({
                    "song_id": song_id,
                    "similarity_score": float(dist)
                })
                if len(recommendations) >= num_recommendations:
                    break
        
        return recommendations
    
    def maximize_marginal_relevance(self,
                                   user_preference: np.ndarray,
                                   candidate_embeddings: Dict[str, np.ndarray],
                                   num_recommendations: int = 10,
                                   lambda_diversity: float = 0.6) -> List[str]:
        """
        Avoid recommending similar songs. Use MMR to balance relevance + diversity.
        
        MMR = λ * Relevance(S) - (1-λ) * max_diversity(S)
        
        Args:
            user_preference: User embedding
            candidate_embeddings: Dict of {song_id: embedding}
            num_recommendations: Number to return
            lambda_diversity: Trade-off (0=pure diversity, 1=pure relevance)
        
        Returns:
            song_ids: Ordered list of diverse, relevant recommendations
        """
        recommendations = []
        candidates_remaining = set(candidate_embeddings.keys())
        
        for _ in range(num_recommendations):
            if not candidates_remaining:
                break
            
            best_song = None
            best_score = float('-inf')
            
            for song_id in candidates_remaining:
                # Relevance: similarity to user preference
                embedding = candidate_embeddings[song_id]
                relevance = np.dot(user_preference, embedding)  # Cosine similarity
                
                # Diversity: minimum similarity to already selected
                if recommendations:
                    diversity_penalty = min(
                        np.dot(embedding, candidate_embeddings[rec_id])
                        for rec_id in recommendations
                    )
                else:
                    diversity_penalty = 0
                
                # MMR score
                mmr_score = lambda_diversity * relevance - (1 - lambda_diversity) * diversity_penalty
                
                if mmr_score > best_score:
                    best_song = song_id
                    best_score = mmr_score
            
            if best_song:
                recommendations.append(best_song)
                candidates_remaining.remove(best_song)
        
        return recommendations


# ============================================================================
# Example Usage
# ============================================================================

def example_workflow():
    """Demonstrates the full embedding and recommendation pipeline"""
    
    # 1. Create hybrid embedding system
    hybrid = HybridMusicEmbedding(hand_crafted_dim=32, neural_dim=128)
    
    # 2. Fit on training features (from feature_extraction.py)
    # (In real code, you'd load actual feature arrays)
    dummy_features = np.random.randn(1000, 67)  # 67 hand-crafted features
    hybrid.fit(dummy_features)
    
    # 3. Generate embeddings
    test_features = np.random.randn(500, 67)
    embeddings = hybrid.embed(test_features)
    print(f"Generated embeddings shape: {embeddings.shape}")  # Should be (500, 160)
    
    # 4. Build FAISS index
    faiss_idx = FAISSIndex(embedding_dim=160)
    song_ids = [f"song_{i}" for i in range(500)]
    faiss_idx.add_embeddings(embeddings, song_ids)
    print(f"FAISS index built with {len(song_ids)} songs")
    
    # 5. Recommend for a user
    engine = RecommendationEngine(faiss_idx)
    
    # User liked songs 0, 5, 10
    liked_embeddings = [embeddings[i] for i in [0, 5, 10]]
    user_pref = engine.get_user_preference_vector(liked_embeddings)
    
    # Get recommendations
    recommendations = engine.recommend_content_based(
        user_pref,
        num_recommendations=10,
        exclude_song_ids=["song_0", "song_5", "song_10"]
    )
    
    print("\nTop 5 Recommendations:")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"{i}. {rec['song_id']}: similarity {rec['similarity_score']:.3f}")


if __name__ == "__main__":
    example_workflow()
