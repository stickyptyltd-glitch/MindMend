class VideoProcessor {
    constructor() {
        this.stream = null;
        this.isActive = false;
        this.canvas = null;
        this.context = null;
        this.frameRate = 5; // Frames per second for analysis
        this.analysisInterval = null;
    }

    async startCapture(videoElementId) {
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

            const videoElement = document.getElementById(videoElementId);
            if (videoElement) {
                videoElement.srcObject = this.stream;
                videoElement.play();
            }

            // Create canvas for frame capture
            this.canvas = document.createElement('canvas');
            this.context = this.canvas.getContext('2d');
            
            this.isActive = true;
            console.log('Video capture started successfully');
            
            return true;
        } catch (error) {
            console.error('Error starting video capture:', error);
            throw new Error('Camera access denied or not available');
        }
    }

    stopCapture() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        if (this.analysisInterval) {
            clearInterval(this.analysisInterval);
            this.analysisInterval = null;
        }
        
        this.isActive = false;
        console.log('Video capture stopped');
    }

    async getCurrentFrame() {
        if (!this.isActive || !this.stream) {
            return null;
        }

        try {
            const videoElement = document.querySelector('video');
            if (!videoElement || videoElement.readyState < 2) {
                return null;
            }

            // Set canvas size to match video
            this.canvas.width = videoElement.videoWidth;
            this.canvas.height = videoElement.videoHeight;

            // Draw current video frame to canvas
            this.context.drawImage(videoElement, 0, 0);

            // Convert to base64
            const dataURL = this.canvas.toDataURL('image/jpeg', 0.8);
            return dataURL.split(',')[1]; // Remove data:image/jpeg;base64, prefix
        } catch (error) {
            console.error('Error capturing frame:', error);
            return null;
        }
    }

    startRealTimeAnalysis(callback, interval = 2000) {
        if (this.analysisInterval) {
            clearInterval(this.analysisInterval);
        }

        this.analysisInterval = setInterval(async () => {
            if (!this.isActive) return;

            const frameData = await this.getCurrentFrame();
            if (frameData && callback) {
                callback(frameData);
            }
        }, interval);
    }

    stopRealTimeAnalysis() {
        if (this.analysisInterval) {
            clearInterval(this.analysisInterval);
            this.analysisInterval = null;
        }
    }

    isActive() {
        return this.isActive;
    }

    // Get video quality metrics
    getVideoQuality() {
        const videoElement = document.querySelector('video');
        if (!videoElement) return null;

        return {
            width: videoElement.videoWidth,
            height: videoElement.videoHeight,
            readyState: videoElement.readyState,
            currentTime: videoElement.currentTime
        };
    }

    // Check if camera is available
    static async checkCameraAvailability() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(device => device.kind === 'videoinput');
            return videoDevices.length > 0;
        } catch (error) {
            console.error('Error checking camera availability:', error);
            return false;
        }
    }

    // Get camera permissions status
    static async getCameraPermissions() {
        try {
            const permission = await navigator.permissions.query({ name: 'camera' });
            return permission.state; // 'granted', 'denied', or 'prompt'
        } catch (error) {
            console.error('Error checking camera permissions:', error);
            return 'unknown';
        }
    }
}

// Face detection utilities
class FaceDetection {
    constructor() {
        this.detector = null;
        this.isLoaded = false;
    }

    async initialize() {
        try {
            // In a real implementation, you would load a face detection library
            // like MediaPipe Face Detection or TensorFlow.js
            console.log('Face detection initialized (mock)');
            this.isLoaded = true;
            return true;
        } catch (error) {
            console.error('Error initializing face detection:', error);
            return false;
        }
    }

    async detectFaces(imageData) {
        if (!this.isLoaded) {
            console.warn('Face detection not initialized');
            return [];
        }

        // Mock face detection results
        // In a real implementation, this would use actual face detection
        return [{
            x: 100,
            y: 100,
            width: 200,
            height: 200,
            confidence: 0.95,
            landmarks: {
                leftEye: { x: 150, y: 140 },
                rightEye: { x: 220, y: 140 },
                nose: { x: 185, y: 170 },
                mouth: { x: 185, y: 210 }
            }
        }];
    }
}

// Emotion analysis utilities
class EmotionAnalysis {
    constructor() {
        this.emotions = [
            'neutral', 'happy', 'sad', 'angry', 
            'fearful', 'disgusted', 'surprised'
        ];
    }

    async analyzeEmotion(faceData) {
        // Mock emotion analysis
        // In a real implementation, this would use actual emotion recognition
        const emotionScores = {};
        
        this.emotions.forEach(emotion => {
            emotionScores[emotion] = Math.random();
        });

        // Normalize scores
        const total = Object.values(emotionScores).reduce((sum, score) => sum + score, 0);
        Object.keys(emotionScores).forEach(emotion => {
            emotionScores[emotion] = emotionScores[emotion] / total;
        });

        return emotionScores;
    }

    getPrimaryEmotion(emotionScores) {
        return Object.keys(emotionScores).reduce((a, b) => 
            emotionScores[a] > emotionScores[b] ? a : b
        );
    }
}

// Export classes for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VideoProcessor, FaceDetection, EmotionAnalysis };
}
