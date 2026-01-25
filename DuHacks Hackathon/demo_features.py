"""
Quick Demo: Audio Feature Extraction with Synthetic Audio
No file loading - just numpy-based feature extraction
"""

import numpy as np
from feature_extraction import AudioFeatureExtractor

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

# Extract features
extractor = AudioFeatureExtractor(sr=sr, n_mfcc=20)

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
    tempo_val = float(features.tempo) if hasattr(features.tempo, '__len__') else features.tempo
    print(f"  Tempo:                 {tempo_val:.1f} BPM")
    
    # Handle rhythm stability (could be array or float)
    rhythm_val = float(features.rhythm_stability) if hasattr(features.rhythm_stability, '__len__') else features.rhythm_stability
    print(f"  Energy (RMS):          {features.rms_energy:.4f}")
    print(f"  Spectral Centroid:     {features.spectral_centroid:.0f} Hz")
    print(f"  Spectral Rolloff:      {features.spectral_rolloff:.0f} Hz")
    print(f"  Zero Crossing Rate:    {features.zcr:.4f}")
    print(f"  Harmonic Energy:       {np.sum(features.chroma):.4f}")
    print(f"  Rhythm Stability:      {rhythm_val:.4f}")
    
    # Get as vector
    feature_vector = features.to_vector()
    print(f"\n  Feature Vector Dimensions: {len(feature_vector)}")
    print(f"  Feature Vector Shape:      {feature_vector.shape}")
    print(f"\n  First 10 features: {feature_vector[:10]}")
    print("=" * 70)
    print("✅ Feature extraction complete!\n")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
