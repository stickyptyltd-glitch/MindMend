// Video Processing Module for Mind Mend
class VideoProcessor {
    constructor() {
        this.video = null;
        this.stream = null;
        this.canvas = document.createElement('canvas');
        this.context = this.canvas.getContext('2d');
        this.captureInterval = null;
    }

    async startCapture(videoElement) {
        this.video = videoElement;
        
        try {
            // Request camera access
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                },
                audio: false 
            });
            
            this.video.srcObject = this.stream;
            await this.video.play();
            
            // Set canvas dimensions
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            
            return true;
        } catch (error) {
            console.error('Error accessing camera:', error);
            throw error;
        }
    }

    stopCapture() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        if (this.captureInterval) {
            clearInterval(this.captureInterval);
            this.captureInterval = null;
        }
        
        if (this.video) {
            this.video.srcObject = null;
        }
    }

    async getCurrentFrame() {
        if (!this.video || this.video.readyState !== 4) {
            return null;
        }
        
        try {
            // Draw current video frame to canvas
            this.context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
            
            // Convert to base64
            const dataUrl = this.canvas.toDataURL('image/jpeg', 0.8);
            const base64 = dataUrl.split(',')[1];
            
            return {
                frame: base64,
                timestamp: Date.now(),
                width: this.canvas.width,
                height: this.canvas.height
            };
        } catch (error) {
            console.error('Error capturing frame:', error);
            return null;
        }
    }

    async analyzeFrame(frameData) {
        // Placeholder for local frame analysis
        // In production, this would use TensorFlow.js or similar
        return {
            faceDetected: true,
            facePosition: {
                x: this.canvas.width / 2,
                y: this.canvas.height / 2,
                width: 200,
                height: 200
            },
            quality: {
                brightness: 0.7,
                contrast: 0.8,
                blur: 0.1
            }
        };
    }

    drawFaceRectangle(faceData) {
        if (!faceData || !faceData.facePosition) return;
        
        const pos = faceData.facePosition;
        const overlayCanvas = document.createElement('canvas');
        overlayCanvas.style.position = 'absolute';
        overlayCanvas.style.top = '0';
        overlayCanvas.style.left = '0';
        overlayCanvas.style.pointerEvents = 'none';
        overlayCanvas.width = this.video.videoWidth;
        overlayCanvas.height = this.video.videoHeight;
        
        const ctx = overlayCanvas.getContext('2d');
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 3;
        ctx.strokeRect(pos.x - pos.width/2, pos.y - pos.height/2, pos.width, pos.height);
        
        // Add to video container
        this.video.parentElement.appendChild(overlayCanvas);
        
        // Remove after 1 second
        setTimeout(() => overlayCanvas.remove(), 1000);
    }
}

// Export for use in other modules
window.VideoProcessor = VideoProcessor;