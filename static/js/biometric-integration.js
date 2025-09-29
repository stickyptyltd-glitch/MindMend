class BiometricIntegrator {
    constructor() {
        this.connectedDevices = new Map();
        this.isConnected = false;
        this.currentData = {};
        this.dataBuffer = [];
        this.maxBufferSize = 100;
        this.updateInterval = null;
    }

    // Connect to various wearable devices
    async connectDevice(deviceType) {
        try {
            switch (deviceType.toLowerCase()) {
                case 'apple_watch':
                    return await this.connectAppleWatch();
                case 'fitbit':
                    return await this.connectFitbit();
                case 'garmin':
                    return await this.connectGarmin();
                case 'samsung_health':
                    return await this.connectSamsungHealth();
                case 'web_hid':
                    return await this.connectWebHID();
                default:
                    return await this.simulateDevice(deviceType);
            }
        } catch (error) {
            console.error(`Error connecting to ${deviceType}:`, error);
            throw error;
        }
    }

    // Apple Watch connection (requires native app)
    async connectAppleWatch() {
        // In a real implementation, this would use HealthKit integration
        console.log('Connecting to Apple Watch...');
        
        // Mock Apple Watch connection
        this.connectedDevices.set('apple_watch', {
            name: 'Apple Watch',
            type: 'apple_watch',
            features: ['heart_rate', 'hrv', 'blood_oxygen', 'activity', 'sleep'],
            connected: true,
            lastUpdate: new Date()
        });

        this.isConnected = true;
        this.startMockDataStream('apple_watch');
        
        return {
            success: true,
            device: 'Apple Watch',
            features: ['heart_rate', 'hrv', 'blood_oxygen', 'activity', 'sleep']
        };
    }

    // Fitbit connection
    async connectFitbit() {
        console.log('Connecting to Fitbit...');
        
        // Mock Fitbit connection
        this.connectedDevices.set('fitbit', {
            name: 'Fitbit',
            type: 'fitbit',
            features: ['heart_rate', 'steps', 'sleep', 'stress'],
            connected: true,
            lastUpdate: new Date()
        });

        this.isConnected = true;
        this.startMockDataStream('fitbit');
        
        return {
            success: true,
            device: 'Fitbit',
            features: ['heart_rate', 'steps', 'sleep', 'stress']
        };
    }

    // Web HID for compatible devices
    async connectWebHID() {
        if (!navigator.hid) {
            throw new Error('Web HID not supported in this browser');
        }

        try {
            const devices = await navigator.hid.requestDevice({
                filters: [
                    { vendorId: 0x1234 }, // Mock vendor ID
                    { vendorId: 0x5678 }  // Another mock vendor ID
                ]
            });

            if (devices.length > 0) {
                const device = devices[0];
                await device.open();
                
                this.connectedDevices.set('hid_device', {
                    name: device.productName || 'HID Device',
                    type: 'hid',
                    device: device,
                    features: ['heart_rate', 'activity'],
                    connected: true,
                    lastUpdate: new Date()
                });

                this.isConnected = true;
                this.startHIDDataListening(device);
                
                return {
                    success: true,
                    device: device.productName || 'HID Device',
                    features: ['heart_rate', 'activity']
                };
            } else {
                throw new Error('No compatible devices selected');
            }
        } catch (error) {
            console.error('HID connection error:', error);
            throw error;
        }
    }

    // Simulate device for demonstration
    async simulateDevice(deviceType) {
        console.log(`Simulating ${deviceType} device...`);
        
        const features = this.getDeviceFeatures(deviceType);
        
        this.connectedDevices.set('simulated', {
            name: `Simulated ${deviceType}`,
            type: 'simulated',
            features: features,
            connected: true,
            lastUpdate: new Date()
        });

        this.isConnected = true;
        this.startMockDataStream('simulated');
        
        return {
            success: true,
            device: `Simulated ${deviceType}`,
            features: features
        };
    }

    getDeviceFeatures(deviceType) {
        const featureMap = {
            'apple_watch': ['heart_rate', 'hrv', 'blood_oxygen', 'activity', 'sleep', 'stress'],
            'fitbit': ['heart_rate', 'steps', 'sleep', 'stress', 'activity'],
            'garmin': ['heart_rate', 'hrv', 'stress', 'activity', 'recovery'],
            'samsung_health': ['heart_rate', 'stress', 'sleep', 'activity'],
            'polar': ['heart_rate', 'hrv', 'training_load', 'recovery'],
            'default': ['heart_rate', 'activity']
        };
        
        return featureMap[deviceType] || featureMap['default'];
    }

    // Start mock data stream for demonstration
    startMockDataStream(deviceId) {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        this.updateInterval = setInterval(() => {
            const mockData = this.generateMockBiometricData();
            this.updateCurrentData(mockData);
            this.addToBuffer(mockData);
            
            // Emit data update event
            if (window.socket) {
                window.socket.emit('biometric_update', mockData);
            }
        }, 5000); // Update every 5 seconds
    }

    generateMockBiometricData() {
        const time = new Date().getTime();
        
        // Generate realistic mock data with some variation
        const baseHeartRate = 70;
        const heartRateVariation = Math.sin(time / 60000) * 10 + Math.random() * 5;
        
        return {
            timestamp: new Date().toISOString(),
            heart_rate: Math.round(baseHeartRate + heartRateVariation),
            hrv_score: Math.round(30 + Math.random() * 40), // 30-70 range
            stress_level: Math.max(0, Math.min(1, 0.3 + Math.random() * 0.4)), // 0.3-0.7 range
            blood_oxygen: Math.round(95 + Math.random() * 4), // 95-99 range
            activity_level: Math.round(Math.random() * 5000), // 0-5000 steps
            sleep_quality: Math.max(0, Math.min(1, 0.6 + Math.random() * 0.3)), // 0.6-0.9 range
            temperature: 98.6 + (Math.random() - 0.5) * 2, // 97.6-99.6 F
            device_type: Array.from(this.connectedDevices.keys())[0] || 'simulated'
        };
    }

    // HID device data listening
    startHIDDataListening(device) {
        device.addEventListener('inputreport', (event) => {
            try {
                const data = this.parseHIDData(event.data);
                if (data) {
                    this.updateCurrentData(data);
                    this.addToBuffer(data);
                }
            } catch (error) {
                console.error('Error parsing HID data:', error);
            }
        });
    }

    parseHIDData(dataView) {
        // Mock HID data parsing
        // In a real implementation, this would parse actual device data
        return {
            timestamp: new Date().toISOString(),
            heart_rate: dataView.getUint8(0) + 60, // Mock heart rate parsing
            activity_level: dataView.getUint16(1), // Mock activity parsing
            device_type: 'hid'
        };
    }

    updateCurrentData(data) {
        this.currentData = { ...this.currentData, ...data };
    }

    addToBuffer(data) {
        this.dataBuffer.push(data);
        if (this.dataBuffer.length > this.maxBufferSize) {
            this.dataBuffer.shift();
        }
    }

    getCurrentData() {
        return this.currentData;
    }

    getHistoricalData(minutes = 60) {
        const cutoffTime = new Date(Date.now() - minutes * 60 * 1000);
        return this.dataBuffer.filter(data => 
            new Date(data.timestamp) > cutoffTime
        );
    }

    // Analyze current biometric state
    analyzeCurrentState() {
        if (!this.currentData.heart_rate) {
            return { status: 'no_data', message: 'No biometric data available' };
        }

        const analysis = {
            status: 'normal',
            alerts: [],
            recommendations: [],
            scores: {}
        };

        // Heart rate analysis
        const hr = this.currentData.heart_rate;
        if (hr > 100) {
            analysis.alerts.push('Elevated heart rate detected');
            analysis.status = 'elevated';
        } else if (hr < 50) {
            analysis.alerts.push('Low heart rate detected');
        }

        // Stress level analysis
        const stress = this.currentData.stress_level;
        if (stress > 0.7) {
            analysis.alerts.push('High stress level detected');
            analysis.recommendations.push('Consider taking a break and practicing deep breathing');
            analysis.status = 'stressed';
        }

        // HRV analysis
        const hrv = this.currentData.hrv_score;
        if (hrv < 20) {
            analysis.alerts.push('Low heart rate variability - may indicate fatigue');
            analysis.recommendations.push('Focus on stress management and recovery');
        }

        // Blood oxygen analysis
        const spo2 = this.currentData.blood_oxygen;
        if (spo2 < 95) {
            analysis.alerts.push('Low blood oxygen detected');
            analysis.status = 'concerning';
        }

        // Calculate overall wellness score
        analysis.scores.wellness = this.calculateWellnessScore();
        analysis.scores.stress = stress || 0;
        analysis.scores.recovery = (hrv || 50) / 70; // Normalize HRV to 0-1 scale

        return analysis;
    }

    calculateWellnessScore() {
        const data = this.currentData;
        let score = 0.5; // Base score

        // Heart rate contribution
        if (data.heart_rate) {
            if (data.heart_rate >= 60 && data.heart_rate <= 80) score += 0.2;
            else if (data.heart_rate >= 50 && data.heart_rate <= 100) score += 0.1;
        }

        // Stress level contribution
        if (data.stress_level !== undefined) {
            score += (1 - data.stress_level) * 0.3;
        }

        // HRV contribution
        if (data.hrv_score) {
            score += Math.min(data.hrv_score / 70, 1) * 0.2;
        }

        // Sleep quality contribution
        if (data.sleep_quality) {
            score += data.sleep_quality * 0.2;
        }

        return Math.max(0, Math.min(1, score));
    }

    // Send data to server
    async sendBiometricData(data = null) {
        const dataToSend = data || this.currentData;
        
        try {
            const response = await fetch('/api/biometric-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dataToSend)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error sending biometric data:', error);
            throw error;
        }
    }

    // Disconnect all devices
    disconnect() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }

        // Close HID devices
        this.connectedDevices.forEach((device, id) => {
            if (device.type === 'hid' && device.device) {
                device.device.close();
            }
        });

        this.connectedDevices.clear();
        this.isConnected = false;
        this.currentData = {};
        
        console.log('All biometric devices disconnected');
    }

    isConnected() {
        return this.isConnected;
    }

    getConnectedDevices() {
        return Array.from(this.connectedDevices.values());
    }
}

// Utility functions for biometric data visualization
class BiometricVisualizer {
    static createHeartRateChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        const labels = data.map(d => new Date(d.timestamp).toLocaleTimeString());
        const heartRateData = data.map(d => d.heart_rate);

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Heart Rate (bpm)',
                    data: heartRateData,
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 50,
                        max: 120
                    }
                }
            }
        });
    }

    static createStressChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        const labels = data.map(d => new Date(d.timestamp).toLocaleTimeString());
        const stressData = data.map(d => (d.stress_level || 0) * 100);

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Stress Level (%)',
                    data: stressData,
                    borderColor: '#ffc107',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { BiometricIntegrator, BiometricVisualizer };
}
