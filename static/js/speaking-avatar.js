/**
 * Speaking Avatar Integration for MindMend Platform
 * Advanced AI-powered speaking avatar with real-time TTS and animations
 */

class SpeakingAvatar {
    constructor() {
        this.personality = 'compassionate';
        this.isActive = false;
        this.currentSpeech = null;
        this.speechQueue = [];
        this.isProcessingQueue = false;
        this.avatarElement = null;
        this.statusElement = null;
        
        // Voice synthesis settings
        this.voiceSettings = {
            rate: 1.0,
            pitch: 0.0,
            volume: 0.8
        };
        
        // Animation states
        this.animationStates = {
            idle: '😊',
            speaking: '😊',
            listening: '👂',
            empathetic: '🤗',
            encouraging: '💪',
            thinking: '🤔',
            concerned: '😟'
        };
        
        this.currentState = 'idle';
        this.init();
    }
    
    init() {
        // Create avatar UI if not exists
        this.createAvatarUI();
        
        // Initialize speech synthesis
        this.initializeSpeechSynthesis();
        
        // Set up event listeners
        this.setupEventListeners();
        
        console.log('🎙️ Speaking Avatar initialized');
    }
    
    createAvatarUI() {
        // Check if avatar already exists
        if (document.getElementById('mindmend-avatar')) {
            this.avatarElement = document.getElementById('mindmend-avatar');
            return;
        }
        
        // Create avatar container
        const avatarContainer = document.createElement('div');
        avatarContainer.id = 'mindmend-avatar-container';
        avatarContainer.className = 'mindmend-avatar-container';
        avatarContainer.innerHTML = `
            <div class="avatar-visual" id="mindmend-avatar">
                <div class="avatar-face" id="avatar-face">${this.animationStates.idle}</div>
                <div class="avatar-status" id="avatar-status">Ready</div>
                <div class="avatar-controls">
                    <button class="avatar-btn" id="avatar-toggle" title="Toggle Avatar">
                        <span class="btn-icon">🎙️</span>
                    </button>
                    <button class="avatar-btn" id="avatar-settings" title="Avatar Settings">
                        <span class="btn-icon">⚙️</span>
                    </button>
                </div>
            </div>
            <div class="avatar-speech-bubble" id="avatar-speech" style="display: none;">
                <div class="speech-content" id="speech-content"></div>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(avatarContainer);
        
        this.avatarElement = document.getElementById('mindmend-avatar');
        this.statusElement = document.getElementById('avatar-status');
        
        // Add CSS styles
        this.injectStyles();
    }
    
    injectStyles() {
        const styles = `
            <style id="avatar-styles">
                .mindmend-avatar-container {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 1000;
                    font-family: system-ui, -apple-system, sans-serif;
                }
                
                .avatar-visual {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 20px;
                    padding: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    text-align: center;
                    color: white;
                    min-width: 120px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.2);
                }
                
                .avatar-face {
                    font-size: 48px;
                    margin-bottom: 10px;
                    transition: all 0.3s ease;
                    cursor: pointer;
                }
                
                .avatar-face:hover {
                    transform: scale(1.1);
                }
                
                .avatar-status {
                    font-size: 12px;
                    opacity: 0.8;
                    margin-bottom: 15px;
                    font-weight: 500;
                }
                
                .avatar-controls {
                    display: flex;
                    gap: 8px;
                    justify-content: center;
                }
                
                .avatar-btn {
                    background: rgba(255,255,255,0.2);
                    border: none;
                    border-radius: 8px;
                    padding: 8px;
                    color: white;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    font-size: 14px;
                }
                
                .avatar-btn:hover {
                    background: rgba(255,255,255,0.3);
                    transform: translateY(-2px);
                }
                
                .avatar-speech-bubble {
                    background: white;
                    color: #333;
                    border-radius: 15px;
                    padding: 15px;
                    margin-bottom: 10px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.2);
                    max-width: 300px;
                    position: relative;
                    animation: fadeIn 0.3s ease;
                }
                
                .avatar-speech-bubble::after {
                    content: '';
                    position: absolute;
                    bottom: -10px;
                    right: 30px;
                    width: 0;
                    height: 0;
                    border-left: 10px solid transparent;
                    border-right: 10px solid transparent;
                    border-top: 10px solid white;
                }
                
                .speech-content {
                    font-size: 14px;
                    line-height: 1.4;
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                @keyframes speaking {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                }
                
                .avatar-speaking {
                    animation: speaking 0.8s ease-in-out infinite;
                }
                
                .avatar-minimized {
                    transform: scale(0.8);
                    opacity: 0.7;
                }
                
                .personality-compassionate { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
                .personality-professional { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
                .personality-encouraging { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
                .personality-calming { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
                
                /* Responsive design */
                @media (max-width: 768px) {
                    .mindmend-avatar-container {
                        bottom: 10px;
                        right: 10px;
                        transform: scale(0.9);
                    }
                    
                    .avatar-speech-bubble {
                        max-width: 250px;
                        font-size: 12px;
                    }
                }
            </style>
        `;
        
        if (!document.getElementById('avatar-styles')) {
            document.head.insertAdjacentHTML('beforeend', styles);
        }
    }
    
    setupEventListeners() {
        // Avatar toggle button
        const toggleBtn = document.getElementById('avatar-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }
        
        // Settings button
        const settingsBtn = document.getElementById('avatar-settings');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.showSettings());
        }
        
        // Face click for interaction
        const avatarFace = document.getElementById('avatar-face');
        if (avatarFace) {
            avatarFace.addEventListener('click', () => this.handleFaceClick());
        }
        
        // Listen for chat messages to generate responses
        this.setupChatIntegration();
    }
    
    setupChatIntegration() {
        // Listen for form submissions or button clicks that send messages
        document.addEventListener('DOMContentLoaded', () => {
            // Hook into existing chat functionality
            const chatForm = document.querySelector('form[action*="session"]') || 
                           document.querySelector('form') ||
                           document.querySelector('[onsubmit]');
            
            if (chatForm) {
                chatForm.addEventListener('submit', (e) => {
                    setTimeout(() => this.handleChatMessage(), 500);
                });
            }
            
            // Also listen for any button that might send messages
            document.querySelectorAll('button[type="submit"], .btn-primary').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    if (this.isActive) {
                        setTimeout(() => this.handleChatMessage(), 1000);
                    }
                });
            });
        });
    }
    
    initializeSpeechSynthesis() {
        // Check if speech synthesis is available
        if (!('speechSynthesis' in window)) {
            console.warn('Speech synthesis not supported');
            return;
        }
        
        // Wait for voices to be loaded
        if (speechSynthesis.getVoices().length === 0) {
            speechSynthesis.addEventListener('voiceschanged', () => {
                console.log('🎙️ Speech synthesis voices loaded');
            });
        }
    }
    
    toggle() {
        this.isActive = !this.isActive;
        
        const toggleBtn = document.getElementById('avatar-toggle');
        if (this.isActive) {
            this.activate();
            if (toggleBtn) toggleBtn.innerHTML = '<span class="btn-icon">🔇</span>';
        } else {
            this.deactivate();
            if (toggleBtn) toggleBtn.innerHTML = '<span class="btn-icon">🎙️</span>';
        }
    }
    
    activate() {
        this.isActive = true;
        this.updateStatus('Active');
        this.avatarElement.classList.remove('avatar-minimized');
        
        // Send activation request to backend
        fetch('/api/avatar/personality', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({personality: this.personality})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.speakText(data.greeting);
                this.updatePersonalityStyle();
            }
        })
        .catch(error => console.warn('Avatar activation error:', error));
        
        console.log('🎙️ Avatar activated');
    }
    
    deactivate() {
        this.isActive = false;
        this.stopSpeaking();
        this.updateStatus('Inactive');
        this.avatarElement.classList.add('avatar-minimized');
        
        console.log('🔇 Avatar deactivated');
    }
    
    async handleChatMessage() {
        if (!this.isActive) return;
        
        // Get the latest user message from the chat
        const userMessage = this.getLatestUserMessage();
        if (!userMessage) return;
        
        try {
            this.updateState('thinking');
            this.updateStatus('Generating response...');
            
            const response = await fetch('/api/avatar/speak', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: userMessage,
                    personality: this.personality,
                    session_type: 'individual'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Show speech bubble
                this.showSpeechBubble(data.response_text);
                
                // Update animation based on response type
                this.updateState(data.animation_type || 'speaking');
                
                // Speak the response
                await this.speakText(data.response_text);
                
                this.updateStatus('Ready');
                this.updateState('idle');
            } else {
                console.warn('Avatar speech generation failed:', data.error);
                if (data.fallback_response) {
                    this.speakText(data.fallback_response);
                }
            }
            
        } catch (error) {
            console.error('Error generating avatar response:', error);
            this.updateStatus('Error');
            this.updateState('idle');
        }
    }
    
    getLatestUserMessage() {
        // Try to find the latest user message in various chat formats
        const messageSelectors = [
            '.user-message:last-child',
            '.message.user:last-child',
            'textarea[name*="message"]',
            'input[name*="message"]',
            '.chat-input',
            '#user-message'
        ];
        
        for (const selector of messageSelectors) {
            const element = document.querySelector(selector);
            if (element) {
                return element.textContent || element.value;
            }
        }
        
        return '';
    }
    
    showSpeechBubble(text) {
        const speechBubble = document.getElementById('avatar-speech');
        const speechContent = document.getElementById('speech-content');
        
        if (speechBubble && speechContent) {
            speechContent.textContent = text;
            speechBubble.style.display = 'block';
            
            // Auto-hide after speaking
            setTimeout(() => {
                speechBubble.style.display = 'none';
            }, Math.max(3000, text.length * 100)); // Minimum 3 seconds
        }
    }
    
    async speakText(text) {
        if (!text || !('speechSynthesis' in window)) return;
        
        return new Promise((resolve) => {
            // Stop any current speech
            this.stopSpeaking();
            
            // Create new utterance
            this.currentSpeech = new SpeechSynthesisUtterance(text);
            
            // Apply voice settings
            this.currentSpeech.rate = this.voiceSettings.rate;
            this.currentSpeech.pitch = this.voiceSettings.pitch;
            this.currentSpeech.volume = this.voiceSettings.volume;
            
            // Select appropriate voice
            const voices = speechSynthesis.getVoices();
            const preferredVoice = voices.find(voice => 
                voice.name.includes('Female') || voice.name.includes('Samantha')
            ) || voices[0];
            
            if (preferredVoice) {
                this.currentSpeech.voice = preferredVoice;
            }
            
            // Set up event handlers
            this.currentSpeech.onstart = () => {
                this.updateState('speaking');
                this.updateStatus('Speaking...');
                document.getElementById('avatar-face').classList.add('avatar-speaking');
            };
            
            this.currentSpeech.onend = () => {
                this.updateState('idle');
                this.updateStatus('Ready');
                document.getElementById('avatar-face').classList.remove('avatar-speaking');
                this.currentSpeech = null;
                resolve();
            };
            
            this.currentSpeech.onerror = (error) => {
                console.warn('Speech synthesis error:', error);
                this.updateStatus('Speech Error');
                this.updateState('idle');
                document.getElementById('avatar-face').classList.remove('avatar-speaking');
                this.currentSpeech = null;
                resolve();
            };
            
            // Speak
            speechSynthesis.speak(this.currentSpeech);
        });
    }
    
    stopSpeaking() {
        if (this.currentSpeech) {
            speechSynthesis.cancel();
            this.currentSpeech = null;
            document.getElementById('avatar-face').classList.remove('avatar-speaking');
            this.updateState('idle');
            this.updateStatus('Ready');
        }
    }
    
    updateState(newState) {
        this.currentState = newState;
        const faceElement = document.getElementById('avatar-face');
        if (faceElement && this.animationStates[newState]) {
            faceElement.textContent = this.animationStates[newState];
        }
    }
    
    updateStatus(status) {
        if (this.statusElement) {
            this.statusElement.textContent = status;
        }
    }
    
    updatePersonalityStyle() {
        if (this.avatarElement) {
            // Remove existing personality classes
            this.avatarElement.classList.remove('personality-compassionate', 'personality-professional', 'personality-encouraging', 'personality-calming');
            // Add current personality class
            this.avatarElement.classList.add(`personality-${this.personality}`);
        }
    }
    
    setPersonality(personality) {
        const validPersonalities = ['compassionate', 'professional', 'encouraging', 'calming'];
        if (!validPersonalities.includes(personality)) return;
        
        this.personality = personality;
        this.updatePersonalityStyle();
        
        // Update backend
        fetch('/api/avatar/personality', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({personality: personality})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && this.isActive) {
                this.speakText(data.greeting);
            }
        })
        .catch(error => console.warn('Personality change error:', error));
    }
    
    updateVoiceSettings(settings) {
        Object.assign(this.voiceSettings, settings);
        
        // Update backend
        fetch('/api/avatar/settings', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({voice_settings: settings})
        })
        .catch(error => console.warn('Voice settings update error:', error));
    }
    
    handleFaceClick() {
        if (!this.isActive) {
            this.activate();
        } else {
            // Cycle through personalities
            const personalities = ['compassionate', 'professional', 'encouraging', 'calming'];
            const currentIndex = personalities.indexOf(this.personality);
            const nextIndex = (currentIndex + 1) % personalities.length;
            this.setPersonality(personalities[nextIndex]);
        }
    }
    
    showSettings() {
        // Create settings modal
        const settingsModal = document.createElement('div');
        settingsModal.className = 'avatar-settings-modal';
        settingsModal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>🎙️ Avatar Settings</h3>
                    <button class="close-btn" onclick="this.closest('.avatar-settings-modal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="setting-group">
                        <label>Personality:</label>
                        <select id="personality-select" onchange="window.mindmendAvatar.setPersonality(this.value)">
                            <option value="compassionate" ${this.personality === 'compassionate' ? 'selected' : ''}>Compassionate</option>
                            <option value="professional" ${this.personality === 'professional' ? 'selected' : ''}>Professional</option>
                            <option value="encouraging" ${this.personality === 'encouraging' ? 'selected' : ''}>Encouraging</option>
                            <option value="calming" ${this.personality === 'calming' ? 'selected' : ''}>Calming</option>
                        </select>
                    </div>
                    <div class="setting-group">
                        <label>Speech Rate: <span id="rate-value">${this.voiceSettings.rate}</span></label>
                        <input type="range" min="0.5" max="2" step="0.1" value="${this.voiceSettings.rate}" 
                               onchange="window.mindmendAvatar.updateVoiceSettings({rate: parseFloat(this.value)}); document.getElementById('rate-value').textContent = this.value">
                    </div>
                    <div class="setting-group">
                        <label>Pitch: <span id="pitch-value">${this.voiceSettings.pitch}</span></label>
                        <input type="range" min="-1" max="1" step="0.1" value="${this.voiceSettings.pitch}"
                               onchange="window.mindmendAvatar.updateVoiceSettings({pitch: parseFloat(this.value)}); document.getElementById('pitch-value').textContent = this.value">
                    </div>
                    <div class="setting-group">
                        <label>Volume: <span id="volume-value">${this.voiceSettings.volume}</span></label>
                        <input type="range" min="0.1" max="1" step="0.1" value="${this.voiceSettings.volume}"
                               onchange="window.mindmendAvatar.updateVoiceSettings({volume: parseFloat(this.value)}); document.getElementById('volume-value').textContent = this.value">
                    </div>
                    <div class="setting-group">
                        <button onclick="window.mindmendAvatar.speakText('This is a test of the current voice settings.')">Test Voice</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal styles
        const modalStyles = `
            <style>
                .avatar-settings-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    z-index: 10000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .avatar-settings-modal .modal-content {
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    max-width: 400px;
                    width: 90%;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                }
                .avatar-settings-modal .modal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #eee;
                }
                .avatar-settings-modal .close-btn {
                    background: none;
                    border: none;
                    font-size: 24px;
                    cursor: pointer;
                }
                .avatar-settings-modal .setting-group {
                    margin-bottom: 15px;
                }
                .avatar-settings-modal label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                    color: #333;
                }
                .avatar-settings-modal input, .avatar-settings-modal select, .avatar-settings-modal button {
                    width: 100%;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    font-size: 14px;
                }
                .avatar-settings-modal button {
                    background: #667eea;
                    color: white;
                    border: none;
                    cursor: pointer;
                    font-weight: bold;
                }
                .avatar-settings-modal button:hover {
                    background: #5a67d8;
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', modalStyles);
        document.body.appendChild(settingsModal);
    }
    
    // Public API methods
    speak(text) {
        if (this.isActive) {
            this.showSpeechBubble(text);
            return this.speakText(text);
        }
    }
    
    setActive(active) {
        if (active !== this.isActive) {
            this.toggle();
        }
    }
    
    getStatus() {
        return {
            active: this.isActive,
            personality: this.personality,
            currentState: this.currentState,
            speaking: this.currentSpeech !== null,
            voiceSettings: this.voiceSettings
        };
    }
}

// Initialize and expose globally
window.mindmendAvatar = new SpeakingAvatar();

// Auto-activate if user prefers it
if (localStorage.getItem('avatar_auto_active') === 'true') {
    window.mindmendAvatar.setActive(true);
}

console.log('🎙️ MindMend Speaking Avatar loaded successfully');