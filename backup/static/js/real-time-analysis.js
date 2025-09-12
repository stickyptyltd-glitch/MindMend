// Real-time Analysis Module for Mind Mend
class RealTimeAnalyzer {
    constructor() {
        this.analysisQueue = [];
        this.isProcessing = false;
        this.emotionHistory = [];
        this.stressHistory = [];
        this.microexpressionBuffer = [];
    }

    async queueAnalysis(frameData, metadata = {}) {
        this.analysisQueue.push({
            frame: frameData,
            metadata: metadata,
            timestamp: Date.now()
        });
        
        if (!this.isProcessing) {
            this.processQueue();
        }
    }

    async processQueue() {
        if (this.analysisQueue.length === 0) {
            this.isProcessing = false;
            return;
        }
        
        this.isProcessing = true;
        const item = this.analysisQueue.shift();
        
        try {
            const result = await this.analyzeFrame(item.frame, item.metadata);
            this.updateHistories(result);
            
            // Continue processing
            setTimeout(() => this.processQueue(), 100);
            
            return result;
        } catch (error) {
            console.error('Analysis error:', error);
            setTimeout(() => this.processQueue(), 500);
        }
    }

    async analyzeFrame(frameData, metadata) {
        // Send to server for analysis
        const response = await fetch('/api/video-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                frame_data: frameData,
                ...metadata
            })
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        return await response.json();
    }

    updateHistories(result) {
        // Update emotion history
        if (result.emotions) {
            this.emotionHistory.push({
                timestamp: Date.now(),
                emotions: result.emotions
            });
            
            // Keep only last 60 seconds of data
            const cutoff = Date.now() - 60000;
            this.emotionHistory = this.emotionHistory.filter(item => item.timestamp > cutoff);
        }
        
        // Update stress history
        if (result.stress_level !== undefined) {
            this.stressHistory.push({
                timestamp: Date.now(),
                level: result.stress_level
            });
            
            // Keep only last 60 seconds
            const cutoff = Date.now() - 60000;
            this.stressHistory = this.stressHistory.filter(item => item.timestamp > cutoff);
        }
        
        // Buffer microexpressions
        if (result.microexpressions) {
            this.microexpressionBuffer.push({
                timestamp: Date.now(),
                expressions: result.microexpressions
            });
            
            // Keep only last 10 seconds
            const cutoff = Date.now() - 10000;
            this.microexpressionBuffer = this.microexpressionBuffer.filter(item => item.timestamp > cutoff);
        }
    }

    getEmotionTrends() {
        if (this.emotionHistory.length < 2) return null;
        
        const emotions = {};
        const counts = {};
        
        // Aggregate emotions over time
        this.emotionHistory.forEach(item => {
            Object.entries(item.emotions).forEach(([emotion, score]) => {
                if (!emotions[emotion]) {
                    emotions[emotion] = 0;
                    counts[emotion] = 0;
                }
                emotions[emotion] += score;
                counts[emotion]++;
            });
        });
        
        // Calculate averages
        const trends = {};
        Object.keys(emotions).forEach(emotion => {
            trends[emotion] = emotions[emotion] / counts[emotion];
        });
        
        return trends;
    }

    getStressTrend() {
        if (this.stressHistory.length < 2) return null;
        
        const recent = this.stressHistory.slice(-10);
        const average = recent.reduce((sum, item) => sum + item.level, 0) / recent.length;
        
        // Calculate trend direction
        const firstHalf = recent.slice(0, Math.floor(recent.length / 2));
        const secondHalf = recent.slice(Math.floor(recent.length / 2));
        
        const firstAvg = firstHalf.reduce((sum, item) => sum + item.level, 0) / firstHalf.length;
        const secondAvg = secondHalf.reduce((sum, item) => sum + item.level, 0) / secondHalf.length;
        
        return {
            current: average,
            trend: secondAvg > firstAvg ? 'increasing' : secondAvg < firstAvg ? 'decreasing' : 'stable',
            change: secondAvg - firstAvg
        };
    }

    getMicroexpressionSummary() {
        if (this.microexpressionBuffer.length === 0) return null;
        
        const summary = {};
        
        this.microexpressionBuffer.forEach(item => {
            Object.entries(item.expressions).forEach(([expression, data]) => {
                if (!summary[expression]) {
                    summary[expression] = {
                        count: 0,
                        totalDuration: 0,
                        avgIntensity: 0
                    };
                }
                
                summary[expression].count++;
                summary[expression].totalDuration += data.duration || 0;
                summary[expression].avgIntensity += data.intensity || 0;
            });
        });
        
        // Calculate averages
        Object.keys(summary).forEach(expression => {
            summary[expression].avgIntensity /= summary[expression].count;
        });
        
        return summary;
    }
}

// Export for use in other modules
window.RealTimeAnalyzer = RealTimeAnalyzer;