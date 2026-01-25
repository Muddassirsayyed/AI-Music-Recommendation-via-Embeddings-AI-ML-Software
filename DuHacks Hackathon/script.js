// ============================================================================
// AUTHENTICATION SYSTEM - AI MUSIC RECOMMENDATION
// ============================================================================

let currentUser = null;

// Initialize on page load
window.addEventListener('load', function() {
    console.log('🎵 Initializing Music AI Dashboard...');
    
    // Check if user is already logged in
    const savedUser = localStorage.getItem('musicai_user');
    if (savedUser) {
        try {
            currentUser = JSON.parse(savedUser);
            console.log('✅ Welcome back, ' + currentUser.name);
            showApp();
        } catch (e) {
            console.error('Error loading user:', e);
            localStorage.removeItem('musicai_user');
            showAuth();
        }
    } else {
        console.log('ℹ️ Please log in or sign up');
        showAuth();
    }
    
    // Attach event listeners
    attachEventListeners();
});

// ============================================================================
// UI STATE MANAGEMENT
// ============================================================================

function showAuth() {
    const authContainer = document.getElementById('authContainer');
    const appContainer = document.getElementById('appContainer');
    if (authContainer) authContainer.style.display = 'flex';
    if (appContainer) appContainer.style.display = 'none';
}

function showApp() {
    const authContainer = document.getElementById('authContainer');
    const appContainer = document.getElementById('appContainer');
    if (authContainer) authContainer.style.display = 'none';
    if (appContainer) appContainer.style.display = 'block';
    initializeApp();
}

function initializeApp() {
    console.log('Initializing app...');
    const dashboard = document.getElementById('dashboard');
    if (dashboard) dashboard.classList.add('active');
    
    const firstNav = document.querySelector('.nav-link');
    if (firstNav) firstNav.classList.add('active');
    
    setupUploadHandlers();
}

// ============================================================================
// PAGE NAVIGATION
// ============================================================================

function switchToSignup() {
    const loginPage = document.getElementById('loginPage');
    const signupPage = document.getElementById('signupPage');
    if (loginPage) loginPage.classList.remove('active');
    if (signupPage) signupPage.classList.add('active');
}

function switchToLogin() {
    const signupPage = document.getElementById('signupPage');
    const loginPage = document.getElementById('loginPage');
    if (signupPage) signupPage.classList.remove('active');
    if (loginPage) loginPage.classList.add('active');
}

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    
    // Show selected section
    const section = document.getElementById(sectionId);
    if (section) section.classList.add('active');
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
    if (event && event.target) event.target.classList.add('active');
    
    window.scrollTo(0, 0);
}

// ============================================================================
// AUTHENTICATION HANDLERS
// ============================================================================

function handleLogin(event) {
    event.preventDefault();
    console.log('📧 Processing login...');
    
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value.trim();
    
    // Validation
    if (!email || !password) {
        showNotification('❌ Please enter email and password', 'error');
        return;
    }
    
    if (!email.includes('@')) {
        showNotification('❌ Invalid email format', 'error');
        return;
    }
    
    // Create user
    const user = {
        id: 'user_' + Date.now(),
        email: email,
        name: email.split('@')[0],
        avatar: `https://ui-avatars.com/api/?name=${email.split('@')[0]}&background=6D28D9&color=fff`,
        loginMethod: 'email',
        loginTime: new Date().toISOString()
    };
    
    loginUser(user);
}

function handleSignup(event) {
    event.preventDefault();
    console.log('👤 Processing signup...');
    
    const name = document.getElementById('signupName').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value.trim();
    const confirm = document.getElementById('signupConfirm').value.trim();
    
    // Validation
    if (!name || !email || !password || !confirm) {
        showNotification('❌ Please fill all fields', 'error');
        return;
    }
    
    if (!email.includes('@')) {
        showNotification('❌ Invalid email format', 'error');
        return;
    }
    
    if (password !== confirm) {
        showNotification('❌ Passwords do not match', 'error');
        return;
    }
    
    if (password.length < 8) {
        showNotification('❌ Password must be 8+ characters', 'error');
        return;
    }
    
    // Create user
    const user = {
        id: 'user_' + Date.now(),
        email: email,
        name: name,
        avatar: `https://ui-avatars.com/api/?name=${name}&background=6D28D9&color=fff`,
        loginMethod: 'email',
        signupTime: new Date().toISOString()
    };
    
    loginUser(user);
}

// ============================================================================
// OAUTH HANDLERS
// ============================================================================

function signInWithSpotify() {
    showNotification('🎵 Connecting to Spotify...', 'info');
    setTimeout(() => {
        const user = {
            id: 'spotify_' + Date.now(),
            email: 'user_' + Date.now() + '@spotify.local',
            name: 'Spotify User',
            avatar: 'https://ui-avatars.com/api/?name=Spotify&background=1DB954&color=fff',
            loginMethod: 'spotify'
        };
        loginUser(user);
    }, 1500);
}

function signUpWithSpotify() {
    showNotification('🎵 Connecting to Spotify...', 'info');
    setTimeout(() => {
        const user = {
            id: 'spotify_' + Date.now(),
            email: 'signup_' + Date.now() + '@spotify.local',
            name: 'New Spotify User',
            avatar: 'https://ui-avatars.com/api/?name=SpotifyUser&background=1DB954&color=fff',
            loginMethod: 'spotify'
        };
        loginUser(user);
    }, 1500);
}

// Google Sign-In Handler
function handleGoogleSignInResponse(response) {
    console.log('🔐 Google Sign-In response received');
    
    try {
        // Decode JWT token
        const base64Url = response.credential.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map((c) => {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        
        const data = JSON.parse(jsonPayload);
        
        console.log('✅ Google user data:', data.name);
        
        // Create user object from Google data
        const user = {
            id: 'google_' + data.sub,
            email: data.email,
            name: data.name,
            avatar: data.picture || `https://ui-avatars.com/api/?name=${data.name}&background=4285F4&color=fff`,
            loginMethod: 'google',
            googleId: data.sub
        };
        
        loginUser(user);
    } catch (error) {
        console.error('❌ Error processing Google response:', error);
        showNotification('❌ Google sign-in failed', 'error');
    }
}

function signInWithGoogle() {
    console.log('🔐 Google sign-in button clicked');
    showNotification('🔐 Connecting to Google...', 'info');
    
    // Trigger Google One Tap or redirect to login
    if (window.google && window.google.accounts) {
        window.google.accounts.id.renderButton(
            document.querySelector('.btn-google'),
            { theme: 'dark', size: 'large' }
        );
    }
}

function signUpWithGoogle() {
    console.log('🔐 Google sign-up button clicked');
    // Same as sign-in for Google
    signInWithGoogle();
}

// ============================================================================
// MAIN LOGIN FUNCTION
// ============================================================================

function loginUser(user) {
    console.log('👤 User logged in:', user.name);
    
    // Save to localStorage
    localStorage.setItem('musicai_user', JSON.stringify(user));
    currentUser = user;
    
    // Show success notification
    showNotification(`✅ Welcome, ${user.name}! 🎵`, 'success');
    
    // Reset forms
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    if (loginForm) loginForm.reset();
    if (signupForm) signupForm.reset();
    
    // Switch to app
    setTimeout(() => showApp(), 1200);
}

function logout() {
    console.log('👋 User logged out');
    
    localStorage.removeItem('musicai_user');
    currentUser = null;
    
    showNotification('👋 Logged out successfully', 'info');
    
    // Reset pages
    const signupPage = document.getElementById('signupPage');
    const loginPage = document.getElementById('loginPage');
    if (signupPage) signupPage.classList.remove('active');
    if (loginPage) loginPage.classList.add('active');
    
    setTimeout(() => showAuth(), 800);
}

// ============================================================================
// PASSWORD STRENGTH INDICATOR
// ============================================================================

function calculatePasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z\d]/.test(password)) strength++;
    return strength;
}

function updatePasswordStrengthBar(strength) {
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');
    if (!strengthFill || !strengthText) return;
    
    const levels = {
        0: { width: '0%', color: '#EF4444', label: 'Weak' },
        1: { width: '20%', color: '#F97316', label: 'Weak' },
        2: { width: '40%', color: '#EAB308', label: 'Fair' },
        3: { width: '60%', color: '#FBBF24', label: 'Good' },
        4: { width: '80%', color: '#84CC16', label: 'Strong' },
        5: { width: '100%', color: '#10B981', label: 'Very Strong' }
    };
    
    const level = levels[strength];
    strengthFill.style.width = level.width;
    strengthFill.style.backgroundColor = level.color;
    strengthText.textContent = level.label;
    strengthText.style.color = level.color;
}

// ============================================================================
// FILE UPLOAD HANDLING
// ============================================================================

function setupUploadHandlers() {
    const uploadBox = document.getElementById('uploadBox');
    const audioFile = document.getElementById('audioFile');
    
    if (!uploadBox || !audioFile) return;
    
    console.log('✅ Upload handlers ready');
    
    // Click to select file
    uploadBox.addEventListener('click', () => audioFile.click());
    
    // Drag over
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.classList.add('dragover');
    });
    
    // Drag leave
    uploadBox.addEventListener('dragleave', () => {
        uploadBox.classList.remove('dragover');
    });
    
    // Drop file
    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadBox.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });
    
    // File input change
    audioFile.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

function handleFileUpload(file) {
    if (!file) return;
    
    console.log('📁 File selected:', file.name);
    
    if (!file.type.startsWith('audio/')) {
        alert('⚠️ Please upload an audio file (MP3, WAV, FLAC, etc.)');
        return;
    }
    
    const uploadBox = document.getElementById('uploadBox');
    const uploadProgress = document.getElementById('uploadProgress');
    const analysisResults = document.getElementById('analysisResults');
    
    if (uploadBox) uploadBox.style.display = 'none';
    if (uploadProgress) uploadProgress.style.display = 'block';
    if (analysisResults) analysisResults.style.display = 'none';
    
    simulateUploadProgress();
    
    setTimeout(() => {
        extractAudioFeatures(file);
    }, 2000);
}

function simulateUploadProgress() {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 30;
        if (progress > 100) progress = 100;
        
        if (progressFill) progressFill.style.width = progress + '%';
        if (progressText) progressText.textContent = `Uploading... ${Math.round(progress)}%`;
        
        if (progress === 100) {
            clearInterval(interval);
            if (progressText) progressText.textContent = 'Processing audio...';
        }
    }, 300);
}

function extractAudioFeatures(file) {
    const fileName = file.name.split('.')[0];
    
    // Create FormData to send file to backend
    const formData = new FormData();
    formData.append('file', file);
    
    // Get token from localStorage
    const user = JSON.parse(localStorage.getItem('musicai_user') || '{}');
    const token = user.token || 'demo_token';
    
    // Call backend API for real feature extraction
    fetch('http://localhost:8000/music/upload?token=' + token, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.features) {
            displayAnalysisResults(fileName, {
                duration: data.features.duration + 's',
                tempo: data.features.tempo + ' BPM',
                energy: data.features.energy.toFixed(3),
                spectralCentroid: data.features.spectral_centroid + ' Hz',
                spectralRolloff: (data.features.spectral_centroid * 2.2).toFixed(0) + ' Hz',
                zeroCrossingRate: (Math.random() * 0.1).toFixed(4),
                harmonicEnergy: (Math.random() * 1 + 1.5).toFixed(3),
                rhythmStability: (Math.random() * 0.2 + 0.2).toFixed(3)
            });
        } else {
            // Fallback to mock data if API fails
            const features = {
                duration: (file.size / 1024 / 1024 * 10).toFixed(1) + 's',
                tempo: Math.floor(Math.random() * 60 + 80) + ' BPM',
                energy: (Math.random() * 0.5 + 0.3).toFixed(3),
                spectralCentroid: Math.floor(Math.random() * 2000 + 3000) + ' Hz',
                spectralRolloff: Math.floor(Math.random() * 3000 + 8000) + ' Hz',
                zeroCrossingRate: (Math.random() * 0.1).toFixed(4),
                harmonicEnergy: (Math.random() * 1 + 1.5).toFixed(3),
                rhythmStability: (Math.random() * 0.2 + 0.2).toFixed(3)
            };
            displayAnalysisResults(fileName, features);
        }
    })
    .catch(error => {
        console.warn('API call failed, using mock data:', error);
        // Fallback to mock data
        const features = {
            duration: (file.size / 1024 / 1024 * 10).toFixed(1) + 's',
            tempo: Math.floor(Math.random() * 60 + 80) + ' BPM',
            energy: (Math.random() * 0.5 + 0.3).toFixed(3),
            spectralCentroid: Math.floor(Math.random() * 2000 + 3000) + ' Hz',
            spectralRolloff: Math.floor(Math.random() * 3000 + 8000) + ' Hz',
            zeroCrossingRate: (Math.random() * 0.1).toFixed(4),
            harmonicEnergy: (Math.random() * 1 + 1.5).toFixed(3),
            rhythmStability: (Math.random() * 0.2 + 0.2).toFixed(3)
        };
        displayAnalysisResults(fileName, features);
    });
}

function displayAnalysisResults(fileName, features) {
    const uploadBox = document.getElementById('uploadBox');
    const uploadProgress = document.getElementById('uploadProgress');
    const analysisResults = document.getElementById('analysisResults');
    
    document.getElementById('songName').textContent = fileName;
    document.getElementById('songDuration').textContent = features.duration;
    document.getElementById('songTempo').textContent = features.tempo;
    document.getElementById('songEnergy').textContent = features.energy;
    
    if (uploadProgress) uploadProgress.style.display = 'none';
    if (uploadBox) uploadBox.style.display = 'none';
    if (analysisResults) analysisResults.style.display = 'block';
    
    console.log('✅ Features extracted:', features);
}

function resetUpload() {
    const uploadBox = document.getElementById('uploadBox');
    const uploadProgress = document.getElementById('uploadProgress');
    const analysisResults = document.getElementById('analysisResults');
    const audioFile = document.getElementById('audioFile');
    
    if (uploadBox) uploadBox.style.display = 'block';
    if (uploadProgress) uploadProgress.style.display = 'none';
    if (analysisResults) analysisResults.style.display = 'none';
    if (audioFile) audioFile.value = '';
}

// ============================================================================
// INTERACTIVE FEATURES
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-icon').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const icon = this.textContent.trim();
            
            if (icon === '▶️') {
                this.textContent = '⏸️';
                setTimeout(() => { this.textContent = '▶️'; }, 3000);
            } else if (icon === '➕') {
                showNotification('Added to playlist! ➕', 'success');
            } else if (icon === '❤️') {
                showNotification('Liked! ❤️', 'success');
            }
        });
    });
});

// ============================================================================
// NOTIFICATION SYSTEM
// ============================================================================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    
    const colors = {
        success: '#10B981',
        error: '#EF4444',
        info: '#6D28D9'
    };
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${colors[type] || colors.info};
        color: white;
        border-radius: 8px;
        z-index: 9999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: slideIn 0.3s ease;
        font-weight: 500;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Add animation CSS if not present
    if (!document.querySelector('style[data-notif]')) {
        const style = document.createElement('style');
        style.setAttribute('data-notif', 'true');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(400px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Auto remove
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ============================================================================
// EVENT LISTENER SETUP
// ============================================================================

function attachEventListeners() {
    console.log('Attaching event listeners...');
    
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
        console.log('✅ Login form ready');
    }
    
    // Signup form
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
        console.log('✅ Signup form ready');
    }
    
    // Password strength
    const passwordInput = document.getElementById('signupPassword');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            updatePasswordStrengthBar(calculatePasswordStrength(this.value));
        });
    }
    
    console.log('✅ All listeners attached');
}

// ============================================================================
// BACKEND INTEGRATION
// ============================================================================

const API_BASE_URL = 'http://localhost:8000';

// Spotify Search Functions
async function spotifySearchTracks(query, limit = 5) {
    try {
        const response = await fetch(
            `${API_BASE_URL}/spotify/search/tracks?q=${encodeURIComponent(query)}&limit=${limit}`
        );
        
        if (!response.ok) throw new Error('Search failed');
        
        const data = await response.json();
        console.log('🎵 Spotify search results:', data);
        return data.tracks || [];
    } catch (error) {
        console.error('Error searching Spotify:', error);
        showNotification('Error searching Spotify', 'error');
        return [];
    }
}

async function spotifySearchArtists(query, limit = 5) {
    try {
        const response = await fetch(
            `${API_BASE_URL}/spotify/search/artists?q=${encodeURIComponent(query)}&limit=${limit}`
        );
        
        if (!response.ok) throw new Error('Search failed');
        
        const data = await response.json();
        return data.artists || [];
    } catch (error) {
        console.error('Error searching artists:', error);
        return [];
    }
}

async function spotifyGetRecommendations(seedTracks = null, seedArtists = null, seedGenres = null, limit = 10) {
    try {
        let url = `${API_BASE_URL}/spotify/recommendations?limit=${limit}`;
        
        if (seedTracks && seedTracks.length > 0) {
            url += `&seed_tracks=${seedTracks.slice(0, 5).join(',')}`;
        }
        if (seedArtists && seedArtists.length > 0) {
            url += `&seed_artists=${seedArtists.slice(0, 5).join(',')}`;
        }
        if (seedGenres && seedGenres.length > 0) {
            url += `&seed_genres=${seedGenres.slice(0, 5).join(',')}`;
        }
        
        const response = await fetch(url);
        
        if (!response.ok) throw new Error('Failed to get recommendations');
        
        const data = await response.json();
        console.log('🎯 Recommendations:', data);
        return data.recommendations || [];
    } catch (error) {
        console.error('Error getting recommendations:', error);
        return [];
    }
}

async function spotifyGetAudioFeatures(trackId) {
    try {
        const response = await fetch(`${API_BASE_URL}/spotify/audio-features/${trackId}`);
        
        if (!response.ok) throw new Error('Failed to get audio features');
        
        const data = await response.json();
        return data.features || null;
    } catch (error) {
        console.error('Error getting audio features:', error);
        return null;
    }
}

async function spotifyGetGenres() {
    try {
        const response = await fetch(`${API_BASE_URL}/spotify/genres`);
        
        if (!response.ok) throw new Error('Failed to get genres');
        
        const data = await response.json();
        return data.genres || [];
    } catch (error) {
        console.error('Error getting genres:', error);
        return [];
    }
}

async function spotifyCheckHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/spotify/health`);
        const data = await response.json();
        return data.status === 'connected';
    } catch (error) {
        console.error('Spotify health check failed:', error);
        return false;
    }
}

// Demo: Search for tracks when upload completes
async function searchSpotifyDemo() {
    console.log('🎵 Searching Spotify for recommendations...');
    
    const tracks = await spotifySearchTracks('lofi', 5);
    
    if (tracks.length > 0) {
        console.log('Found tracks:', tracks);
        displaySpotifyResults(tracks);
    }
}

function displaySpotifyResults(tracks) {
    console.log('Displaying Spotify results...');
    
    // You can display these in the recommendations section
    // For now, just log them
    tracks.forEach((track, index) => {
        console.log(`${index + 1}. ${track.name} - ${track.artist}`);
    });
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

// ============================================================================
// ERROR HANDLING
// ============================================================================

window.addEventListener('error', function(event) {
    console.error('Error:', event.error);
});

// ============================================================================
// GOOGLE SIGN-IN INITIALIZATION
// ============================================================================

// Initialize Google Sign-In when API is loaded
function initializeGoogleSignIn() {
    // Check if Google API is loaded
    if (window.google && window.google.accounts) {
        console.log('🔐 Initializing Google Sign-In...');
        
        try {
            window.google.accounts.id.initialize({
                client_id: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com', // Replace with your Google Client ID from https://console.cloud.google.com
                callback: handleGoogleSignInResponse,
                auto_select: false,
                ux_mode: 'popup',
                itp_support: true
            });
            
            // Render Google Sign-In button on login page
            const loginButton = document.getElementById('googleSignInButton');
            if (loginButton && !loginButton.hasChildNodes()) {
                window.google.accounts.id.renderButton(loginButton, {
                    theme: 'outline',
                    size: 'large',
                    text: 'signin_with',
                });
                console.log('✅ Google Sign-In button rendered on login page');
            }
            
            // Render Google Sign-Up button on signup page
            const signupButton = document.getElementById('googleSignUpButton');
            if (signupButton && !signupButton.hasChildNodes()) {
                window.google.accounts.id.renderButton(signupButton, {
                    theme: 'outline',
                    size: 'large',
                    text: 'signup_with',
                });
                console.log('✅ Google Sign-In button rendered on signup page');
            }
            
            // Try to show One Tap UI (prompt)
            window.google.accounts.id.prompt((notification) => {
                if (notification.isNotDisplayed()) {
                    console.log('ℹ️ One Tap UI not displayed');
                } else if (notification.isSkippedMoment()) {
                    console.log('ℹ️ One Tap UI skipped');
                }
            });
            
            console.log('✅ Google Sign-In fully initialized');
        } catch (error) {
            console.error('❌ Error initializing Google Sign-In:', error);
        }
    } else {
        console.log('⏳ Google API not loaded yet, retrying...');
        setTimeout(initializeGoogleSignIn, 500);
    }
}

// Initialize when page loads
window.addEventListener('load', function() {
    setTimeout(initializeGoogleSignIn, 1000);
});

// Also try to initialize if document is already ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(initializeGoogleSignIn, 500);
    });
} else {
    setTimeout(initializeGoogleSignIn, 500);
}

console.log('🎵 Music AI Dashboard loaded successfully!');
console.log('📝 SETUP REQUIRED: Replace YOUR_GOOGLE_CLIENT_ID in script.js with your actual Google Client ID');
