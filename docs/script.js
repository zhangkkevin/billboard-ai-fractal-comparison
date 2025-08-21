// Song data from the analysis results
const songData = {
    // DFA Analysis Results
    dfa: {
        closest: [
            { model: "billboard", title: "Bad Day", artist: "Daniel Powter", year: 2006, rank: 1, value: "α = 1.0" },
            { model: "suno_v4_5", title: "Anti-Hero", artist: "Taylor Swift", year: 2023, rank: 4, value: "α = 1.0" },
            { model: "diffrhythm", title: "Claudette", artist: "The Everly Brothers", year: 1958, rank: "2b", value: "α = 1.0" },
            { model: "YuE", title: "All Shook Up", artist: "Elvis Presley", year: 1957, rank: 1, value: "α = 1.0" }
        ],
        min: [
            { model: "billboard", title: "Let Me Love You", artist: "Mario", year: 2005, rank: 3, value: "α = 0.767" },
            { model: "suno_v4_5", title: "Love's Theme", artist: "Love Unlimited Orchestra", year: 1974, rank: 3, value: "α = 0.679" },
            { model: "diffrhythm", title: "Hanging By A Moment", artist: "Lifehouse", year: 2001, rank: 1, value: "α = 0.702" },
            { model: "YuE", title: "Harlem Shake", artist: "Baauer", year: 2013, rank: 4, value: "α = 0.721" }
        ],
        max: [
            { model: "billboard", title: "Rockstar", artist: "DaBaby feat. Roddy Ricch", year: 2020, rank: 5, value: "α = 1.267" },
            { model: "suno_v4_5", title: "You're Beautiful", artist: "James Blunt", year: 2006, rank: 4, value: "α = 1.25" },
            { model: "diffrhythm", title: "Mona Lisa", artist: "Nat King Cole", year: 1950, rank: 2, value: "α = 1.257" },
            { model: "YuE", title: "Blue Tango", artist: "Leroy Anderson", year: 1952, rank: 1, value: "α = 1.413" }
        ]
    },
    
    // MFDFA Analysis Results
    mfdfa: {
        maxWidth: [
            { model: "billboard", title: "Sugar", artist: "Maroon 5", year: 2015, rank: 5, value: "α width = 4.874" },
            { model: "suno_v4_5", title: "The Yellow Rose of Texas", artist: "Mitch Miller", year: 1955, rank: 3, value: "α width = 4.716" },
            { model: "diffrhythm", title: "When I'm Gone", artist: "3 Doors Down", year: 2003, rank: 5, value: "α width = 3.399" },
            { model: "YuE", title: "The Sweet Escape", artist: "Gwen Stefani feat. Akon", year: 2007, rank: 3, value: "α width = 5.334" }
        ],
        minWidth: [
            { model: "billboard", title: "Dark Horse", artist: "Katy Perry and Juicy J", year: 2014, rank: 2, value: "α width = 0.218" },
            { model: "suno_v4_5", title: "Hot in Herre", artist: "Nelly", year: 2002, rank: 3, value: "α width = 0.59" },
            { model: "diffrhythm", title: "Auf Wiederseh'n Sweetheart", artist: "Vera Lynn", year: 1952, rank: 5, value: "α width = 0.837" },
            { model: "YuE", title: "rockstar", artist: "Post Malone feat. 21 Savage", year: 2018, rank: 5, value: "α width = 0.382" }
        ],
        maxSkew: [
            { model: "billboard", title: "Auf Wiederseh'n Sweetheart", artist: "Vera Lynn", year: 1952, rank: 5, value: "skew = 1.0" },
            { model: "suno_v4_5", title: "Good 4 U", artist: "Olivia Rodrigo", year: 2021, rank: 5, value: "skew = 0.833" },
            { model: "diffrhythm", title: "Poker Face", artist: "Lady Gaga", year: 2009, rank: 2, value: "skew = 0.924" },
            { model: "YuE", title: "Honey", artist: "Bobby Goldsboro", year: 1968, rank: 3, value: "skew = 1.0" }
        ],
        minSkew: [
            { model: "billboard", title: "Low", artist: "Flo Rida feat. T-Pain", year: 2008, rank: 1, value: "skew = -0.888" },
            { model: "suno_v4_5", title: "Hips Don't Lie", artist: "Shakira feat. Wyclef Jean", year: 2006, rank: 5, value: "skew = -0.846" },
            { model: "diffrhythm", title: "Without Me", artist: "Halsey", year: 2019, rank: 3, value: "skew = -0.787" },
            { model: "YuE", title: "Blue Tango", artist: "Leroy Anderson", year: 1952, rank: 1, value: "skew = -0.729" }
        ]
    },
    
    // JSD Comparison Results
    jsd: {
        best: [
            { model: "suno_v4_5", title: "End of the Road", artist: "Boyz II Men", year: 1992, value: "JSD = 0.007" },
            { model: "diffrhythm", title: "Bad Guy", artist: "Billie Eilish", year: 2019, value: "JSD = 0.013" },
            { model: "YuE", title: "Uptown Funk", artist: "Mark Ronson feat. Bruno Mars", year: 2015, value: "JSD = 0.010" }
        ],
        worst: [
            { model: "suno_v4_5", title: "Hot in Herre", artist: "Nelly", year: 2002, value: "JSD = 0.452" },
            { model: "diffrhythm", title: "Hanging By A Moment", artist: "Lifehouse", year: 2001, value: "JSD = 0.342" },
            { model: "YuE", title: "Straight Up", artist: "Paula Abdul", year: 1989, value: "JSD = 0.772" }
        ]
    }
};

// Function to create a song item element
function createSongItem(song) {
    const songDiv = document.createElement('div');
    songDiv.className = `song-item model-${song.model.toLowerCase()}`;
    
    // Try to find matching audio file
    const audioFile = findAudioFile(song);
    
    songDiv.innerHTML = `
        <div class="song-title">${song.title}</div>
        <div class="song-artist">${song.artist}</div>
        <div class="song-meta">${song.year}, Rank ${song.rank} • ${song.model}</div>
        <div class="song-value">${song.value}</div>
        <div class="audio-player">
            ${getAudioPlayer(song)}
        </div>
    `;
    
    return songDiv;
}

// Function to get appropriate audio player for a song
function getAudioPlayer(song) {
    console.log('Getting audio player for song:', song.title, 'by', song.artist, 'model:', song.model);
    
    // For Billboard music, use Spotify embeds
    if (song.model.toLowerCase() === 'billboard') {
        const spotifyEmbed = getSpotifyEmbed(song);
        if (spotifyEmbed) {
            console.log('Using Spotify embed for Billboard song');
            return `
                <div class="spotify-embed" id="spotify-${song.title.replace(/\s+/g, '-')}">
                    <iframe 
                        style="border-radius:12px" 
                        src="${spotifyEmbed}" 
                        width="100%" 
                        height="152" 
                        frameborder="0" 
                        allowfullscreen="" 
                        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
                        loading="lazy"
                        onload="console.log('Spotify iframe loaded successfully: ${song.title}')"
                        onerror="handleSpotifyError('${song.title}', '${song.artist}')"
                        onabort="handleSpotifyError('${song.title}', '${song.artist}')">
                    </iframe>
                    <div class="spotify-info">
                        <small>Spotify: ${song.title} by ${song.artist}</small>
                    </div>
                </div>
            `;
        } else {
            console.log('Spotify embed not found for Billboard song');
            return `
                <div class="audio-placeholder">
                    🎵 Spotify track not available
                    <br><small>(Original Billboard recording)</small>
                </div>
            `;
        }
    }
    
    // For AI-generated music, use audio files
    const audioFile = findAudioFile(song);
    console.log('Audio file found:', audioFile);
    if (audioFile) {
        return `
            <audio controls preload="metadata" style="width: 100%;" onerror="console.error('Audio loading error for:', '${audioFile}')" onloadstart="console.log('Loading audio:', '${audioFile}')">
                <source src="audio/${audioFile}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
        `;
    } else {
        return `
            <div class="audio-placeholder">
                🎵 Audio sample not available
                <br><small>(AI-generated audio file not uploaded yet)</small>
            </div>
        `;
    }
}

// Spotify track ID mapping for Billboard songs
const spotifyTrackIds = {
    // DFA Analysis - Closest to α=1.0
    "Bad Day - Daniel Powter": "0mUyMawtxj1CJ76kn9gIZK",
    
    // DFA Analysis - Min α
    "Let Me Love You - Mario": "3bNx3S9e3VR3EKtE4HZdnf",
    
    // DFA Analysis - Max α
    "Rockstar - DaBaby feat. Roddy Ricch": "17jTxlFxv1n5rc7uVJotLi",
    
    // MFDFA Analysis - Max Width
    "Sugar - Maroon 5": "2iuZJX9X9P0GKaE3cim7qU",
    
    // MFDFA Analysis - Min Width
    "Dark Horse - Katy Perry and Juicy J": "6jJ1R9cktKcMky9elKwZ0x",
    
    // MFDFA Analysis - Max Skew
    "Auf Wiederseh'n Sweetheart - Vera Lynn": "2QwMObGLHr5K7k6OZWiS5K",
    
    // MFDFA Analysis - Min Skew
    "Low - Flo Rida feat. T-Pain": "0CAfXk7DXMnon4gLudAp7J"
};

// Function to get Spotify embed URL for a song
function getSpotifyEmbed(song) {
    const songKey = `${song.title} - ${song.artist}`;
    const trackId = spotifyTrackIds[songKey];
    
    console.log('Spotify lookup:', {
        songKey: songKey,
        trackId: trackId,
        found: !!trackId
    });
    
    if (trackId) {
        const embedUrl = `https://open.spotify.com/embed/track/${trackId}`;
        console.log('Spotify embed URL:', embedUrl);
        return embedUrl;
    }
    
    console.log('No Spotify track found for:', songKey);
    return null;
}

// Function to find matching audio file
function findAudioFile(song) {
    // Load audio metadata if available
    const audioMetadata = window.audioMetadata || {};
    
    console.log('Looking for song:', song.title, 'by', song.artist, 'model:', song.model, 'year:', song.year);
    
    // Search for matching file based on song info
    for (const [fileId, metadata] of Object.entries(audioMetadata.files || {})) {
        // Parse the song field to extract title and artist
        const songParts = metadata.song.split(' - ');
        const metadataTitle = songParts[0] ? songParts[0].replace(/_/g, ' ').replace(/s_Theme/g, "'s Theme").replace(/Loves_Theme/g, "Love's Theme") : '';
        const metadataArtist = songParts[1] ? songParts[1].replace(/_/g, ' ') : '';
        
        // Normalize titles for comparison (remove apostrophes, extra spaces, etc.)
        const normalizedMetadataTitle = metadataTitle.toLowerCase().replace(/['']/g, '').replace(/\s+/g, ' ').trim();
        const normalizedSongTitle = song.title.toLowerCase().replace(/['']/g, '').replace(/\s+/g, ' ').trim();
        const normalizedMetadataArtist = metadataArtist.toLowerCase().replace(/\s+/g, ' ').trim();
        const normalizedSongArtist = song.artist.toLowerCase().replace(/\s+/g, ' ').trim();
        
        const modelMatch = metadata.model.toLowerCase() === song.model.toLowerCase();
        const titleMatch = normalizedMetadataTitle === normalizedSongTitle;
        const artistMatch = normalizedMetadataArtist === normalizedSongArtist;
        const yearMatch = metadata.year === song.year;
        
        console.log('Comparing with metadata:', {
            metadataTitle: metadataTitle,
            metadataArtist: metadataArtist,
            modelMatch,
            titleMatch,
            artistMatch,
            yearMatch
        });
        
        if (modelMatch && titleMatch && artistMatch && yearMatch) {
            console.log('Found matching audio file:', metadata.file);
            return metadata.file;
        }
    }
    
    console.log('No matching audio file found in metadata for:', song.title, 'by', song.artist);
    
    // Fallback: try to construct filename that matches actual file pattern
    const safeTitle = song.title.replace(/[^a-zA-Z0-9\s]/g, '').replace(/\s+/g, '_');
    const safeArtist = song.artist.replace(/[^a-zA-Z0-9\s]/g, '').replace(/\s+/g, '_');
    
    // Preserve original case for model names
    let modelPrefix;
    switch(song.model.toLowerCase()) {
        case 'yue':
            modelPrefix = 'YuE';
            break;
        case 'suno_v4_5':
            modelPrefix = 'suno_v4_5';
            break;
        case 'diffrhythm':
            modelPrefix = 'diffrhythm';
            break;
        default:
            modelPrefix = song.model;
    }
    
    // Handle special cases for rank
    const rank = song.rank || 'undefined';
    
    const possibleFilename = `${modelPrefix}_${song.year}_${rank}_${safeArtist}_${safeTitle}.mp3`;
    
    console.log('Generated fallback filename:', possibleFilename);
    return possibleFilename;
}

// Function to populate a section with songs
function populateSection(sectionId, songs) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.innerHTML = '';
        songs.forEach(song => {
            section.appendChild(createSongItem(song));
        });
    }
}

// Function to load audio metadata
async function loadAudioMetadata() {
    try {
        console.log('Loading audio metadata...');
        const response = await fetch('audio_metadata.json?v=10');
        console.log('Metadata response status:', response.status);
        if (response.ok) {
            const metadata = await response.json();
            window.audioMetadata = metadata;
            console.log(`Loaded metadata for ${Object.keys(metadata.files || {}).length} audio files`);
            console.log('Metadata keys:', Object.keys(metadata.files || {}));
        } else {
            console.log('No audio metadata file found, using fallback filename matching');
            window.audioMetadata = {};
        }
    } catch (error) {
        console.log('Could not load audio metadata:', error);
        window.audioMetadata = {};
    }
}

// Function to check if running locally
function isLocalhost() {
    return window.location.hostname === 'localhost' || 
           window.location.hostname === '127.0.0.1' || 
           window.location.hostname === '';
}

// Function to handle Spotify track loading errors
function handleSpotifyError(title, artist) {
    console.error(`Spotify iframe failed to load: ${title} by ${artist}`);
    
    // Find the Spotify container and replace with error message
    const containerId = `spotify-${title.replace(/\s+/g, '-')}`;
    const container = document.getElementById(containerId);
    
    if (container) {
        container.innerHTML = `
            <div class="audio-placeholder">
                🎵 Spotify track unavailable
                <br><small>${title} by ${artist}</small>
                <br><small>(Track may be restricted or removed)</small>
            </div>
        `;
    }
}

// Initialize the page when DOM is loaded
document.addEventListener('DOMContentLoaded', async function() {
    console.log('DOM loaded, starting initialization...');
    
    // Show debug links only on localhost
    const debugLinks = document.getElementById('debug-links');
    if (debugLinks && isLocalhost()) {
        debugLinks.style.display = 'block';
        console.log('Debug links enabled for localhost');
    }
    
    // Load audio metadata first
    await loadAudioMetadata();
    
    // Test audio file accessibility (only on localhost)
    if (isLocalhost()) {
        console.log('Testing audio file accessibility...');
        const testFiles = [
            'audio/suno_v4_5_2023_4_Taylor_Swift_Anti-Hero.mp3',
            'audio/YuE_1957_1_Elvis_Presley_All_Shook_Up.mp3'
        ];
        
        for (const file of testFiles) {
            try {
                const response = await fetch(file, { method: 'HEAD' });
                console.log(`${file}: ${response.ok ? '✅ Accessible' : '❌ Not accessible'} (${response.status})`);
            } catch (error) {
                console.error(`${file}: ❌ Error - ${error.message}`);
            }
        }
    }
    
    // Populate DFA sections
    populateSection('dfa-closest', songData.dfa.closest);
    populateSection('dfa-min', songData.dfa.min);
    populateSection('dfa-max', songData.dfa.max);
    
    // Populate MFDFA sections
    populateSection('mfdfa-max-width', songData.mfdfa.maxWidth);
    populateSection('mfdfa-min-width', songData.mfdfa.minWidth);
    populateSection('mfdfa-max-skew', songData.mfdfa.maxSkew);
    populateSection('mfdfa-min-skew', songData.mfdfa.minSkew);
    
    // Populate JSD sections
    populateSection('jsd-best', songData.jsd.best);
    populateSection('jsd-worst', songData.jsd.worst);
    
    console.log('Billboard AI Fractal Comparison website loaded successfully!');
});
