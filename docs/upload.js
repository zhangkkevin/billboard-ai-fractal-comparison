// Audio Upload and Management System
class AudioUploadManager {
    constructor() {
        this.uploadForm = document.getElementById('uploadForm');
        this.fileList = document.getElementById('fileList');
        this.progressBar = document.getElementById('progressBar');
        this.progressFill = document.getElementById('progressFill');
        this.statusMessage = document.getElementById('statusMessage');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.fileInput = document.getElementById('audio_file');
        this.fileInfo = document.getElementById('file_info');
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadAudioFiles();
    }
    
    setupEventListeners() {
        // File input change handler
        this.fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e);
        });
        
        // Form submission handler
        this.uploadForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleUpload();
        });
        
        // Category change handler to update value placeholder
        document.getElementById('category').addEventListener('change', (e) => {
            this.updateValuePlaceholder(e.target.value);
        });
    }
    
    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            const fileSize = this.formatFileSize(file.size);
            const fileType = file.type;
            this.fileInfo.textContent = `Selected: ${file.name} (${fileSize}, ${fileType})`;
        } else {
            this.fileInfo.textContent = '';
        }
    }
    
    updateValuePlaceholder(category) {
        const valueInput = document.getElementById('value');
        const placeholders = {
            'closest': 'e.g., α = 1.0',
            'min': 'e.g., α = 0.767',
            'max': 'e.g., α = 1.267',
            'max_width': 'e.g., α width = 4.874',
            'min_width': 'e.g., α width = 0.218',
            'max_skew': 'e.g., skew = 1.0',
            'min_skew': 'e.g., skew = -0.888',
            'best': 'e.g., JSD = 0.007',
            'worst': 'e.g., JSD = 0.452'
        };
        valueInput.placeholder = placeholders[category] || 'e.g., α = 1.0, JSD = 0.007';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    async handleUpload() {
        const formData = new FormData(this.uploadForm);
        const file = this.fileInput.files[0];
        
        if (!file) {
            this.showStatus('Please select an audio file.', 'error');
            return;
        }
        
        // Validate file type
        if (!file.type.startsWith('audio/')) {
            this.showStatus('Please select a valid audio file.', 'error');
            return;
        }
        
        // Validate file size (max 50MB)
        if (file.size > 50 * 1024 * 1024) {
            this.showStatus('File size must be less than 50MB.', 'error');
            return;
        }
        
        this.uploadBtn.disabled = true;
        this.uploadBtn.textContent = 'Uploading...';
        this.progressBar.style.display = 'block';
        
        try {
            // Simulate upload progress (in real implementation, this would be actual upload)
            await this.simulateUpload(formData);
            
            this.showStatus('Audio file uploaded successfully!', 'success');
            this.uploadForm.reset();
            this.fileInfo.textContent = '';
            this.loadAudioFiles(); // Refresh the file list
            
        } catch (error) {
            this.showStatus(`Upload failed: ${error.message}`, 'error');
        } finally {
            this.uploadBtn.disabled = false;
            this.uploadBtn.textContent = 'Upload Audio File';
            this.progressBar.style.display = 'none';
            this.progressFill.style.width = '0%';
        }
    }
    
    async simulateUpload(formData) {
        return new Promise((resolve, reject) => {
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 100) progress = 100;
                
                this.progressFill.style.width = progress + '%';
                
                if (progress >= 100) {
                    clearInterval(interval);
                    setTimeout(() => {
                        // In a real implementation, this would be an actual file upload
                        // For now, we'll just store the data locally
                        this.saveAudioData(formData);
                        resolve();
                    }, 500);
                }
            }, 200);
        });
    }
    
    saveAudioData(formData) {
        const audioData = {
            id: Date.now(),
            model: formData.get('model'),
            title: formData.get('title'),
            artist: formData.get('artist'),
            year: formData.get('year'),
            rank: formData.get('rank'),
            analysis_type: formData.get('analysis_type'),
            category: formData.get('category'),
            value: formData.get('value'),
            notes: formData.get('notes'),
            filename: this.fileInput.files[0].name,
            upload_date: new Date().toISOString(),
            file_size: this.fileInput.files[0].size
        };
        
        // Get existing data or initialize empty array
        const existingData = JSON.parse(localStorage.getItem('audioFiles') || '[]');
        existingData.push(audioData);
        localStorage.setItem('audioFiles', JSON.stringify(existingData));
    }
    
    loadAudioFiles() {
        const audioFiles = JSON.parse(localStorage.getItem('audioFiles') || '[]');
        
        if (audioFiles.length === 0) {
            this.fileList.innerHTML = '<p>No audio files uploaded yet.</p>';
            return;
        }
        
        this.fileList.innerHTML = '';
        
        audioFiles.forEach(file => {
            const fileItem = this.createFileItem(file);
            this.fileList.appendChild(fileItem);
        });
    }
    
    createFileItem(file) {
        const fileDiv = document.createElement('div');
        fileDiv.className = 'file-item';
        
        fileDiv.innerHTML = `
            <div class="file-info">
                <div class="file-name">${file.title} - ${file.artist}</div>
                <div class="file-meta">
                    ${file.year}, Rank ${file.rank} • ${file.model} • ${file.analysis_type} • ${file.category}
                    <br>${file.value} • ${this.formatFileSize(file.file_size)}
                </div>
            </div>
            <div class="file-actions">
                <button class="btn btn-play" onclick="audioManager.playAudio('${file.id}')">Play</button>
                <button class="btn btn-delete" onclick="audioManager.deleteAudio('${file.id}')">Delete</button>
            </div>
        `;
        
        return fileDiv;
    }
    
    playAudio(fileId) {
        const audioFiles = JSON.parse(localStorage.getItem('audioFiles') || '[]');
        const file = audioFiles.find(f => f.id == fileId);
        
        if (file) {
            // In a real implementation, this would play the actual audio file
            // For now, we'll show a message
            this.showStatus(`Playing: ${file.title} by ${file.artist}`, 'success');
            
            // Create a temporary audio element (this would work with actual file URLs)
            const audio = new Audio();
            audio.src = `audio/${file.filename}`;
            audio.play().catch(e => {
                this.showStatus(`Audio playback failed: ${e.message}`, 'error');
            });
        }
    }
    
    deleteAudio(fileId) {
        if (confirm('Are you sure you want to delete this audio file?')) {
            const audioFiles = JSON.parse(localStorage.getItem('audioFiles') || '[]');
            const updatedFiles = audioFiles.filter(f => f.id != fileId);
            localStorage.setItem('audioFiles', JSON.stringify(updatedFiles));
            
            this.showStatus('Audio file deleted successfully.', 'success');
            this.loadAudioFiles(); // Refresh the list
        }
    }
    
    showStatus(message, type) {
        this.statusMessage.textContent = message;
        this.statusMessage.className = `status-message status-${type}`;
        
        setTimeout(() => {
            this.statusMessage.textContent = '';
            this.statusMessage.className = 'status-message';
        }, 5000);
    }
}

// Initialize the upload manager when the page loads
let audioManager;
document.addEventListener('DOMContentLoaded', function() {
    audioManager = new AudioUploadManager();
});

// Export for use in other scripts
window.AudioUploadManager = AudioUploadManager;


