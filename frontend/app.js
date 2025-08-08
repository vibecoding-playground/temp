/**
 * MeetingMind - Main JavaScript Application
 * Handles UI interactions, WebSocket communication, and speech recognition
 * 
 * Author: Claude
 * Date: 2025-01-08
 */

class MeetingMind {
    constructor() {
        // Application state
        this.currentMeeting = null;
        this.websocket = null;
        this.isRecording = false;
        this.speechRecognition = null;
        this.meetingStartTime = null;
        this.timerInterval = null;
        
        // Settings
        this.settings = {
            speechLanguage: 'ko-KR',
            autoAnalysis: true,
            notificationSound: true
        };
        
        // Cache DOM elements
        this.elements = {};
        
        // Initialize app
        this.init();
    }
    
    init() {
        this.cacheElements();
        this.setupEventListeners();
        this.loadSettings();
        this.initSpeechRecognition();
        
        console.log('MeetingMind initialized');
    }
    
    cacheElements() {
        this.elements = {
            // Screens
            welcomeScreen: document.getElementById('welcome-screen'),
            meetingInterface: document.getElementById('meeting-interface'),
            loadingOverlay: document.getElementById('loading-overlay'),
            loadingText: document.getElementById('loading-text'),
            
            // Meeting form
            meetingForm: document.getElementById('meeting-form'),
            meetingTitle: document.getElementById('meeting-title'),
            participants: document.getElementById('participants'),
            duration: document.getElementById('duration'),
            
            // Meeting interface
            currentMeetingTitle: document.getElementById('current-meeting-title'),
            meetingTimer: document.getElementById('meeting-timer'),
            participantCount: document.getElementById('participant-count'),
            connectionStatus: document.getElementById('connection-status'),
            
            // Controls
            toggleRecording: document.getElementById('toggle-recording'),
            recordingIcon: document.getElementById('recording-icon'),
            recordingText: document.getElementById('recording-text'),
            endMeeting: document.getElementById('end-meeting'),
            
            // Transcript
            transcriptDisplay: document.getElementById('transcript-display'),
            voiceStatus: document.getElementById('voice-status'),
            clearTranscript: document.getElementById('clear-transcript'),
            
            // Manual input
            textInputForm: document.getElementById('text-input-form'),
            speakerSelect: document.getElementById('speaker-select'),
            manualText: document.getElementById('manual-text'),
            
            // Right panel
            tabButtons: document.querySelectorAll('.tab-button'),
            tabContents: document.querySelectorAll('.tab-content'),
            insightsList: document.getElementById('insights-list'),
            actionsList: document.getElementById('actions-list'),
            summaryContent: document.getElementById('summary-content'),
            
            // Toast container
            toastContainer: document.getElementById('toast-container'),
            
            // Settings
            settingsBtn: document.getElementById('settings-btn'),
            settingsModal: document.getElementById('settings-modal')
        };
    }
    
    setupEventListeners() {
        // Meeting form
        this.elements.meetingForm.addEventListener('submit', (e) => this.handleMeetingStart(e));
        
        // Meeting controls
        this.elements.toggleRecording.addEventListener('click', () => this.toggleRecording());
        this.elements.endMeeting.addEventListener('click', () => this.endMeeting());
        this.elements.clearTranscript.addEventListener('click', () => this.clearTranscript());
        
        // Manual text input
        this.elements.textInputForm.addEventListener('submit', (e) => this.handleManualTextInput(e));
        
        // Tab switching
        this.elements.tabButtons.forEach(button => {
            button.addEventListener('click', () => this.switchTab(button.dataset.tab));
        });
        
        // Settings
        this.elements.settingsBtn.addEventListener('click', () => this.openSettings());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
        
        // Window events
        window.addEventListener('beforeunload', () => {
            if (this.websocket) {
                this.websocket.close();
            }
        });
    }
    
    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.speechRecognition = new SpeechRecognition();
            
            this.speechRecognition.continuous = true;
            this.speechRecognition.interimResults = true;
            this.speechRecognition.lang = this.settings.speechLanguage;
            
            this.speechRecognition.onstart = () => {
                console.log('Speech recognition started');
                this.showVoiceStatus(true);
            };
            
            this.speechRecognition.onresult = (event) => {
                this.handleSpeechResult(event);
            };
            
            this.speechRecognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.showToast('음성 인식 오류: ' + event.error, 'error');
                this.stopRecording();
            };
            
            this.speechRecognition.onend = () => {
                console.log('Speech recognition ended');
                this.showVoiceStatus(false);
                if (this.isRecording) {
                    // Restart if we're still supposed to be recording
                    setTimeout(() => this.speechRecognition.start(), 100);
                }
            };
        } else {
            console.warn('Speech recognition not supported');
            this.showToast('이 브라우저는 음성 인식을 지원하지 않습니다', 'error');
        }
    }
    
    async handleMeetingStart(event) {
        event.preventDefault();
        
        const formData = new FormData(this.elements.meetingForm);
        const participants = formData.get('participants')
            .split(',')
            .map(p => p.trim())
            .filter(p => p.length > 0);
        
        const meetingData = {
            title: formData.get('title'),
            participants: participants,
            duration_estimate: parseInt(formData.get('duration'))
        };
        
        try {
            this.showLoading('회의를 생성하는 중...');
            
            const response = await fetch('/api/meetings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(meetingData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            this.currentMeeting = {
                id: result.meeting_id,
                title: meetingData.title,
                participants: participants
            };
            
            this.hideLoading();
            this.showMeetingInterface();
            await this.connectWebSocket(result.meeting_id);
            
        } catch (error) {
            console.error('Failed to create meeting:', error);
            this.hideLoading();
            this.showToast('회의 생성에 실패했습니다: ' + error.message, 'error');
        }
    }
    
    async connectWebSocket(meetingId) {
        try {
            const wsUrl = `ws://localhost:8000/ws/${meetingId}`;
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.updateConnectionStatus(true);
                this.showToast('회의에 연결되었습니다', 'success');
                this.startMeetingTimer();
            };
            
            this.websocket.onmessage = (event) => {
                this.handleWebSocketMessage(JSON.parse(event.data));
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
                this.showToast('연결 오류가 발생했습니다', 'error');
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateConnectionStatus(false);
                if (this.currentMeeting) {
                    this.showToast('연결이 끊어졌습니다. 재연결을 시도하세요', 'error');
                }
            };
            
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.showToast('WebSocket 연결에 실패했습니다', 'error');
        }
    }
    
    handleWebSocketMessage(message) {
        console.log('WebSocket message received:', message);
        
        switch (message.type) {
            case 'connection_established':
                this.handleConnectionEstablished(message.data);
                break;
                
            case 'text_received':
                this.addToTranscript(message.data.text, message.data.speaker, message.data.timestamp);
                break;
                
            case 'analysis_result':
                this.handleAnalysisResult(message.data);
                break;
                
            case 'real_time_insight':
                this.addInsight(message.data.analysis);
                break;
                
            case 'action_item_detected':
                this.handleActionItemDetected(message.data);
                break;
                
            case 'participant_joined':
                this.updateParticipantCount(message.data.participant_count);
                break;
                
            case 'error':
                this.showToast('서버 오류: ' + message.data.message, 'error');
                break;
                
            default:
                console.log('Unknown message type:', message.type);
        }
    }
    
    sendWebSocketMessage(type, data) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: type,
                data: data,
                timestamp: new Date().toISOString()
            }));
        } else {
            console.error('WebSocket not connected');
            this.showToast('연결이 끊어져 메시지를 보낼 수 없습니다', 'error');
        }
    }
    
    toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }
    
    startRecording() {
        if (!this.speechRecognition) {
            this.showToast('음성 인식이 지원되지 않습니다', 'error');
            return;
        }
        
        try {
            this.speechRecognition.start();
            this.isRecording = true;
            this.updateRecordingUI(true);
            this.sendWebSocketMessage('start_recording', {});
            
        } catch (error) {
            console.error('Failed to start recording:', error);
            this.showToast('음성 인식을 시작할 수 없습니다', 'error');
        }
    }
    
    stopRecording() {
        if (this.speechRecognition) {
            this.speechRecognition.stop();
        }
        
        this.isRecording = false;
        this.updateRecordingUI(false);
        this.showVoiceStatus(false);
        this.sendWebSocketMessage('stop_recording', {});
    }
    
    handleSpeechResult(event) {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        
        if (finalTranscript) {
            const speaker = this.getCurrentSpeaker();
            this.sendWebSocketMessage('text_input', {
                text: finalTranscript,
                speaker: speaker,
                timestamp: new Date().toISOString()
            });
        }
    }
    
    handleManualTextInput(event) {
        event.preventDefault();
        
        const text = this.elements.manualText.value.trim();
        const speaker = this.elements.speakerSelect.value || '알 수 없음';
        
        if (text) {
            this.sendWebSocketMessage('text_input', {
                text: text,
                speaker: speaker,
                timestamp: new Date().toISOString()
            });
            
            this.elements.manualText.value = '';
        }
    }
    
    addToTranscript(text, speaker, timestamp) {
        const transcriptEntry = document.createElement('div');
        transcriptEntry.className = 'transcript-entry';
        
        const time = timestamp ? new Date(timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
        
        transcriptEntry.innerHTML = `
            <div class="transcript-speaker">${speaker}</div>
            <div class="transcript-text">${text}</div>
            <div class="transcript-time">${time}</div>
        `;
        
        // Remove placeholder if exists
        const placeholder = this.elements.transcriptDisplay.querySelector('.transcript-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        this.elements.transcriptDisplay.appendChild(transcriptEntry);
        this.elements.transcriptDisplay.scrollTop = this.elements.transcriptDisplay.scrollHeight;
    }
    
    handleAnalysisResult(data) {
        const analysis = data.analysis;
        
        // Add insights
        if (analysis.insights && analysis.insights.length > 0) {
            analysis.insights.forEach(insight => {
                this.addInsight({
                    ...insight,
                    speaker: data.speaker,
                    original_text: data.original_text
                });
            });
        }
        
        // Add action items
        if (analysis.action_items && analysis.action_items.length > 0) {
            analysis.action_items.forEach(actionItem => {
                this.addActionItem({
                    ...actionItem,
                    speaker: data.speaker
                });
            });
        }
        
        // Update summary if available
        if (analysis.summary) {
            this.updateSummary(analysis);
        }
    }
    
    addInsight(insight) {
        const insightElement = document.createElement('div');
        insightElement.className = 'insight-item';
        
        const confidence = Math.round((insight.confidence || 0) * 100);
        
        insightElement.innerHTML = `
            <div class="insight-header">
                <span class="insight-type ${insight.type}">${this.getInsightTypeText(insight.type)}</span>
                <span class="insight-confidence">${confidence}%</span>
            </div>
            <div class="insight-content">${insight.content}</div>
            ${insight.speaker ? `<div class="insight-speaker">발언자: ${insight.speaker}</div>` : ''}
        `;
        
        // Remove placeholder if exists
        const placeholder = this.elements.insightsList.querySelector('.insights-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        this.elements.insightsList.insertBefore(insightElement, this.elements.insightsList.firstChild);
        
        // Auto-switch to insights tab if not active
        if (!document.querySelector('[data-tab="insights"]').classList.contains('active')) {
            this.switchTab('insights');
        }
    }
    
    addActionItem(actionItem) {
        const actionElement = document.createElement('div');
        actionElement.className = 'action-item';
        
        const confidence = Math.round((actionItem.confidence || 0) * 100);
        
        actionElement.innerHTML = `
            <div class="action-header">
                <span class="action-priority ${actionItem.priority || 'medium'}">${actionItem.priority || 'MEDIUM'}</span>
            </div>
            <div class="action-description">${actionItem.description}</div>
            <div class="action-meta">
                <span>담당자: ${actionItem.assignee || '미정'}</span>
                <span>기한: ${actionItem.due_date || '미정'}</span>
                <span>신뢰도: ${confidence}%</span>
            </div>
        `;
        
        // Remove placeholder if exists
        const placeholder = this.elements.actionsList.querySelector('.actions-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        this.elements.actionsList.appendChild(actionElement);
        
        // Show notification
        this.showToast(`새 액션 아이템: ${actionItem.description}`, 'info');
    }
    
    updateSummary(analysis) {
        const summaryHTML = `
            <div class="summary-section">
                <h4>실시간 요약</h4>
                <p>${analysis.summary}</p>
            </div>
            <div class="summary-section">
                <h4>주요 포인트</h4>
                <ul>
                    ${(analysis.key_points || []).map(point => `<li>${point}</li>`).join('')}
                </ul>
            </div>
            <div class="summary-section">
                <h4>감정 분석</h4>
                <p>전체 분위기: ${this.getSentimentText(analysis.sentiment)}</p>
                <p>긴급도: ${this.getUrgencyText(analysis.urgency_level)}</p>
            </div>
        `;
        
        // Remove placeholder if exists
        const placeholder = this.elements.summaryContent.querySelector('.summary-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        this.elements.summaryContent.innerHTML = summaryHTML;
    }
    
    // UI Helper Methods
    showMeetingInterface() {
        this.elements.welcomeScreen.style.display = 'none';
        this.elements.meetingInterface.style.display = 'block';
        
        // Update meeting info
        this.elements.currentMeetingTitle.textContent = this.currentMeeting.title;
        this.updateParticipantCount(this.currentMeeting.participants.length);
        
        // Populate speaker select
        this.elements.speakerSelect.innerHTML = '<option value="">발언자 선택</option>';
        this.currentMeeting.participants.forEach(participant => {
            const option = document.createElement('option');
            option.value = participant;
            option.textContent = participant;
            this.elements.speakerSelect.appendChild(option);
        });
    }
    
    showLoading(text = '로딩 중...') {
        this.elements.loadingText.textContent = text;
        this.elements.loadingOverlay.style.display = 'flex';
    }
    
    hideLoading() {
        this.elements.loadingOverlay.style.display = 'none';
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        this.elements.toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);
        
        // Play notification sound if enabled
        if (this.settings.notificationSound && type === 'info') {
            this.playNotificationSound();
        }
    }
    
    switchTab(tabName) {
        // Update tab buttons
        this.elements.tabButtons.forEach(button => {
            button.classList.toggle('active', button.dataset.tab === tabName);
        });
        
        // Update tab contents
        this.elements.tabContents.forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        });
    }
    
    updateConnectionStatus(isConnected) {
        this.elements.connectionStatus.textContent = isConnected ? '연결됨' : '연결 끊김';
        this.elements.connectionStatus.className = `connection-status ${isConnected ? 'connected' : 'disconnected'}`;
    }
    
    updateRecordingUI(isRecording) {
        this.elements.recordingIcon.textContent = isRecording ? '⏹️' : '🎤';
        this.elements.recordingText.textContent = isRecording ? '음성 인식 중지' : '음성 인식 시작';
        this.elements.toggleRecording.classList.toggle('btn-danger', isRecording);
        this.elements.toggleRecording.classList.toggle('btn-primary', !isRecording);
    }
    
    showVoiceStatus(show) {
        this.elements.voiceStatus.style.display = show ? 'flex' : 'none';
    }
    
    startMeetingTimer() {
        this.meetingStartTime = Date.now();
        this.timerInterval = setInterval(() => {
            const elapsed = Date.now() - this.meetingStartTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            this.elements.meetingTimer.textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }
    
    updateParticipantCount(count) {
        this.elements.participantCount.textContent = `참석자 ${count}명`;
    }
    
    clearTranscript() {
        this.elements.transcriptDisplay.innerHTML = 
            '<div class="transcript-placeholder">대화 내용이 지워졌습니다.</div>';
    }
    
    endMeeting() {
        if (confirm('정말 회의를 종료하시겠습니까?')) {
            this.stopRecording();
            if (this.websocket) {
                this.websocket.close();
            }
            if (this.timerInterval) {
                clearInterval(this.timerInterval);
            }
            
            // Reset state
            this.currentMeeting = null;
            this.websocket = null;
            
            // Show welcome screen
            this.elements.meetingInterface.style.display = 'none';
            this.elements.welcomeScreen.style.display = 'block';
            
            this.showToast('회의가 종료되었습니다', 'success');
        }
    }
    
    // Utility Methods
    getCurrentSpeaker() {
        const selectedSpeaker = this.elements.speakerSelect.value;
        if (selectedSpeaker) {
            return selectedSpeaker;
        }
        
        // Try to determine speaker from participants
        if (this.currentMeeting && this.currentMeeting.participants.length > 0) {
            return this.currentMeeting.participants[0];
        }
        
        return '알 수 없음';
    }
    
    getInsightTypeText(type) {
        const typeMap = {
            'key_point': '핵심 포인트',
            'decision': '의사결정',
            'action_item': '액션 아이템',
            'question': '질문',
            'concern': '우려사항'
        };
        return typeMap[type] || type;
    }
    
    getSentimentText(sentiment) {
        const sentimentMap = {
            'positive': '긍정적',
            'neutral': '중립적',
            'negative': '부정적'
        };
        return sentimentMap[sentiment] || sentiment;
    }
    
    getUrgencyText(urgency) {
        const urgencyMap = {
            'high': '높음',
            'medium': '보통',
            'low': '낮음'
        };
        return urgencyMap[urgency] || urgency;
    }
    
    handleKeyboardShortcuts(event) {
        // Ctrl/Cmd + R: Toggle recording
        if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
            event.preventDefault();
            if (this.currentMeeting) {
                this.toggleRecording();
            }
        }
        
        // Ctrl/Cmd + E: End meeting
        if ((event.ctrlKey || event.metaKey) && event.key === 'e') {
            event.preventDefault();
            if (this.currentMeeting) {
                this.endMeeting();
            }
        }
        
        // Escape: Close modals
        if (event.key === 'Escape') {
            const modal = document.querySelector('.modal[style*="block"]');
            if (modal) {
                modal.style.display = 'none';
            }
        }
    }
    
    handleConnectionEstablished(data) {
        this.showToast(data.message || '연결되었습니다', 'success');
    }
    
    handleActionItemDetected(data) {
        if (data.requires_confirmation) {
            // Show confirmation dialog or add to pending actions
            this.showToast('새로운 액션 아이템이 감지되었습니다', 'info');
        }
        
        this.addActionItem(data.item);
    }
    
    playNotificationSound() {
        // Simple beep sound using Web Audio API
        if (this.settings.notificationSound) {
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
                oscillator.type = 'sine';
                gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
                
                oscillator.start();
                oscillator.stop(audioContext.currentTime + 0.1);
            } catch (error) {
                console.log('Could not play notification sound:', error);
            }
        }
    }
    
    openSettings() {
        document.getElementById('settings-modal').style.display = 'flex';
    }
    
    loadSettings() {
        const savedSettings = localStorage.getItem('meetingmind-settings');
        if (savedSettings) {
            this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
        }
    }
    
    saveSettings() {
        // Get values from settings form
        this.settings.speechLanguage = document.getElementById('speech-language').value;
        this.settings.autoAnalysis = document.getElementById('auto-analysis').checked;
        this.settings.notificationSound = document.getElementById('notification-sound').checked;
        
        // Save to localStorage
        localStorage.setItem('meetingmind-settings', JSON.stringify(this.settings));
        
        // Update speech recognition language
        if (this.speechRecognition) {
            this.speechRecognition.lang = this.settings.speechLanguage;
        }
        
        this.showToast('설정이 저장되었습니다', 'success');
        this.closeSettings();
    }
    
    closeSettings() {
        document.getElementById('settings-modal').style.display = 'none';
    }
}

// Global functions for modal controls
function closeSettings() {
    app.closeSettings();
}

function saveSettings() {
    app.saveSettings();
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MeetingMind();
});

// Add error handling for unhandled errors
window.addEventListener('error', (event) => {
    console.error('Unhandled error:', event.error);
    if (window.app) {
        window.app.showToast('예상치 못한 오류가 발생했습니다', 'error');
    }
});

// Add visibility change handler to pause/resume recognition when tab is hidden
document.addEventListener('visibilitychange', () => {
    if (window.app && window.app.isRecording) {
        if (document.hidden) {
            console.log('Tab hidden, pausing speech recognition');
            window.app.stopRecording();
        }
    }
});