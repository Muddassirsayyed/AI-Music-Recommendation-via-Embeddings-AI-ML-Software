# Complete Setup & Deployment Guide

## Part 1: Local Development Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+ (or use SQLite for dev)
- FFmpeg (for audio processing)

### Step 1: Backend Setup

```bash
# Create project directory
mkdir musicai && cd musicai

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn librosa numpy scipy scikit-learn torch torchaudio faiss-cpu pydantic aiosqlite pydantic[email]

# Optional: GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118  # CUDA 11.8
```

### Step 2: Frontend Setup

```bash
# Create React app
npx create-react-app frontend
cd frontend

# Install dependencies
npm install
npm install -D tailwindcss postcss autoprefixer
npm install lucide-react axios zustand

# Initialize Tailwind
npx tailwindcss init -p

# Update tailwind.config.js with custom colors (see SYSTEM_ARCHITECTURE.md)

# Start dev server
npm start  # Runs on http://localhost:3000
```

### Step 3: Run Backend

```bash
# From project root
python backend_api.py
# API runs on http://localhost:8000
# Swagger docs available at http://localhost:8000/docs
```

---

## Part 2: Database Setup (PostgreSQL)

### Installation

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS (with Homebrew)
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### Initial Configuration

```bash
# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
brew services start postgresql  # macOS

# Create database
createdb musicai_db

# Connect to database
psql musicai_db
```

### Schema Creation

```sql
-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    profile_picture_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Songs table
CREATE TABLE songs (
    song_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255),
    album VARCHAR(255),
    duration_seconds INT,
    file_path TEXT NOT NULL,
    extracted_features JSONB,
    metadata JSONB,
    embedding FLOAT8[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index on embeddings for faster search
CREATE INDEX idx_song_embedding ON songs USING ivfflat (embedding);

-- Listening history
CREATE TABLE listening_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    song_id UUID REFERENCES songs(song_id) ON DELETE CASCADE,
    played_at TIMESTAMP DEFAULT NOW(),
    duration_played_seconds INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    UNIQUE(user_id, song_id, played_at)
);

-- User preferences
CREATE TABLE user_preference_embeddings (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    embedding FLOAT8[] NOT NULL,
    last_updated TIMESTAMP DEFAULT NOW(),
    computed_from_plays INT DEFAULT 0
);

-- Create indexes for performance
CREATE INDEX idx_listening_user ON listening_history(user_id);
CREATE INDEX idx_listening_song ON listening_history(song_id);
CREATE INDEX idx_listening_date ON listening_history(played_at);
```

### Connection String for Backend

```python
# In backend_api.py or config.py
DATABASE_URL = "postgresql://username:password@localhost:5432/musicai_db"

# SQLAlchemy connection (for production)
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL, echo=True)
```

---

## Part 3: FAISS Index Setup

### Installation

```bash
# CPU version (fast on most machines)
pip install faiss-cpu

# GPU version (CUDA 11.4+)
pip install faiss-gpu
```

### Building Index from Songs

```python
# build_index.py
import numpy as np
import faiss
from backend_api import songs_db

def build_faiss_index(output_path="faiss_index"):
    """
    Build and save FAISS index from all song embeddings
    """
    # Collect all embeddings
    embeddings = []
    song_ids = []
    
    for song_id, song_data in songs_db.items():
        if 'embedding' in song_data:
            embeddings.append(np.array(song_data['embedding'], dtype=np.float32))
            song_ids.append(song_id)
    
    embeddings = np.array(embeddings)
    
    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Create index
    index = faiss.IndexFlatIP(embeddings.shape[1])  # Inner Product
    index.add(embeddings)
    
    # Save
    faiss.write_index(index, f"{output_path}.bin")
    
    # Save mapping
    np.save(f"{output_path}_ids.npy", song_ids)
    
    print(f"✅ FAISS index built: {len(song_ids)} songs indexed")

if __name__ == "__main__":
    build_faiss_index()
```

Run: `python build_index.py`

---

## Part 4: Dataset Preparation

### Option A: Use FMA (Free Music Archive)

```bash
# Download FMA dataset
# Small: 8,000 songs (7.2 GB)
# Medium: 25,000 songs (30 GB)
# Full: 106,574 songs (879 GB)

# From: https://github.com/mdeff/fma

# Install FMA library
pip install fma

# Download and extract
python -c "
import fma.utils
fma.utils.download('fma_small')
"
```

### Option B: Use Spotify API

```python
# install_spotify_integration.py
pip install spotipy python-dotenv

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Create .env file with:
# SPOTIFY_CLIENT_ID=your_client_id
# SPOTIFY_CLIENT_SECRET=your_client_secret

# Authentication
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

# Search and get preview URLs
def get_spotify_songs(query, limit=50):
    results = sp.search(q=query, type='track', limit=limit)
    songs = []
    for track in results['tracks']['items']:
        songs.append({
            'title': track['name'],
            'artist': track['artists'][0]['name'],
            'preview_url': track['preview_url'],  # 30-second preview
            'image': track['album']['images'][0]['url']
        })
    return songs

# Batch download previews
songs = get_spotify_songs("upbeat tempo:120-140", limit=100)
for song in songs:
    if song['preview_url']:
        # Download and process
        pass
```

### Option C: User Uploads

```python
# Users can upload their own music
# Files stored in S3 or local storage
# Processing handled by feature_extraction.py
```

---

## Part 5: Docker Deployment

### Dockerfile (Backend)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "backend_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile (Frontend)

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

RUN npm install -g serve

COPY --from=builder /app/build ./build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: musicai_db
      POSTGRES_USER: musicai_user
      POSTGRES_PASSWORD: secure_password_change_me
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./schema.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U musicai_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://musicai_user:secure_password_change_me@db:5432/musicai_db
      REDIS_URL: redis://redis:6379
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn backend_api:app --host 0.0.0.0 --port 8000 --reload

  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend/src:/app/src

volumes:
  postgres_data:
```

### Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

---

## Part 6: AWS Deployment (Production)

### Architecture Overview

```
┌─────────────────┐
│  CloudFront CDN │ ← React frontend (static)
└────────┬────────┘
         │
    ┌────┴────┐
    │          │
┌───▼───┐  ┌──▼──────┐
│ ECS   │  │ Elastic │
│ Fargate   │ Load    │
│(API)  │  │ Balancer│
└───┬───┘  └─────────┘
    │
┌───┴───────────────────────────┐
│                               │
│  ┌──────────────┐             │
│  │ RDS Postgres │             │
│  └──────────────┘             │
│  ┌──────────────┐             │
│  │ElastiCache   │             │
│  │(Redis)       │             │
│  └──────────────┘             │
│  ┌──────────────┐             │
│  │ S3 Bucket    │             │
│  │(Audio files) │             │
│  └──────────────┘             │
│  ┌──────────────┐             │
│  │Pinecone      │             │
│  │(Vector DB)   │             │
│  └──────────────┘             │
└───────────────────────────────┘
```

### Terraform Configuration (Infrastructure as Code)

```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

# ECS Cluster
resource "aws_ecs_cluster" "musicai" {
  name = "musicai-cluster"
}

# RDS PostgreSQL
resource "aws_db_instance" "musicai" {
  identifier          = "musicai-db"
  engine             = "postgres"
  engine_version     = "15.2"
  instance_class     = "db.t3.micro"
  allocated_storage  = 20
  storage_encrypted  = true
  
  db_name  = "musicai_db"
  username = "admin"
  password = random_password.db_password.result
  
  publicly_accessible = false
  skip_final_snapshot = false
}

# S3 Bucket for audio files
resource "aws_s3_bucket" "audio_storage" {
  bucket = "musicai-audio-files"
}

resource "aws_s3_bucket_versioning" "audio_versioning" {
  bucket = aws_s3_bucket.audio_storage.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

### Deploy Frontend to CloudFront

```bash
# Build React app
npm run build

# Deploy to S3
aws s3 sync build/ s3://musicai-frontend/ --delete

# Create CloudFront distribution (point to S3)
# Set cache policy: 24 hours for index.html, 1 year for static assets

# Invalidate cache after deployment
aws cloudfront create-invalidation \
  --distribution-id E123456789ABC \
  --paths "/*"
```

---

## Part 7: Monitoring & Logging

### Install Monitoring Stack

```bash
# Prometheus for metrics
pip install prometheus-client

# Sentry for error tracking
pip install sentry-sdk

# ELK Stack for logging (optional)
docker-compose -f elk-compose.yml up -d
```

### Add to Backend

```python
# In backend_api.py
import sentry_sdk
from prometheus_client import Counter, Histogram

# Sentry
sentry_sdk.init(
    dsn="https://your-sentry-key@sentry.io/project-id",
    traces_sample_rate=0.1
)

# Prometheus metrics
recommendations_counter = Counter(
    'recommendations_generated_total',
    'Total recommendations generated'
)

recommendation_latency = Histogram(
    'recommendation_latency_seconds',
    'Time to generate recommendations'
)

@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    start_time = time.time()
    
    recs = generate_recommendations(user_id)
    
    duration = time.time() - start_time
    recommendation_latency.observe(duration)
    recommendations_counter.inc()
    
    return recs
```

### Health Monitoring Dashboard

Create alerts for:
- API response time > 500ms
- Error rate > 1%
- FAISS search latency > 100ms
- Database connection pool exhaustion
- Memory usage > 80%

---

## Part 8: Performance Optimization

### Backend Optimization

```python
# 1. Database Connection Pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)

# 2. Redis Caching
from functools import lru_cache
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    # Check cache first
    cached = cache.get(f"recommendations:{user_id}")
    if cached:
        return json.loads(cached)
    
    # Generate recommendations
    recs = generate_recommendations(user_id)
    
    # Cache for 5 minutes
    cache.setex(f"recommendations:{user_id}", 300, json.dumps(recs))
    
    return recs

# 3. FAISS GPU Acceleration
import faiss
if torch.cuda.is_available():
    index = faiss.index_cpu_to_gpu(
        faiss.StandardGpuResources(),
        0,  # GPU device ID
        cpu_index
    )
```

### Frontend Optimization

```javascript
// 1. Code Splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Upload = lazy(() => import('./pages/Upload'));

// 2. Image Optimization
<img 
  src={imageSrc} 
  loading="lazy"
  decoding="async"
/>

// 3. Virtual Scrolling for large lists
import { FixedSizeList } from 'react-window';

// 4. Memoization
const SongCard = memo(({ song }) => ...);
```

---

## Part 9: Security Checklist

- [ ] Use HTTPS/TLS for all connections
- [ ] Implement CORS properly (not `*`)
- [ ] Hash passwords with bcrypt
- [ ] Use JWT with short expiration
- [ ] Implement rate limiting
- [ ] Validate file uploads (size, type)
- [ ] Sanitize user inputs
- [ ] Use environment variables for secrets
- [ ] Enable database encryption
- [ ] Implement audit logging
- [ ] Regular dependency updates
- [ ] OWASP Top 10 compliance check

---

## Part 10: Testing

### Backend Unit Tests

```bash
pip install pytest pytest-asyncio pytest-cov
```

```python
# test_recommendations.py
import pytest
from backend_api import app, get_recommendations

@pytest.mark.asyncio
async def test_recommendations_basic():
    """Test recommendation endpoint returns recommendations"""
    response = await app.test_client().get("/recommendations/user_123?num=10")
    assert response.status_code == 200
    assert len(response.json()["recommendations"]) <= 10

@pytest.mark.asyncio
async def test_recommendations_diversity():
    """Test MMR produces diverse recommendations"""
    recs = await get_recommendations("user_123", diversity=0.8)
    # Calculate diversity metric
    similarities = [cosine_sim(recs[i], recs[j]) for i in range(len(recs)) for j in range(i+1, len(recs))]
    assert np.mean(similarities) < 0.7  # Should not be too similar
```

Run tests: `pytest test_recommendations.py -v --cov=backend_api`

---

## Summary

This setup provides:
✅ Local development environment
✅ Production-grade database
✅ Fast vector search (FAISS)
✅ Docker containerization
✅ AWS cloud deployment
✅ Monitoring and logging
✅ Performance optimization
✅ Security best practices
✅ Comprehensive testing

**Next steps**: Configure your specific AWS credentials, database passwords, and API keys, then deploy!
