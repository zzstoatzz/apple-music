console.log("Script loaded and musickit.js should be ready.");

async function authorizeUser(service) {
    let userToken = localStorage.getItem(`${service}UserToken`);
    if (!userToken) {
        console.log(`Authorizing user for ${service}...`);
        if (service === "Spotify") {
            // TODO: Implement Spotify authorization flow
        } else if (service === "AppleMusic") {
            const music = MusicKit.getInstance();
            userToken = await music.authorize();
            localStorage.setItem('AppleMusicUserToken', userToken);
        }
        console.log(`${service} user authorized successfully.`);
    } else {
        console.log(`${service} user token found in cache.`);
        if (service === "AppleMusic") {
            document.getElementById('apple-login').style.display = 'none';
        } else if (service === "Spotify") {
            document.getElementById('spotify-login').style.display = 'none';
        }
    }
    return userToken;
}

function showError(message) {
    const errorMessage = document.getElementById('error-message');
    errorMessage.textContent = message;
}

async function loadSpotifyPlaylists() {
    try {
        const response = await fetch('/api/spotify-playlists'); // TODO: Implement this endpoint
        if (response.status === 404) {
            showError('Failed to load Spotify playlists.');
            return;
        }
        const playlists = await response.json();
        const playlistContainer = document.getElementById('playlists');
        playlistContainer.innerHTML = '';

        playlists.forEach(playlist => {
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = playlist.id;
            checkbox.id = `playlist-${playlist.id}`;

            const label = document.createElement('label');
            label.htmlFor = checkbox.id;
            label.textContent = playlist.name;

            playlistContainer.appendChild(checkbox);
            playlistContainer.appendChild(label);
            playlistContainer.appendChild(document.createElement('br'));
        });

        document.getElementById('playlist-selection').style.display = 'block';
    } catch (error) {
        showError('An error occurred while loading Spotify playlists.');
        console.error('Failed to load Spotify playlists:', error);
    }
}

document.addEventListener('musickitloaded', async function () {
    console.log("MusicKit loaded successfully.");

    try {
        // Fetch the developer token from the backend
        const response = await fetch('/api/developer-token');
        console.log("Fetching developer token...");

        const data = await response.json();
        const developerToken = data.token;

        // Configure MusicKit with the fetched developer token
        MusicKit.configure({
            developerToken: developerToken,
            app: {
                name: 'Spotify2Apple',
                build: '1.0.0'
            }
        });

        // Hide Apple Music login button if already authorized
        await authorizeUser('AppleMusic');

        // Handle Spotify login and playlist loading
        document.getElementById('spotify-login').addEventListener('click', async function () {
            try {
                await authorizeUser('Spotify');
                await loadSpotifyPlaylists();
            } catch (error) {
                showError('Spotify authorization failed. Please try again.');
                console.error('Spotify authorization failed:', error);
            }
        });

        // Handle the migration button click
        document.getElementById('migrate-button').addEventListener('click', async function () {
            console.log("Migrate button clicked.");

            try {
                const selectedPlaylists = Array.from(document.querySelectorAll('#playlists input:checked'))
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

                if (response.status === 422) {
                    showError('Failed to migrate the playlists. Please try again.');
                    return;
                }

                const result = await response.json();
                console.log('Playlists migrated successfully:', result);
            } catch (error) {
                showError('An error occurred during playlist migration. Please try again.');
                console.error('Playlist migration failed:', error);
            }
        });

    } catch (error) {
        showError('Failed to fetch developer token. Please try again later.');
        console.error('Failed to fetch developer token:', error);
    }
});
