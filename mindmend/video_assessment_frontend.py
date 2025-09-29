#!/usr/bin/env python3

# Video Assessment Frontend Component - to be placed at bottom of therapy pages

video_assessment_frontend = '''
<!-- Video Assessment Panel (placed at bottom of therapy pages) -->
<div id="video-assessment-section" class="mt-5">
    <div class="card border-info">
        <div class="card-header bg-info text-white">
            <h5 class="mb-0">
                <i class="fas fa-video me-2"></i>
                Video Assessment & Microexpression Analysis
            </h5>
        </div>
        <div class="card-body">
            <!-- Assessment Controls -->
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">Assessment Type</label>
                        <select class="form-select" id="assessment-type">
                            <option value="general">General Assessment</option>
                            <option value="anxiety">Anxiety Detection</option>
                            <option value="depression">Depression Screening</option>
                            <option value="stress">Stress Analysis</option>
                            <option value="engagement">Engagement Monitoring</option>
                            <option value="authenticity">Authenticity Check</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">Analysis Settings</label>
                        <div class="d-flex gap-2">
                            <button class="btn btn-outline-info btn-sm" id="start-assessment">
                                <i class="fas fa-play"></i> Start Assessment
                            </button>
                            <button class="btn btn-outline-warning btn-sm" id="pause-assessment" disabled>
                                <i class="fas fa-pause"></i> Pause
                            </button>
                            <button class="btn btn-outline-danger btn-sm" id="stop-assessment" disabled>
                                <i class="fas fa-stop"></i> Stop & Report
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Video Feed and Analysis Display -->
            <div class="row">
                <div class="col-md-6">
                    <div class="card bg-light">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-camera me-2"></i>Video Feed
                            </h6>
                        </div>
                        <div class="card-body text-center">
                            <video id="assessment-video" width="100%" height="240" autoplay muted style="background: #000; border-radius: 8px;">
                                <div class="d-flex align-items-center justify-content-center h-100 text-muted">
                                    <div>
                                        <i class="fas fa-video fa-3x mb-2"></i>
                                        <p>Camera feed will appear here</p>
                                    </div>
                                </div>
                            </video>
                            <canvas id="analysis-overlay" width="320" height="240" style="display: none;"></canvas>

                            <div class="mt-2">
                                <small class="text-muted">
                                    Status: <span id="assessment-status" class="badge bg-secondary">Ready</span> |
                                    Frames: <span id="frames-analyzed">0</span> |
                                    Duration: <span id="assessment-duration">00:00</span>
                                </small>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card bg-light">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-brain me-2"></i>Real-time Analysis
                            </h6>
                        </div>
                        <div class="card-body">
                            <!-- Primary Emotion Display -->
                            <div class="mb-3">
                                <label class="form-label">Primary Emotion</label>
                                <div class="d-flex align-items-center">
                                    <div class="flex-grow-1">
                                        <div class="progress">
                                            <div id="emotion-bar" class="progress-bar bg-success" style="width: 0%"></div>
                                        </div>
                                    </div>
                                    <span id="primary-emotion" class="ms-2 badge bg-success">Neutral</span>
                                </div>
                                <small class="text-muted">Confidence: <span id="emotion-confidence">0%</span></small>
                            </div>

                            <!-- Stress Level -->
                            <div class="mb-3">
                                <label class="form-label">Stress Level</label>
                                <div class="d-flex align-items-center">
                                    <div class="flex-grow-1">
                                        <div class="progress">
                                            <div id="stress-bar" class="progress-bar bg-warning" style="width: 0%"></div>
                                        </div>
                                    </div>
                                    <span id="stress-level" class="ms-2 badge bg-warning">Low</span>
                                </div>
                            </div>

                            <!-- Engagement Score -->
                            <div class="mb-3">
                                <label class="form-label">Engagement</label>
                                <div class="d-flex align-items-center">
                                    <div class="flex-grow-1">
                                        <div class="progress">
                                            <div id="engagement-bar" class="progress-bar bg-info" style="width: 0%"></div>
                                        </div>
                                    </div>
                                    <span id="engagement-level" class="ms-2 badge bg-info">Moderate</span>
                                </div>
                            </div>

                            <!-- Authenticity Score -->
                            <div class="mb-3">
                                <label class="form-label">Authenticity</label>
                                <div class="d-flex align-items-center">
                                    <div class="flex-grow-1">
                                        <div class="progress">
                                            <div id="authenticity-bar" class="progress-bar bg-primary" style="width: 0%"></div>
                                        </div>
                                    </div>
                                    <span id="authenticity-level" class="ms-2 badge bg-primary">Authentic</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Microexpression Events -->
            <div class="row mt-3">
                <div class="col-12">
                    <div class="card bg-light">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-lightning-bolt me-2"></i>
                                Microexpression Events
                                <span id="microexpression-count" class="badge bg-warning ms-2">0</span>
                            </h6>
                        </div>
                        <div class="card-body">
                            <div id="microexpression-log" class="microexpression-log">
                                <div class="text-muted text-center">
                                    <i class="fas fa-search fa-2x mb-2"></i>
                                    <p>Microexpression events will appear here during analysis</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Assessment Summary (shown after completion) -->
            <div id="assessment-summary" class="row mt-3" style="display: none;">
                <div class="col-12">
                    <div class="card border-success">
                        <div class="card-header bg-success text-white">
                            <h6 class="mb-0">
                                <i class="fas fa-chart-bar me-2"></i>Assessment Report
                            </h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Session Summary</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <td>Dominant Emotion:</td>
                                            <td><span id="summary-dominant-emotion" class="badge bg-primary">-</span></td>
                                        </tr>
                                        <tr>
                                            <td>Average Confidence:</td>
                                            <td><span id="summary-confidence">0%</span></td>
                                        </tr>
                                        <tr>
                                            <td>Frames Analyzed:</td>
                                            <td><span id="summary-frames">0</span></td>
                                        </tr>
                                        <tr>
                                            <td>Microexpressions:</td>
                                            <td><span id="summary-microexpressions">0</span></td>
                                        </tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6>Therapeutic Recommendations</h6>
                                    <ul id="recommendations-list" class="list-unstyled">
                                        <!-- Recommendations will be populated here -->
                                    </ul>
                                </div>
                            </div>
                            <div class="mt-3">
                                <button class="btn btn-primary" id="download-report">
                                    <i class="fas fa-download me-2"></i>Download Full Report
                                </button>
                                <button class="btn btn-secondary" id="new-assessment">
                                    <i class="fas fa-plus me-2"></i>New Assessment
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
class VideoAssessmentManager {
    constructor() {
        this.currentSession = null;
        this.video = null;
        this.canvas = null;
        this.ctx = null;
        this.isRecording = false;
        this.analysisInterval = null;
        this.startTime = null;
        this.frameCount = 0;
        this.microexpressionCount = 0;

        this.init();
    }

    init() {
        this.video = document.getElementById('assessment-video');
        this.canvas = document.getElementById('analysis-overlay');
        this.ctx = this.canvas.getContext('2d');

        this.bindEvents();
        this.setupCamera();
    }

    bindEvents() {
        document.getElementById('start-assessment').addEventListener('click', () => {
            this.startAssessment();
        });

        document.getElementById('pause-assessment').addEventListener('click', () => {
            this.pauseAssessment();
        });

        document.getElementById('stop-assessment').addEventListener('click', () => {
            this.stopAssessment();
        });

        document.getElementById('new-assessment').addEventListener('click', () => {
            this.resetAssessment();
        });

        document.getElementById('download-report').addEventListener('click', () => {
            this.downloadReport();
        });
    }

    async setupCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: 640,
                    height: 480,
                    frameRate: 15
                },
                audio: false
            });

            this.video.srcObject = stream;
            this.updateStatus('Camera Ready', 'success');
        } catch (error) {
            console.error('Error accessing camera:', error);
            this.updateStatus('Camera Error', 'danger');
        }
    }

    async startAssessment() {
        const assessmentType = document.getElementById('assessment-type').value;

        try {
            // Start assessment session
            const response = await fetch('/api/video-assessment/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: assessmentType })
            });

            const result = await response.json();

            if (result.success) {
                this.currentSession = result.session_id;
                this.isRecording = true;
                this.startTime = new Date();
                this.frameCount = 0;
                this.microexpressionCount = 0;

                // Update UI
                this.updateStatus('Recording', 'danger');
                document.getElementById('start-assessment').disabled = true;
                document.getElementById('pause-assessment').disabled = false;
                document.getElementById('stop-assessment').disabled = false;

                // Start frame analysis
                this.startFrameAnalysis();
                this.startDurationTimer();

            } else {
                alert('Failed to start assessment');
            }
        } catch (error) {
            console.error('Error starting assessment:', error);
            alert('Failed to start assessment');
        }
    }

    startFrameAnalysis() {
        this.analysisInterval = setInterval(() => {
            if (this.isRecording && this.video.videoWidth > 0) {
                this.captureAndAnalyzeFrame();
            }
        }, 1000); // Analyze one frame per second
    }

    captureAndAnalyzeFrame() {
        if (!this.video.videoWidth || !this.video.videoHeight) return;

        // Draw video frame to canvas
        this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);

        // Convert canvas to base64
        const frameData = this.canvas.toDataURL('image/jpeg', 0.8);

        // Send for analysis
        this.analyzeFrame(frameData);
        this.frameCount++;
        document.getElementById('frames-analyzed').textContent = this.frameCount;
    }

    async analyzeFrame(frameData) {
        try {
            const response = await fetch('/api/video-assessment/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.currentSession,
                    frame_data: frameData,
                    timestamp: new Date().toISOString()
                })
            });

            const result = await response.json();

            if (result.success && result.analysis_results.length > 0) {
                const analysis = result.analysis_results[0];
                this.updateAnalysisDisplay(analysis);

                // Handle microexpressions
                if (analysis.microexpressions.length > 0) {
                    this.handleMicroexpressions(analysis.microexpressions);
                }
            }
        } catch (error) {
            console.error('Error analyzing frame:', error);
        }
    }

    updateAnalysisDisplay(analysis) {
        // Update primary emotion
        const primaryEmotion = analysis.primary_emotion;
        const confidence = Math.round(analysis.emotion_confidence * 100);

        document.getElementById('primary-emotion').textContent =
            primaryEmotion.charAt(0).toUpperCase() + primaryEmotion.slice(1);
        document.getElementById('emotion-confidence').textContent = confidence + '%';
        document.getElementById('emotion-bar').style.width = confidence + '%';

        // Update stress level
        const stressLevel = analysis.stress_level.overall_level;
        const stressPercentage = Math.round(stressLevel * 100);
        const stressClassification = analysis.stress_level.classification;

        document.getElementById('stress-level').textContent =
            stressClassification.charAt(0).toUpperCase() + stressClassification.slice(1);
        document.getElementById('stress-bar').style.width = stressPercentage + '%';

        // Update progress bar color based on stress level
        const stressBar = document.getElementById('stress-bar');
        stressBar.className = 'progress-bar ' +
            (stressLevel > 0.6 ? 'bg-danger' : stressLevel > 0.3 ? 'bg-warning' : 'bg-success');

        // Update engagement
        const engagementScore = analysis.engagement_score.score;
        const engagementPercentage = Math.round(engagementScore * 100);
        const engagementLevel = analysis.engagement_score.level;

        document.getElementById('engagement-level').textContent =
            engagementLevel.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        document.getElementById('engagement-bar').style.width = engagementPercentage + '%';

        // Update authenticity
        const authenticityScore = analysis.authenticity_score.score;
        const authenticityPercentage = Math.round(authenticityScore * 100);
        const authenticityClassification = analysis.authenticity_score.classification;

        document.getElementById('authenticity-level').textContent =
            authenticityClassification.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        document.getElementById('authenticity-bar').style.width = authenticityPercentage + '%';
    }

    handleMicroexpressions(microexpressions) {
        const logContainer = document.getElementById('microexpression-log');

        microexpressions.forEach(micro => {
            this.microexpressionCount++;

            const microEvent = document.createElement('div');
            microEvent.className = 'microexpression-event mb-2 p-2 border-start border-warning';
            microEvent.innerHTML = `
                <div class="d-flex justify-content-between">
                    <strong>${micro.type.replace('_', ' ')}</strong>
                    <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                </div>
                <div class="d-flex justify-content-between">
                    <span>Intensity: ${Math.round(micro.intensity * 100)}%</span>
                    <span>Duration: ${micro.duration_ms}ms</span>
                    <span>Confidence: ${Math.round(micro.confidence * 100)}%</span>
                </div>
            `;

            // Add to top of log
            if (logContainer.children.length === 1 && logContainer.children[0].classList.contains('text-muted')) {
                logContainer.innerHTML = '';
            }
            logContainer.insertBefore(microEvent, logContainer.firstChild);

            // Keep only last 10 events
            while (logContainer.children.length > 10) {
                logContainer.removeChild(logContainer.lastChild);
            }
        });

        document.getElementById('microexpression-count').textContent = this.microexpressionCount;
    }

    pauseAssessment() {
        this.isRecording = false;
        this.updateStatus('Paused', 'warning');
        document.getElementById('pause-assessment').disabled = true;
        document.getElementById('start-assessment').disabled = false;
        document.getElementById('start-assessment').innerHTML = '<i class="fas fa-play"></i> Resume';
    }

    async stopAssessment() {
        this.isRecording = false;
        clearInterval(this.analysisInterval);

        this.updateStatus('Processing...', 'info');

        try {
            // End assessment and get final report
            const response = await fetch('/api/video-assessment/end', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: this.currentSession })
            });

            const report = await response.json();

            if (report.session_id) {
                this.showAssessmentSummary(report);
                this.updateStatus('Completed', 'success');
            }
        } catch (error) {
            console.error('Error ending assessment:', error);
            this.updateStatus('Error', 'danger');
        }

        // Reset buttons
        document.getElementById('start-assessment').disabled = false;
        document.getElementById('pause-assessment').disabled = true;
        document.getElementById('stop-assessment').disabled = true;
        document.getElementById('start-assessment').innerHTML = '<i class="fas fa-play"></i> Start Assessment';
    }

    showAssessmentSummary(report) {
        const summary = report.summary;
        const analysis = report.detailed_analysis;
        const recommendations = report.recommendations;

        // Update summary data
        document.getElementById('summary-dominant-emotion').textContent =
            summary.dominant_emotion.charAt(0).toUpperCase() + summary.dominant_emotion.slice(1);
        document.getElementById('summary-confidence').textContent =
            Math.round(summary.average_confidence * 100) + '%';
        document.getElementById('summary-frames').textContent = summary.frames_analyzed;
        document.getElementById('summary-microexpressions').textContent = summary.microexpression_count;

        // Update recommendations
        const recommendationsList = document.getElementById('recommendations-list');
        recommendationsList.innerHTML = recommendations.map(rec =>
            `<li><i class="fas fa-lightbulb text-warning me-2"></i>${rec}</li>`
        ).join('');

        // Show summary section
        document.getElementById('assessment-summary').style.display = 'block';

        // Store report for download
        this.currentReport = report;
    }

    downloadReport() {
        if (!this.currentReport) return;

        const reportData = {
            ...this.currentReport,
            generated_at: new Date().toISOString(),
            export_format: 'JSON'
        };

        const blob = new Blob([JSON.stringify(reportData, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `video_assessment_${this.currentReport.session_id}.json`;
        a.click();

        URL.revokeObjectURL(url);
    }

    resetAssessment() {
        this.currentSession = null;
        this.frameCount = 0;
        this.microexpressionCount = 0;

        // Reset UI
        document.getElementById('assessment-summary').style.display = 'none';
        document.getElementById('microexpression-log').innerHTML = `
            <div class="text-muted text-center">
                <i class="fas fa-search fa-2x mb-2"></i>
                <p>Microexpression events will appear here during analysis</p>
            </div>
        `;
        document.getElementById('microexpression-count').textContent = '0';
        document.getElementById('frames-analyzed').textContent = '0';
        document.getElementById('assessment-duration').textContent = '00:00';

        // Reset progress bars
        document.getElementById('emotion-bar').style.width = '0%';
        document.getElementById('stress-bar').style.width = '0%';
        document.getElementById('engagement-bar').style.width = '0%';
        document.getElementById('authenticity-bar').style.width = '0%';

        this.updateStatus('Ready', 'secondary');
    }

    updateStatus(status, type) {
        const statusElement = document.getElementById('assessment-status');
        statusElement.textContent = status;
        statusElement.className = `badge bg-${type}`;
    }

    startDurationTimer() {
        setInterval(() => {
            if (this.isRecording && this.startTime) {
                const duration = new Date() - this.startTime;
                const minutes = Math.floor(duration / 60000);
                const seconds = Math.floor((duration % 60000) / 1000);
                document.getElementById('assessment-duration').textContent =
                    `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        }, 1000);
    }
}

// Initialize video assessment when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('assessment-video')) {
        new VideoAssessmentManager();
    }
});
</script>

<style>
.microexpression-log {
    max-height: 200px;
    overflow-y: auto;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 10px;
    background: white;
}

.microexpression-event {
    background: #fff3cd;
    border-radius: 4px;
    font-size: 0.9rem;
}

#assessment-video {
    border: 2px solid #007bff;
    border-radius: 8px;
}

.progress {
    height: 8px;
}

.card-header h6 {
    font-weight: 600;
}

.badge {
    font-size: 0.8em;
}
</style>
'''

print("Video assessment frontend component created:")
print("✅ Real-time video capture and analysis")
print("✅ Microexpression event logging and visualization")
print("✅ Emotion, stress, engagement, and authenticity tracking")
print("✅ Assessment session management")
print("✅ Detailed reporting and recommendations")
print("✅ Downloadable analysis reports")
print("✅ Responsive design for therapy session integration")