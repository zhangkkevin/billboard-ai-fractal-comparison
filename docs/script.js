// Song data from the analysis results
const songData = {
    // DFA Analysis Results
    dfa: {
        closest: [
            { model: "Billboard", title: "Bad Day", artist: "Daniel Powter", year: 2006, rank: 1, value: "α = 1.0" },
            { model: "Suno", title: "Anti-Hero", artist: "Taylor Swift", year: 2023, rank: 4, value: "α = 1.0" },
            { model: "DiffRhythm", title: "Claudette", artist: "The Everly Brothers", year: 1958, rank: "2b", value: "α = 1.0" },
            { model: "YuE", title: "All Shook Up", artist: "Elvis Presley", year: 1957, rank: 1, value: "α = 1.0" }
        ],
        min: [
            { model: "Billboard", title: "Let Me Love You", artist: "Mario", year: 2005, rank: 3, value: "α = 0.767" },
            { model: "Suno", title: "Love's Theme", artist: "Love Unlimited Orchestra", year: 1974, rank: 3, value: "α = 0.679" },
            { model: "DiffRhythm", title: "Hanging By A Moment", artist: "Lifehouse", year: 2001, rank: 1, value: "α = 0.702" },
            { model: "YuE", title: "Harlem Shake", artist: "Baauer", year: 2013, rank: 4, value: "α = 0.721" }
        ],
        max: [
            { model: "Billboard", title: "Rockstar", artist: "DaBaby feat. Roddy Ricch", year: 2020, rank: 5, value: "α = 1.267" },
            { model: "Suno", title: "You're Beautiful", artist: "James Blunt", year: 2006, rank: 4, value: "α = 1.25" },
            { model: "DiffRhythm", title: "Mona Lisa", artist: "Nat King Cole", year: 1950, rank: 2, value: "α = 1.257" },
            { model: "YuE", title: "Blue Tango", artist: "Leroy Anderson", year: 1952, rank: 1, value: "α = 1.413" }
        ]
    },
    
    // MFDFA Analysis Results
    mfdfa: {
        maxWidth: [
            { model: "Billboard", title: "Sugar", artist: "Maroon 5", year: 2015, rank: 5, value: "α width = 4.874" },
            { model: "Suno", title: "The Yellow Rose of Texas", artist: "Mitch Miller", year: 1955, rank: 3, value: "α width = 4.716" },
            { model: "DiffRhythm", title: "When I'm Gone", artist: "3 Doors Down", year: 2003, rank: 5, value: "α width = 3.399" },
            { model: "YuE", title: "The Sweet Escape", artist: "Gwen Stefani feat. Akon", year: 2007, rank: 3, value: "α width = 5.334" }
        ],
        minWidth: [
            { model: "Billboard", title: "Dark Horse", artist: "Katy Perry and Juicy J", year: 2014, rank: 2, value: "α width = 0.218" },
            { model: "Suno", title: "Hot in Herre", artist: "Nelly", year: 2002, rank: 3, value: "α width = 0.59" },
            { model: "DiffRhythm", title: "Auf Wiederseh'n Sweetheart", artist: "Vera Lynn", year: 1952, rank: 5, value: "α width = 0.837" },
            { model: "YuE", title: "rockstar", artist: "Post Malone feat. 21 Savage", year: 2018, rank: 5, value: "α width = 0.382" }
        ],
        maxSkew: [
            { model: "Billboard", title: "Auf Wiederseh'n Sweetheart", artist: "Vera Lynn", year: 1952, rank: 5, value: "skew = 1.0" },
            { model: "Suno", title: "Good 4 U", artist: "Olivia Rodrigo", year: 2021, rank: 5, value: "skew = 0.833" },
            { model: "DiffRhythm", title: "Poker Face", artist: "Lady Gaga", year: 2009, rank: 2, value: "skew = 0.924" },
            { model: "YuE", title: "Honey", artist: "Bobby Goldsboro", year: 1968, rank: 3, value: "skew = 1.0" }
        ],
        minSkew: [
            { model: "Billboard", title: "Low", artist: "Flo Rida feat. T-Pain", year: 2008, rank: 1, value: "skew = -0.888" },
            { model: "Suno", title: "Hips Don't Lie", artist: "Shakira feat. Wyclef Jean", year: 2006, rank: 5, value: "skew = -0.846" },
            { model: "DiffRhythm", title: "Without Me", artist: "Halsey", year: 2019, rank: 3, value: "skew = -0.787" },
            { model: "YuE", title: "Blue Tango", artist: "Leroy Anderson", year: 1952, rank: 1, value: "skew = -0.729" }
        ]
    },
    
    // JSD Comparison Results
    jsd: {
        best: [
            { model: "Suno", title: "End of the Road", artist: "Boyz II Men", year: 1992, value: "JSD = 0.007" },
            { model: "DiffRhythm", title: "Bad Guy", artist: "Billie Eilish", year: 2019, value: "JSD = 0.013" },
            { model: "YuE", title: "Uptown Funk", artist: "Mark Ronson feat. Bruno Mars", year: 2015, value: "JSD = 0.010" }
        ],
        worst: [
            { model: "Suno", title: "Hot in Herre", artist: "Nelly", year: 2002, value: "JSD = 0.452" },
            { model: "DiffRhythm", title: "Hanging By A Moment", artist: "Lifehouse", year: 2001, value: "JSD = 0.342" },
            { model: "YuE", title: "Straight Up", artist: "Paula Abdul", year: 1989, value: "JSD = 0.772" }
        ]
    }
};

// Function to create a song item element
function createSongItem(song) {
    const songDiv = document.createElement('div');
    songDiv.className = `song-item model-${song.model.toLowerCase()}`;
    
    songDiv.innerHTML = `
        <div class="song-title">${song.title}</div>
        <div class="song-artist">${song.artist}</div>
        <div class="song-meta">${song.year}, Rank ${song.rank} • ${song.model}</div>
        <div class="song-value">${song.value}</div>
        <div class="audio-placeholder">
            🎵 Audio sample would be embedded here
            <br><small>(Due to copyright, audio files are not included)</small>
        </div>
    `;
    
    return songDiv;
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
document.addEventListener('DOMContentLoaded', function() {
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
