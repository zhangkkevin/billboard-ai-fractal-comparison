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
            { model: "suno_v4_5", title: "Youre Beautiful", artist: "James Blunt", year: 2006, rank: 4, value: "α = 1.25" },
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
            { model: "suno_v4_5", title: "Hips Dont Lie", artist: "Shakira feat. Wyclef Jean", year: 2006, rank: 5, value: "skew = -0.846" },
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
    // For Billboard music, use YouTube embeds
    if (song.model.toLowerCase() === 'billboard') {
        const youtubeEmbed = getYouTubeEmbed(song);
        if (youtubeEmbed) {
            return `
                <div class="youtube-embed">
                    <iframe 
                        width="100%" 
                        height="166" 
                        src="${youtubeEmbed}" 
                        title="${song.title} by ${song.artist}"
                        frameborder="0" 
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                        allowfullscreen>
                    </iframe>
                </div>
            `;
        } else {
            return `
                <div class="audio-placeholder">
                    🎵 YouTube video not available
                    <br><small>(Original Billboard recording)</small>
                </div>
            `;
        }
    }
    
    // For AI-generated music, use audio files
    const audioFile = findAudioFile(song);
    if (audioFile) {
        return `
            <audio controls preload="metadata" style="width: 100%;">
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

// Function to find matching audio file
function findAudioFile(song) {
    // Load audio metadata if available
    const audioMetadata = window.audioMetadata || {};
    
    // Search for matching file based on song info
    for (const [fileId, metadata] of Object.entries(audioMetadata.files || {})) {
        // Parse the song field to extract title and artist
        const songParts = metadata.song.split(' - ');
        const metadataTitle = songParts[0] || '';
        const metadataArtist = songParts[1] || '';
        
        // Normalize both metadata and song data for comparison
        const normalizeString = (str) => {
            return str.replace(/[._]/g, ' ').replace(/\s+/g, ' ').trim().toLowerCase();
        };
        
        const normalizedMetadataTitle = normalizeString(metadataTitle);
        const normalizedMetadataArtist = normalizeString(metadataArtist);
        const normalizedSongTitle = normalizeString(song.title);
        const normalizedSongArtist = normalizeString(song.artist);
        
        // Check if model, title, artist, and year match
        if (metadata.model.toLowerCase() === song.model.toLowerCase() &&
            normalizedMetadataTitle === normalizedSongTitle &&
            normalizedMetadataArtist === normalizedSongArtist &&
            metadata.year === song.year) {
            console.log(`Found match: ${metadata.file} for ${song.title} - ${song.artist}`);
            return metadata.file;
        }
    }
    
    console.log(`No match found for: ${song.title} - ${song.artist} (${song.model}, ${song.year})`);
    return null;
}

// YouTube video ID mapping for Billboard songs
const youtubeVideoIds = {
    // DFA Analysis - Closest to α=1.0
    "Bad Day - Daniel Powter": "eN_SVw-yyhA",
    "Anti-Hero - Taylor Swift": "b1kbLWf8aQY", 
    "Claudette - The Everly Brothers": "8qHhVJtQj-s",
    "All Shook Up - Elvis Presley": "lzXgnX8aXzI",
    
    // DFA Analysis - Min α
    "Let Me Love You - Mario": "mbG5fhlMdrI",
    "Love's Theme - Love Unlimited Orchestra": "8bfyS-S-TcA", // Placeholder
    "Hanging By A Moment - Lifehouse": "t4QK8RxCAwo",
    "Harlem Shake - Baauer": "8UFIYGkROII",
    
    // DFA Analysis - Max α
    "Rockstar - DaBaby feat. Roddy Ricch": "83xBPCw5hh4",
    "Youre Beautiful - James Blunt": "oofSnsGkops",
    "Mona Lisa - Nat King Cole": "8bfyS-S-TcA", // Placeholder
    "Blue Tango - Leroy Anderson": "8bfyS-S-TcA", // Placeholder
    
    // MFDFA Analysis - Max Width
    "Sugar - Maroon 5": "N1BcpzPGlYQ",
    "The Yellow Rose of Texas - Mitch Miller": "8bfyS-S-TcA", // Placeholder
    "When I'm Gone - 3 Doors Down": "kXYiU_JCYtU",
    "The Sweet Escape - Gwen Stefani feat. Akon": "OJB8ZjGJ8YI",
    
    // MFDFA Analysis - Min Width
    "Dark Horse - Katy Perry and Juicy J": "ONb4aTtG6Ps",
    "Hot in Herre - Nelly": "GeZZr_p6vB8",
    "Auf Wiederseh'n Sweetheart - Vera Lynn": "8bfyS-S-TcA", // Placeholder
    "rockstar - Post Malone feat. 21 Savage": "UceaB4D0jpo",
    
    // MFDFA Analysis - Max Skew
    "Auf Wiederseh'n Sweetheart - Vera Lynn": "36prRdWCqu0", // Placeholder
    "Good 4 U - Olivia Rodrigo": "gNi_6U5Pm_o",
    "Poker Face - Lady Gaga": "bESGLojNYSo",
    "Honey - Bobby Goldsboro": "8bfyS-S-TcA", // Placeholder
    
    // MFDFA Analysis - Min Skew
    "Low - Flo Rida feat. T-Pain": "CxPc1Q3-0zc",
    "Hips Dont Lie - Shakira feat. Wyclef Jean": "DUT5rEU6pqM",
    "Without Me - Halsey": "Y7dpJ0oseIA",
    "Blue Tango - Leroy Anderson": "8bfyS-S-TcA", // Placeholder
    
    // JSD Analysis - Best
    "End of the Road - Boyz II Men": "zDKO6XYXioc",
    "Bad Guy - Billie Eilish": "DdyweUxXgFY",
    "Uptown Funk - Mark Ronson feat. Bruno Mars": "OPf0YbXqDm0",
    
    // JSD Analysis - Worst
    "Hot in Herre - Nelly": "GeZZr_p6vB8",
    "Hanging By A Moment - Lifehouse": "t4QK8RxCAwo",
    "Straight Up - Paula Abdul": "kXYiU_JCYtU" // Placeholder
};

// Function to get YouTube embed URL for a song
function getYouTubeEmbed(song) {
    const songKey = `${song.title} - ${song.artist}`;
    const videoId = youtubeVideoIds[songKey];
    
    if (videoId) {
        return `https://www.youtube.com/embed/${videoId}`;
    }
    
    return null;
}

// Function to load audio metadata
async function loadAudioMetadata() {
    try {
        const response = await fetch('audio_metadata.json?v=3');
        if (response.ok) {
            const metadata = await response.json();
            window.audioMetadata = metadata;
            console.log(`Loaded metadata for ${Object.keys(metadata.files || {}).length} audio files`);
            
            // Debug: Log first few entries
            const entries = Object.entries(metadata.files || {});
            console.log('First 3 metadata entries:');
            entries.slice(0, 3).forEach(([id, data]) => {
                console.log(`  ${data.song} -> ${data.file}`);
            });
        } else {
            console.log('No audio metadata file found, using fallback filename matching');
            window.audioMetadata = {};
        }
    } catch (error) {
        console.log('Could not load audio metadata:', error);
        window.audioMetadata = {};
    }
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

// Initialize the page when DOM is loaded
document.addEventListener('DOMContentLoaded', async function() {
    // Load audio metadata first
    await loadAudioMetadata();
    
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
