"""
Audio Feature Extraction Pipeline
Complete implementation with all signal processing steps
"""

import numpy as np
import librosa
import librosa.display
from typing import Dict, Tuple, List
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler


@dataclass
class AudioFeatures:
    """Container for extracted audio features"""
    mfcc: np.ndarray
    chroma: np.ndarray
    spectral_centroid: float
    spectral_rolloff: float
    rms_energy: float
    zcr: float
    tempo: float
    rhythm_stability: float
    spectral_contrast: np.ndarray
    duration: float
    
    def to_vector(self) -> np.ndarray:
        """Convert all features to single 1D vector"""
        # Flatten all arrays to handle multi-dimensional features
        mfcc_flat = self.mfcc.flatten() if isinstance(self.mfcc, np.ndarray) else np.array([self.mfcc])
        chroma_flat = self.chroma.flatten() if isinstance(self.chroma, np.ndarray) else np.array([self.chroma])
        contrast_flat = self.spectral_contrast.flatten() if isinstance(self.spectral_contrast, np.ndarray) else np.array([self.spectral_contrast])
        
        return np.concatenate([
            mfcc_flat,                    # 20 dims
            chroma_flat,                  # 12 dims
            [self.spectral_centroid],     # 1 dim
            [self.spectral_rolloff],      # 1 dim
            [self.rms_energy],            # 1 dim
            [self.zcr],                   # 1 dim
            [self.tempo] if np.isscalar(self.tempo) else np.array([self.tempo[0] if len(self.tempo) > 0 else 0]),  # 1 dim
            [self.rhythm_stability],      # 1 dim
            contrast_flat                 # 7 dims
        ])  # Total: ~46 dims (will expand to 73 with statistics)


class AudioFeatureExtractor:
    """
    Extracts comprehensive audio features from raw audio files.
    
    Features extracted:
    - Mel-Frequency Cepstral Coefficients (MFCCs): Timbral quality
    - Chroma Features: Harmonic content (12 pitch classes)
    - Spectral Features: Frequency distribution and brightness
    - Temporal Features: Energy and rhythmic characteristics
    - Rhythm Features: Tempo and beat stability
    """
    
    def __init__(self, sr: int = 22050, n_mfcc: int = 20):
        """
        Initialize extractor.
        
        Args:
            sr: Sample rate (Hz). 22050 Hz is standard for librosa
            n_mfcc: Number of MFCC coefficients (13-40 typical)
        """
        self.sr = sr
        self.n_mfcc = n_mfcc
        self.scaler = StandardScaler()
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file with validation.
        
        Args:
            file_path: Path to audio file (.mp3, .wav, .flac, etc.)
            
        Returns:
            y: Audio waveform (1D array of amplitudes)
            sr: Sample rate (Hz)
        """
        try:
            # Load audio, converting to mono if necessary
            y, sr = librosa.load(file_path, sr=self.sr, mono=True)
            
            # Validate
            duration = len(y) / sr
            if duration < 10:
                raise ValueError(f"Audio too short: {duration}s (min: 10s)")
            if duration > 3600:
                raise ValueError(f"Audio too long: {duration}s (max: 1 hour)")
            
            return y, sr
        except Exception as e:
            raise RuntimeError(f"Failed to load audio: {str(e)}")
    
    def normalize_audio(self, y: np.ndarray) -> np.ndarray:
        """
        Normalize audio amplitude to [-1, 1] range.
        Prevents issues from very quiet or very loud files.
        """
        max_val = np.max(np.abs(y))
        if max_val > 0:
            y = y / max_val
        return y
    
    def extract_mfcc(self, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract MFCC (Mel-Frequency Cepstral Coefficients).
        
        Mimics human hearing by using mel-scale (logarithmic pitch scale).
        Each coefficient captures different spectral aspects.
        
        Returns:
            mfcc_mean: Average MFCC over time (n_mfcc,)
            mfcc_std: Standard deviation over time (n_mfcc,)
        """
        mfcc = librosa.feature.mfcc(y=y, sr=self.sr, n_mfcc=self.n_mfcc)
        # Shape: (n_mfcc, n_frames)
        
        mfcc_mean = np.mean(mfcc, axis=1)    # (n_mfcc,)
        mfcc_std = np.std(mfcc, axis=1)      # (n_mfcc,)
        
        return mfcc_mean, mfcc_std
    
    def extract_chroma(self, y: np.ndarray) -> np.ndarray:
        """
        Extract chroma features (pitch classes).
        
        Captures harmonic content by summing energy of each pitch class:
        C, C#, D, D#, E, F, F#, G, G#, A, A#, B
        
        Returns:
            chroma_mean: Average chroma vector (12,)
        """
        # CQT (Constant-Q Transform) is better than STFT for music pitch
        chroma = librosa.feature.chroma_cqt(y=y, sr=self.sr)
        # Shape: (12, n_frames)
        
        chroma_mean = np.mean(chroma, axis=1)  # (12,)
        
        return chroma_mean
    
    def extract_spectral_features(self, y: np.ndarray) -> Tuple[float, float]:
        """
        Extract spectral centroid and rolloff.
        
        Spectral Centroid: Center of mass in frequency domain.
        High = bright timbre, Low = dark timbre
        
        Spectral Rolloff: Frequency below which 85% of energy is concentrated.
        High = harsh, Low = smooth
        
        Returns:
            spectral_centroid_mean: Mean spectral centroid (Hz)
            spectral_rolloff_mean: Mean spectral rolloff (Hz)
        """
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=self.sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=self.sr)
        
        return (
            np.mean(spectral_centroid),
            np.mean(spectral_rolloff)
        )
    
    def extract_energy(self, y: np.ndarray) -> Tuple[float, float]:
        """
        Extract RMS energy and zero-crossing rate.
        
        RMS Energy: Loudness/amplitude variation over time.
        High = loud/energetic, Low = quiet/calm
        
        Zero-Crossing Rate: How often signal crosses zero (indicates high freq content).
        High = noisy/fricative, Low = pitched/harmonic
        
        Returns:
            rms_mean: Mean RMS energy
            rms_std: Std dev of RMS energy
            zcr_mean: Mean zero-crossing rate
        """
        rms = librosa.feature.rms(y=y)
        zcr = librosa.feature.zero_crossing_rate(y)
        
        return (
            np.mean(rms),
            np.std(rms),
            np.mean(zcr)
        )
    
    def extract_tempo_and_rhythm(self, y: np.ndarray) -> Tuple[float, float]:
        """
        Extract tempo and rhythm stability.
        
        Tempo: Beats per minute (BPM).
        Calculated from onset detection (where new sounds begin).
        
        Rhythm Stability: Consistency of the beat (tempogram energy).
        High = metronomic/steady, Low = syncopated/polyrhythmic
        
        Returns:
            tempo: Tempo in BPM
            rhythm_stability: Normalized tempogram energy [0, 1]
        """
        # Onset strength: likelihood of new sound starting
        onset_env = librosa.onset.onset_strength(y=y, sr=self.sr)
        
        # Estimate tempo from onset
        tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=self.sr)
        
        # Tempogram: strength of different tempos
        tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=self.sr)
        rhythm_stability = np.mean(tempogram)  # 0-1 scale
        
        # Normalize tempo to reasonable range
        tempo = np.clip(tempo, 30, 300)  # Most music is 30-300 BPM
        
        return tempo, rhythm_stability
    
    def extract_spectral_contrast(self, y: np.ndarray) -> np.ndarray:
        """
        Extract spectral contrast (brightness across bands).
        
        Divides spectrum into 7 frequency bands and measures
        the contrast within each band.
        
        Returns:
            spectral_contrast_mean: Mean contrast per band (7,)
        """
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=self.sr)
        # Shape: (7, n_frames)
        
        return np.mean(spectral_contrast, axis=1)  # (7,)
    
    def extract_all_features(self, file_path: str) -> AudioFeatures:
        """
        Main extraction pipeline.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            AudioFeatures object with all extracted features
        """
        # Load and validate
        y, sr = self.load_audio(file_path)
        duration = len(y) / sr
        
        # Normalize amplitude
        y = self.normalize_audio(y)
        
        # Extract all feature groups
        mfcc_mean, mfcc_std = self.extract_mfcc(y)
        chroma = self.extract_chroma(y)
        spec_cent, spec_roll = self.extract_spectral_features(y)
        rms_mean, rms_std, zcr = self.extract_energy(y)
        tempo, rhythm_stab = self.extract_tempo_and_rhythm(y)
        spec_contrast = self.extract_spectral_contrast(y)
        
        # Create features object
        # Include both mean and std for temporal statistics
        features = AudioFeatures(
            mfcc=np.concatenate([mfcc_mean, mfcc_std]),  # 40 dims
            chroma=chroma,                               # 12 dims
            spectral_centroid=spec_cent,                 # 1 dim
            spectral_rolloff=spec_roll,                  # 1 dim
            rms_energy=rms_mean,                         # 1 dim
            zcr=zcr,                                     # 1 dim
            tempo=tempo,                                 # 1 dim
            rhythm_stability=rhythm_stab,                # 1 dim
            spectral_contrast=spec_contrast,             # 7 dims
            duration=duration
        )
        
        return features
    
    def extract_all_features_from_signal(self, y: np.ndarray, sr: int) -> AudioFeatures:
        """
        Extract features directly from audio signal (numpy array).
        
        Args:
            y: Audio time series (1D numpy array)
            sr: Sample rate
            
        Returns:
            AudioFeatures object with all extracted features
        """
        duration = len(y) / sr
        
        # Normalize amplitude
        y = self.normalize_audio(y)
        
        # Extract all feature groups
        mfcc_mean, mfcc_std = self.extract_mfcc(y)
        chroma = self.extract_chroma(y)
        spec_cent, spec_roll = self.extract_spectral_features(y)
        rms_mean, rms_std, zcr = self.extract_energy(y)
        tempo, rhythm = self.extract_tempo_and_rhythm(y)
        spec_contrast = self.extract_spectral_contrast(y)
        
        # Create features object
        features = AudioFeatures(
            mfcc=mfcc_mean,
            chroma=chroma,
            spectral_centroid=spec_cent,
            spectral_rolloff=spec_roll,
            rms_energy=rms_mean,
            zcr=zcr,
            tempo=tempo,
            rhythm_stability=rhythm,
            spectral_contrast=spec_contrast,
            duration=duration
        )
        
        return features
    
    def get_feature_vector(self, file_path: str) -> np.ndarray:
        """
        Extract and return as single vector.
        
        Returns:
            features: 1D array of ~67 features (normalized to [0,1])
        """
        features = self.extract_all_features(file_path)
        vector = features.to_vector()
        
        # Normalize using standard scaler
        # In production, use a pre-fitted scaler from training data
        vector_normalized = self.scaler.fit_transform(vector.reshape(1, -1))
        
        return vector_normalized.flatten()


# ============================================================================
# Example Usage
# ============================================================================

def main():
    """Demonstrate feature extraction with synthetic audio"""
    
    # Initialize extractor
    extractor = AudioFeatureExtractor(sr=22050, n_mfcc=20)
    
    print("\n" + "=" * 70)
    print("🎵 AUDIO FEATURE EXTRACTION DEMO")
    print("=" * 70)
    print("\n📝 Creating synthetic audio for demonstration...")
    
    # Generate synthetic audio (musical tone)
    sr = 22050
    duration = 5
    t = np.linspace(0, duration, sr * duration)
    
    # Create synthesized audio: A4 note (440 Hz) with harmonics
    frequency = 440
    y = (np.sin(2 * np.pi * frequency * t) +
         0.5 * np.sin(2 * np.pi * frequency * 2 * t) +
         0.3 * np.sin(2 * np.pi * frequency * 3 * t))
    
    # Add envelope and noise
    envelope = np.sin(np.pi * t / duration) ** 0.5
    y = y * envelope * 0.5 + 0.05 * np.random.randn(len(y))
    
    print("✅ Synthetic audio created!")
    
    try:
        print("🔍 Extracting features...")
        features = extractor.extract_all_features_from_signal(y, sr)
        print("✅ Features extracted!\n")
        
        # Print results
        print("=" * 70)
        print("📊 EXTRACTED FEATURES")
        print("=" * 70)
        print(f"  Duration:              {features.duration:.2f} seconds")
        
        # Handle tempo (could be array or float)
        tempo_val = float(features.tempo[0]) if hasattr(features.tempo, '__len__') and len(features.tempo) > 0 else float(features.tempo)
        print(f"  Tempo:                 {tempo_val:.1f} BPM")
        
        print(f"  Energy (RMS):          {features.rms_energy:.4f}")
        print(f"  Spectral Centroid:     {features.spectral_centroid:.0f} Hz")
        print(f"  Spectral Rolloff:      {features.spectral_rolloff:.0f} Hz")
        print(f"  Zero Crossing Rate:    {features.zcr:.4f}")
        print(f"  Harmonic Energy:       {np.sum(features.chroma):.4f}")
        print(f"  Rhythm Stability:      {features.rhythm_stability:.4f}")
        
        # Get as vector
        feature_vector = features.to_vector()
        print(f"\n  Feature Vector Dimensions: {len(feature_vector)}")
        print(f"  Feature Vector Shape:      {feature_vector.shape}")
        print(f"  First 10 features:     {feature_vector[:10]}")
        print("=" * 70)
        print("✅ Feature extraction complete!\n")
        
    except Exception as e:
        print(f"❌ Error during feature extraction: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
