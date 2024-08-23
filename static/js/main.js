console.log("main.js is loading...");

// Constants
const WELCOME_MESSAGE_KEY = 'welcomeMessage';
const WELCOME_MESSAGE_EXPIRY_KEY = 'welcomeMessageExpiry';

// Helper functions
async function fetchWelcomeMessage() {
    const cachedMessage = localStorage.getItem('welcomeMessage');
    const cacheExpiry = localStorage.getItem('welcomeMessageExpiry');

    if (cachedMessage && Date.now() < Number(cacheExpiry)) {
        return cachedMessage;
    }

    try {
        const response = await fetch('/api/welcome-message');
        const data = await response.json();
        const message = data.response || 'Welcome to Spotify2Apple!';

        const expiry = Date.now() + 24 * 60 * 60 * 1000; // 24 hours from now
        localStorage.setItem('welcomeMessage', message);
        console.log("New welcome message fetched and cached:", message);
        localStorage.setItem('welcomeMessageExpiry', expiry.toString());

        return message;
    } catch (error) {
        console.error('Failed to fetch welcome message:', error);
        return 'Welcome to Spotify2Apple!';
    }
}

async function authorizeUser(service) {
    console.log(`Attempting to authorize user for ${service}...`);
    let userToken = localStorage.getItem(`${service}UserToken`);
    if (!userToken) {
        console.log(`No cached token found for ${service}, proceeding with authorization...`);
        if (service === "Spotify") {
            // TODO: Implement Spotify authorization flow
            console.log("Spotify authorization not yet implemented");
            // For now, let's simulate a successful auth
            userToken = "dummy_spotify_token";
            localStorage.setItem('SpotifyUserToken', userToken);
        } else if (service === "AppleMusic") {
            try {
                const music = MusicKit.getInstance();
                userToken = await music.authorize();
                localStorage.setItem('AppleMusicUserToken', userToken);
                console.log(`AppleMusic user authorized successfully. Token: ${userToken.substring(0, 10)}...`);
            } catch (error) {
                console.error("Error during Apple Music authorization:", error);
                return null;
            }
        }
    } else {
        console.log(`${service} user token found in cache.`);
    }

    updateButtonState(`${service.toLowerCase()}-login`, true);
    return userToken;
}

function updateButtonState(buttonId, isAuthorized) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = isAuthorized;
        button.textContent = isAuthorized ? `Logged in to ${buttonId.split('-')[0].charAt(0).toUpperCase() + buttonId.split('-')[0].slice(1)}` : button.textContent;
    }
}

function showError(message) {
    console.error("Error:", message);
    const errorMessage = document.getElementById('error-message');
    if (errorMessage) {
        errorMessage.textContent = message;
    }
}

async function loadPlaylists(service) {
    console.log(`Loading playlists for ${service}...`);
    try {
        const response = await fetch(`/api/${service.toLowerCase()}-playlists`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const playlists = await response.json();
        console.log(`${service} playlists loaded:`, playlists);
        return playlists;
    } catch (error) {
        showError(`An error occurred while loading ${service} playlists.`);
        console.error(`Failed to load ${service} playlists:`, error);
        return [];
    }
}

function displayPlaylists(playlists, containerId) {
    console.log(`Displaying playlists in ${containerId}:`, playlists);
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container ${containerId} not found`);
        return;
    }
    container.innerHTML = '';

    if (playlists.length === 0) {
        container.textContent = 'No playlists found.';
        return;
    }

    playlists.forEach(playlist => {
        const div = document.createElement('div');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = playlist.id;
        checkbox.id = `playlist-${playlist.id}`;

        const label = document.createElement('label');
        label.htmlFor = checkbox.id;
        label.textContent = playlist.name;

        div.appendChild(checkbox);
        div.appendChild(label);
        container.appendChild(div);
    });
}

// Main function
async function initializeApp() {
    console.log("Initializing app...");

    try {
        const welcomeMessage = await fetchWelcomeMessage();
        const welcomeElement = document.getElementById('welcome-message');
        if (welcomeElement) {
            welcomeElement.textContent = welcomeMessage;
        }

        const response = await fetch('/api/developer-token');
        const data = await response.json();
        const developerToken = data.token;
        console.log("Developer token fetched successfully");

        MusicKit.configure({
            developerToken: developerToken,
            app: {
                name: 'Spotify2Apple',
                build: '1.0.0'
            }
        });
        console.log("MusicKit configured successfully");

        // Set up event listeners
        setupEventListeners();

        // Check for existing tokens and update button states
        const spotifyToken = localStorage.getItem('SpotifyUserToken');
        const appleMusicToken = localStorage.getItem('AppleMusicUserToken');

        updateButtonState('spotify-login', !!spotifyToken);
        updateButtonState('apple-login', !!appleMusicToken);

        if (spotifyToken) {
            const spotifyPlaylists = await loadPlaylists('Spotify');
            displayPlaylists(spotifyPlaylists, 'spotify-playlists');
        }

        if (appleMusicToken) {
            const appleMusicPlaylists = await loadPlaylists('AppleMusic');
            displayPlaylists(appleMusicPlaylists, 'apple-playlists');
        }

        // Show migrate button if both services are authorized
        if (spotifyToken && appleMusicToken) {
            const migrateButton = document.getElementById('migrate-button');
            if (migrateButton) {
                migrateButton.style.display = 'block';
            }
        }

    } catch (error) {
        showError('Failed to initialize the app. Please try again later.');
        console.error('App initialization failed:', error);
    }
}

function setupEventListeners() {
    console.log("Setting up event listeners...");
    const spotifyLoginButton = document.getElementById('spotify-login');
    const appleLoginButton = document.getElementById('apple-login');
    const migrateButton = document.getElementById('migrate-button');

    if (spotifyLoginButton) {
        spotifyLoginButton.addEventListener('click', handleSpotifyLogin);
        console.log("Spotify login button listener added");
    } else {
        console.error("Spotify login button not found");
    }

    if (appleLoginButton) {
        appleLoginButton.addEventListener('click', handleAppleLogin);
        console.log("Apple login button listener added");
    } else {
        console.error("Apple login button not found");
    }

    if (migrateButton) {
        migrateButton.addEventListener('click', handleMigration);
        console.log("Migrate button listener added");
    } else {
        console.error("Migrate button not found");
    }
}

// Event handlers
async function handleSpotifyLogin() {
    console.log("Spotify login button clicked");
    try {
        const token = await authorizeUser('Spotify');
        if (token) {
            const spotifyPlaylists = await loadPlaylists('Spotify');
            displayPlaylists(spotifyPlaylists, 'spotify-playlists');
            updateButtonState('spotify-login', true);
            checkMigrateButtonVisibility();
        }
    } catch (error) {
        showError('Spotify authorization failed. Please try again.');
        console.error('Spotify authorization failed:', error);
    }
}

async function handleAppleLogin() {
    console.log("Apple Music login button clicked");
    try {
        const token = await authorizeUser('AppleMusic');
        if (token) {
            const appleMusicPlaylists = await loadPlaylists('AppleMusic');
            displayPlaylists(appleMusicPlaylists, 'apple-playlists');
            updateButtonState('apple-login', true);
            checkMigrateButtonVisibility();
        }
    } catch (error) {
        showError('Apple Music authorization failed. Please try again.');
        console.error('Apple Music authorization failed:', error);
    }
}

function checkMigrateButtonVisibility() {
    const spotifyToken = localStorage.getItem('SpotifyUserToken');
    const appleMusicToken = localStorage.getItem('AppleMusicUserToken');
    const migrateButton = document.getElementById('migrate-button');
    if (migrateButton) {
        migrateButton.style.display = (spotifyToken && appleMusicToken) ? 'block' : 'none';
    }
}

async function handleMigration() {
    console.log("Migrate button clicked");
    try {
        const selectedPlaylists = Array.from(document.querySelectorAll('#spotify-playlists input:checked'))
            .map(checkbox => checkbox.value);

        if (selectedPlaylists.length === 0) {
            showError('Please select at least one playlist to migrate.');
            return;
        }

        const musicUserToken = localStorage.getItem('AppleMusicUserToken');
        const response = await fetch('/api/migrate-playlists', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_token: musicUserToken,
                playlists: selectedPlaylists
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('Playlists migrated successfully:', result);

        // Refresh Apple Music playlists after migration
        const appleMusicPlaylists = await loadPlaylists('AppleMusic');
        displayPlaylists(appleMusicPlaylists, 'apple-playlists');
    } catch (error) {
        showError('An error occurred during playlist migration. Please try again.');
        console.error('Playlist migration failed:', error);
    }
}

// Initialize the app when MusicKit is loaded
document.addEventListener('musickitloaded', () => {
    console.log("MusicKit loaded event fired");
    initializeApp();
});

// Fallback initialization if MusicKit doesn't load
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log("Document already loaded, initializing app");
    initializeApp();
}

console.log("main.js finished loading");