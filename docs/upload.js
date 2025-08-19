// Upload functionality
class AudioUploader {
    constructor() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.fileList = document.getElementById('fileList');
        this.files = [];
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // File input change
        this.fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });
        
        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });
        
        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
        });
        
        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });
        
        // Click to select
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });
    }
    
    handleFiles(fileList) {
        Array.from(fileList).forEach(file => {
            if (file.type.startsWith('audio/')) {
                this.addFile(file);
            } else {
                this.showError(`${file.name} is not an audio file`);
            }
        });
    }
    
    addFile(file) {
        const fileId = this.generateFileId();
        const fileItem = {
            id: fileId,
            file: file,
            name: file.name,
            size: file.size,
            status: 'pending'
        };
        
        this.files.push(fileItem);
        this.renderFileItem(fileItem);
        this.uploadFile(fileItem);
    }
    
    generateFileId() {
        return 'file_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    renderFileItem(fileItem) {
        const fileElement = document.createElement('div');
        fileElement.className = 'file-item';
        fileElement.id = fileItem.id;
        
        const fileSize = this.formatFileSize(fileItem.size);
        
        fileElement.innerHTML = `
            <div class="file-info">
                <div class="file-name">${fileItem.name}</div>
                <div class="file-size">${fileSize}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%"></div>
                </div>
            </div>
            <div class="file-status status-uploading">Uploading...</div>
        `;
        
        this.fileList.appendChild(fileElement);
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    async uploadFile(fileItem) {
        try {
            const formData = new FormData();
            formData.append('audio', fileItem.file);
            
            // Simulate upload progress
            const progressElement = document.querySelector(`#${fileItem.id} .progress-fill`);
            const statusElement = document.querySelector(`#${fileItem.id} .file-status`);
            
            // Simulate progress
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 20;
                if (progress > 90) progress = 90;
                progressElement.style.width = progress + '%';
            }, 200);
            
            // In a real implementation, you would send the file to a server
            // For now, we'll simulate a successful upload
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            clearInterval(progressInterval);
            progressElement.style.width = '100%';
            
            // Update status
            fileItem.status = 'success';
            statusElement.textContent = 'Uploaded';
            statusElement.className = 'file-status status-success';
            
            this.showSuccess(`${fileItem.name} uploaded successfully`);
            
        } catch (error) {
            fileItem.status = 'error';
            const statusElement = document.querySelector(`#${fileItem.id} .file-status`);
            statusElement.textContent = 'Error';
            statusElement.className = 'file-status status-error';
            
            this.showError(`Failed to upload ${fileItem.name}: ${error.message}`);
        }
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        if (type === 'success') {
            notification.style.background = '#38a169';
        } else {
            notification.style.background = '#e53e3e';
        }
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize uploader when page loads
document.addEventListener('DOMContentLoaded', () => {
    new AudioUploader();
});
