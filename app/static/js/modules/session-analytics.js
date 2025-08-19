/**
 * Session Analytics Module
 * Handles session history display and detailed analytics
 */

export class SessionAnalytics {
    constructor() {
        this.sessionHistory = [];
        this.historyLimit = 20;
        this.historyDays = 30;
        
        this.init();
    }
    
    async init() {
        console.log('Session Analytics initializing...');
        await this.loadSessionHistory();
        this.bindEvents();
        console.log('Session Analytics initialized');
    }
    
    async loadSessionHistory() {
        try {
            const response = await fetch(`/api/progress/session-history?limit=${this.historyLimit}&days=${this.historyDays}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.sessionHistory = data.session_history || [];
                this.updateSessionHistoryDisplay();
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            console.error('Failed to load session history:', error);
            this.showHistoryError();
        } finally {
            this.hideHistoryLoader();
        }
    }
    
    updateSessionHistoryDisplay() {
        const container = document.getElementById('session-history-container');
        if (!container) return;
        
        if (this.sessionHistory.length === 0) {
            this.showNoHistoryMessage();
            return;
        }
        
        const html = this.sessionHistory.map(session => {
            const sessionDate = new Date(session.datetime);
            const formattedDate = sessionDate.toLocaleDateString();
            const formattedTime = sessionDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            const progressColor = this.getProgressColor(session.progress_percentage);
            
            return `
                <div class="border rounded p-3 mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div>
                            <h6 class="mb-1">${session.movie_title}</h6>
                            <small class="text-muted">
                                <i class="fas fa-language me-1"></i>${session.language_pair}
                            </small>
                        </div>
                        <span class="badge bg-${progressColor}">${session.progress_percentage.toFixed(1)}%</span>
                    </div>
                    
                    <div class="progress mb-2" style="height: 4px;">
                        <div class="progress-bar bg-${progressColor}" 
                             style="width: ${session.progress_percentage}%" 
                             role="progressbar"></div>
                    </div>
                    
                    <div class="row small text-muted">
                        <div class="col-md-3">
                            <i class="fas fa-calendar-alt me-1"></i>${formattedDate}
                        </div>
                        <div class="col-md-3">
                            <i class="fas fa-clock me-1"></i>${formattedTime}
                        </div>
                        <div class="col-md-3">
                            <i class="fas fa-stopwatch me-1"></i>${session.duration_minutes} min
                        </div>
                        <div class="col-md-3">
                            <i class="fas fa-align-left me-1"></i>${session.alignments_studied} alignments
                        </div>
                    </div>
                    
                    <div class="d-flex justify-content-between align-items-center mt-2">
                        <small class="text-muted">
                            Position: ${session.current_position + 1}
                        </small>
                        <a href="/learn/${session.sub_link_id}" class="btn btn-sm btn-outline-primary">
                            ${session.progress_percentage >= 100 ? 'Review' : 'Continue'}
                        </a>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = html;
    }
    
    getProgressColor(percentage) {
        if (percentage >= 100) return 'success';
        if (percentage >= 75) return 'info';
        if (percentage >= 50) return 'warning';
        if (percentage >= 25) return 'secondary';
        return 'light';
    }
    
    showNoHistoryMessage() {
        const container = document.getElementById('session-history-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-history fa-3x text-muted mb-3"></i>
                <h6 class="text-muted">No Session History</h6>
                <p class="text-muted mb-3">Start learning to see your session history here!</p>
                <a href="/movies" class="btn btn-primary btn-sm">Browse Movies</a>
            </div>
        `;
    }
    
    showHistoryError() {
        const container = document.getElementById('session-history-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-exclamation-triangle fa-2x text-warning mb-3"></i>
                <p class="text-muted">Unable to load session history</p>
                <button class="btn btn-outline-primary btn-sm" onclick="window.location.reload()">
                    Try Again
                </button>
            </div>
        `;
    }
    
    hideHistoryLoader() {
        const loader = document.getElementById('history-loader');
        if (loader && loader.parentElement) {
            loader.parentElement.style.display = 'none';
        }
    }
    
    bindEvents() {
        // Refresh history button
        const refreshBtn = document.getElementById('refresh-history');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', async () => {
                refreshBtn.disabled = true;
                const icon = refreshBtn.querySelector('i');
                if (icon) icon.classList.add('fa-spin');
                
                await this.loadSessionHistory();
                
                refreshBtn.disabled = false;
                if (icon) icon.classList.remove('fa-spin');
            });
        }
    }
    
    async refreshHistory() {
        await this.loadSessionHistory();
    }
    
    getSessionSummary() {
        if (this.sessionHistory.length === 0) {
            return {
                totalSessions: 0,
                totalMinutes: 0,
                avgSessionTime: 0,
                totalAlignments: 0
            };
        }
        
        const totalMinutes = this.sessionHistory.reduce((sum, session) => sum + session.duration_minutes, 0);
        const totalAlignments = this.sessionHistory.reduce((sum, session) => sum + session.alignments_studied, 0);
        
        return {
            totalSessions: this.sessionHistory.length,
            totalMinutes: totalMinutes,
            avgSessionTime: totalMinutes / this.sessionHistory.length,
            totalAlignments: totalAlignments
        };
    }
    
    getRecentActivity() {
        if (this.sessionHistory.length === 0) return null;
        
        // Return the most recent session
        return this.sessionHistory[0];
    }
    
    getStudyStreak() {
        if (this.sessionHistory.length === 0) return 0;
        
        // Simple streak calculation based on consecutive days
        const today = new Date().toDateString();
        const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toDateString();
        
        let streak = 0;
        const studiedDates = new Set();
        
        this.sessionHistory.forEach(session => {
            const sessionDate = new Date(session.datetime).toDateString();
            studiedDates.add(sessionDate);
        });
        
        // Check if studied today or yesterday to start streak
        if (studiedDates.has(today) || studiedDates.has(yesterday)) {
            streak = 1;
            
            // Count backwards for consecutive days
            let checkDate = new Date();
            if (!studiedDates.has(today)) {
                checkDate.setDate(checkDate.getDate() - 1);
            }
            
            while (studiedDates.has(checkDate.toDateString())) {
                checkDate.setDate(checkDate.getDate() - 1);
                if (studiedDates.has(checkDate.toDateString())) {
                    streak++;
                } else {
                    break;
                }
            }
        }
        
        return streak;
    }
}