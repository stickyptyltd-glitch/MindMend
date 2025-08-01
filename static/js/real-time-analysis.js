class RealTimeAnalyzer {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.analysisQueue = [];
        this.callbacks = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
    }

    // Initialize Socket.IO connection
    initialize() {
        try {
            this.socket = io();
            this.setupSocketEvents();
            console.log('Real-time analyzer initialized');
        } catch (error) {
            console.error('Failed to initialize Socket.IO:', error);
        }
    }

    setupSocketEvents() {
        this.socket.on('connect', () => {
            console.log('Connected to real-time analysis server');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            
            // Process any queued analysis requests
            this.processQueue();
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from real-time analysis server');
            this.isConnected = false;
            this.attemptReconnect();
        });

        this.socket.on('video_analysis', (data) => {
            this.handleVideoAnalysis(data);
        });

        this.socket.on('biometric_analysis', (data) => {
            this.handleBiometricAnalysis(data);
        });

        this.socket.on('text_analysis', (data) => {
            this.handleTextAnalysis(data);
        });

        this.socket.on('error', (error) => {
            console.error('Socket.IO error:', error);
        });

        this.socket.on('analysis_complete', (data) => {
            this.handleAnalysisComplete(data);
        });
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.socket.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
        }
    }

    // Send video frame for analysis
    analyzeVideoFrame(frameData, sessionId = null, options = {}) {
        const analysisData = {
            frame_data: frameData,
            session_id: sessionId,
            timestamp: Date.now(),
            options: {
                enable_emotions: true,
                enable_microexpressions: true,
                enable_gaze_tracking: true,
                ...options
            }
        };

        if (this.isConnected) {
            this.socket.emit('video_frame', analysisData);
        } else {
            this.queueAnalysis('video_frame', analysisData);
        }
    }

    // Send biometric data for analysis
    analyzeBiometricData(biometricData, sessionId = null) {
        const analysisData = {
            biometric_data: biometricData,
            session_id: sessionId,
            timestamp: Date.now()
        };

        if (this.isConnected) {
            this.socket.emit('biometric_update', analysisData);
        } else {
            this.queueAnalysis('biometric_update', analysisData);
        }
    }

    // Send text for real-time analysis
    analyzeText(text, sessionType = 'individual', context = {}) {
        const analysisData = {
            text: text,
            session_type: sessionType,
            context: context,
            timestamp: Date.now()
        };

        if (this.isConnected) {
            this.socket.emit('text_analysis', analysisData);
        } else {
            this.queueAnalysis('text_analysis', analysisData);
        }
    }

    // Start comprehensive multi-modal analysis
    startMultiModalAnalysis(config = {}) {
        const defaultConfig = {
            video: {
                enabled: true,
                frameRate: 2, // frames per second
                enableEmotions: true,
                enableMicroexpressions: true,
                enableGazeTracking: false
            },
            biometric: {
                enabled: true,
                updateInterval: 5000, // milliseconds
                devices: ['simulated'] // device types to monitor
            },
            text: {
                enabled: true,
                realTimeAnalysis: true,
                sentimentTracking: true
            },
            session: {
                sessionId: `session_${Date.now()}`,
                sessionType: 'individual',
                patientId: null
            }
        };

        const analysisConfig = { ...defaultConfig, ...config };

        if (this.isConnected) {
            this.socket.emit('start_multimodal_analysis', analysisConfig);
        } else {
            console.warn('Cannot start multi-modal analysis: not connected');
        }

        return analysisConfig.session.sessionId;
    }

    // Stop multi-modal analysis
    stopMultiModalAnalysis(sessionId) {
        if (this.isConnected) {
            this.socket.emit('stop_multimodal_analysis', { session_id: sessionId });
        }
    }

    // Queue analysis when disconnected
    queueAnalysis(eventType, data) {
        this.analysisQueue.push({ eventType, data, timestamp: Date.now() });
        
        // Limit queue size
        if (this.analysisQueue.length > 50) {
            this.analysisQueue.shift();
        }
    }

    // Process queued analysis requests
    processQueue() {
        while (this.analysisQueue.length > 0) {
            const { eventType, data } = this.analysisQueue.shift();
            this.socket.emit(eventType, data);
        }
    }

    // Event handlers
    handleVideoAnalysis(data) {
        const { session_id, analysis, timestamp } = data;
        
        // Update UI with video analysis results
        this.updateVideoAnalysisUI(analysis);
        
        // Trigger callbacks
        this.triggerCallbacks('video_analysis', data);
        
        // Store analysis data
        this.storeAnalysisData('video', data);
    }

    handleBiometricAnalysis(data) {
        const { analysis, timestamp } = data;
        
        // Update UI with biometric analysis
        this.updateBiometricAnalysisUI(analysis);
        
        // Trigger callbacks
        this.triggerCallbacks('biometric_analysis', data);
        
        // Check for health alerts
        if (analysis.alerts && analysis.alerts.length > 0) {
            this.handleHealthAlerts(analysis.alerts);
        }
    }

    handleTextAnalysis(data) {
        const { analysis, timestamp } = data;
        
        // Update UI with text analysis
        this.updateTextAnalysisUI(analysis);
        
        // Trigger callbacks
        this.triggerCallbacks('text_analysis', data);
    }

    handleAnalysisComplete(data) {
        const { session_id, comprehensive_analysis } = data;
        
        // Display comprehensive analysis results
        this.displayComprehensiveAnalysis(comprehensive_analysis);
        
        // Trigger completion callbacks
        this.triggerCallbacks('analysis_complete', data);
    }

    // UI Update Methods
    updateVideoAnalysisUI(analysis) {
        // Update emotion display
        if (analysis.emotions) {
            const primaryEmotion = this.getPrimaryEmotion(analysis.emotions);
            this.updateElement('primaryEmotion', primaryEmotion);
            this.updateElement('emotionConfidence', `${Math.round(analysis.confidence * 100)}%`);
            this.updateEmotionIndicator(primaryEmotion);
        }

        // Update stress level
        if (analysis.stress_level !== undefined) {
            const stressLevel = this.getStressLevelText(analysis.stress_level);
            this.updateElement('stressLevel', stressLevel);
            this.updateProgressBar('stressConfidence', analysis.stress_level * 100);
        }

        // Update engagement
        if (analysis.engagement_level !== undefined) {
            const engagementLevel = this.getEngagementLevelText(analysis.engagement_level);
            this.updateElement('engagementLevel', engagementLevel);
            this.updateProgressBar('engagementConfidence', analysis.engagement_level * 100);
        }

        // Show microexpression alerts
        if (analysis.microexpressions && Object.keys(analysis.microexpressions).length > 0) {
            this.showMicroexpressionAlert(analysis.microexpressions);
        }
    }

    updateBiometricAnalysisUI(analysis) {
        // Update current biometric values
        if (analysis.current_state) {
            const state = analysis.current_state;
            this.updateElement('heartRate', state.heart_rate || '--');
            this.updateElement('stressLevel', state.stress_level || '--');
            this.updateBiometricStatus('hrStatus', state.heart_rate);
            this.updateBiometricStatus('stressStatus', state.stress_level);
        }

        // Update recommendations
        if (analysis.recommendations) {
            this.updateRecommendations(analysis.recommendations);
        }

        // Show alerts
        if (analysis.alerts) {
            this.showBiometricAlerts(analysis.alerts);
        }
    }

    updateTextAnalysisUI(analysis) {
        // Update sentiment indicators
        if (analysis.sentiment) {
            this.updateSentimentDisplay(analysis.sentiment);
        }

        // Show risk indicators
        if (analysis.risk_level) {
            this.updateRiskLevelDisplay(analysis.risk_level);
        }

        // Update topic analysis
        if (analysis.topics) {
            this.updateTopicDisplay(analysis.topics);
        }
    }

    // Utility methods
    getPrimaryEmotion(emotions) {
        return Object.keys(emotions).reduce((a, b) => 
            emotions[a] > emotions[b] ? a : b
        );
    }

    getStressLevelText(stressLevel) {
        if (stressLevel < 0.3) return 'Low';
        if (stressLevel < 0.6) return 'Moderate';
        if (stressLevel < 0.8) return 'High';
        return 'Very High';
    }

    getEngagementLevelText(engagementLevel) {
        if (engagementLevel < 0.3) return 'Low';
        if (engagementLevel < 0.7) return 'Moderate';
        return 'High';
    }

    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }

    updateProgressBar(id, percentage) {
        const element = document.getElementById(id);
        if (element) {
            element.style.width = `${percentage}%`;
        }
    }

    updateEmotionIndicator(emotion) {
        const indicator = document.getElementById('emotionIndicator');
        if (indicator) {
            const emotionColors = {
                'happy': '#28a745',
                'sad': '#6c757d',
                'angry': '#dc3545',
                'fearful': '#ffc107',
                'surprised': '#17a2b8',
                'disgusted': '#6f42c1',
                'neutral': '#007bff'
            };
            indicator.style.backgroundColor = emotionColors[emotion] || '#007bff';
        }
    }

    updateBiometricStatus(id, value) {
        const element = document.getElementById(id);
        if (element) {
            let statusClass = 'status-normal';
            
            if (id === 'hrStatus' && value) {
                if (value > 100) statusClass = 'status-high';
                else if (value > 85) statusClass = 'status-elevated';
            } else if (id === 'stressStatus' && value) {
                if (value > 0.7) statusClass = 'status-high';
                else if (value > 0.5) statusClass = 'status-elevated';
            }
            
            element.className = `biometric-indicator ${statusClass}`;
        }
    }

    showMicroexpressionAlert(microexpressions) {
        const alert = document.getElementById('microAlert');
        const text = document.getElementById('microText');
        
        if (alert && text) {
            const expressions = Object.keys(microexpressions);
            text.textContent = `Detected: ${expressions.join(', ')}`;
            alert.classList.add('show');
            
            setTimeout(() => {
                alert.classList.remove('show');
            }, 3000);
        }
    }

    updateRecommendations(recommendations) {
        const list = document.getElementById('recommendationsList');
        if (list && recommendations.length > 0) {
            list.innerHTML = recommendations.map(rec => 
                `<li><i class="fas fa-lightbulb text-warning me-2"></i>${rec}</li>`
            ).join('');
        }
    }

    showBiometricAlerts(alerts) {
        alerts.forEach(alert => {
            this.showNotification(alert.message, alert.level);
        });
    }

    handleHealthAlerts(alerts) {
        const criticalAlerts = alerts.filter(alert => alert.level === 'critical');
        
        if (criticalAlerts.length > 0) {
            // Show critical alert modal or notification
            this.showCriticalAlert(criticalAlerts);
        }
    }

    showCriticalAlert(alerts) {
        const alertText = alerts.map(alert => alert.message).join('\n');
        alert(`CRITICAL HEALTH ALERT:\n\n${alertText}\n\nPlease seek immediate medical attention if needed.`);
    }

    showNotification(message, level = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast show position-fixed top-0 end-0 m-3`;
        toast.innerHTML = `
            <div class="toast-body bg-${level} text-white">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 5000);
    }

    // Callback management
    onVideoAnalysis(callback) {
        this.addCallback('video_analysis', callback);
    }

    onBiometricAnalysis(callback) {
        this.addCallback('biometric_analysis', callback);
    }

    onTextAnalysis(callback) {
        this.addCallback('text_analysis', callback);
    }

    onAnalysisComplete(callback) {
        this.addCallback('analysis_complete', callback);
    }

    addCallback(event, callback) {
        if (!this.callbacks.has(event)) {
            this.callbacks.set(event, []);
        }
        this.callbacks.get(event).push(callback);
    }

    triggerCallbacks(event, data) {
        if (this.callbacks.has(event)) {
            this.callbacks.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in ${event} callback:`, error);
                }
            });
        }
    }

    // Data storage
    storeAnalysisData(type, data) {
        const storageKey = `mindmend_${type}_analysis`;
        let storedData = JSON.parse(localStorage.getItem(storageKey) || '[]');
        
        storedData.push({
            ...data,
            stored_at: new Date().toISOString()
        });
        
        // Keep only last 100 entries
        if (storedData.length > 100) {
            storedData = storedData.slice(-100);
        }
        
        localStorage.setItem(storageKey, JSON.stringify(storedData));
    }

    getStoredAnalysisData(type, limit = 50) {
        const storageKey = `mindmend_${type}_analysis`;
        const data = JSON.parse(localStorage.getItem(storageKey) || '[]');
        return data.slice(-limit);
    }

    clearStoredData() {
        ['video', 'biometric', 'text'].forEach(type => {
            localStorage.removeItem(`mindmend_${type}_analysis`);
        });
    }

    // Status check
    isConnected() {
        return this.isConnected;
    }

    getConnectionStatus() {
        return {
            connected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            queueLength: this.analysisQueue.length
        };
    }
}

// Initialize global analyzer instance
window.realTimeAnalyzer = new RealTimeAnalyzer();

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.realTimeAnalyzer.initialize();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { RealTimeAnalyzer };
}
