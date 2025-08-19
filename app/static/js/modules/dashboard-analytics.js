/**
 * Dashboard Analytics Module
 * Handles comprehensive learning analytics and Chart.js visualizations
 */

export class DashboardAnalytics {
    constructor() {
        this.dashboardStats = null;
        this.streakData = null;
        this.progressChart = null;
        this.chartPeriod = 'weekly';
        
        this.init();
    }
    
    async init() {
        console.log('Dashboard Analytics initializing...');
        await this.loadDashboardStats();
        await this.loadStreakData();
        await this.loadProgressChart();
        this.bindEvents();
        console.log('Dashboard Analytics initialized');
    }
    
    async loadDashboardStats() {
        try {
            const response = await fetch('/api/progress/dashboard', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.dashboardStats = data.stats;
                this.updateStatsDisplay();
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            console.error('Failed to load dashboard statistics:', error);
            this.showStatsError();
        }
    }
    
    async loadStreakData() {
        try {
            const response = await fetch('/api/progress/streak', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.streakData = data.streak;
                this.updateStreakDisplay();
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            console.error('Failed to load streak data:', error);
        }
    }
    
    async loadProgressChart() {
        try {
            const response = await fetch(`/api/progress/charts?period=${this.chartPeriod}&days=30`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.renderProgressChart(data.chart_data);
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            console.error('Failed to load progress chart data:', error);
            this.showChartError();
        }
    }
    
    updateStatsDisplay() {
        if (!this.dashboardStats) return;
        
        const stats = this.dashboardStats;
        
        // Update enhanced statistics
        this.updateElement('total-alignments-completed', stats.total_alignments?.toLocaleString() || '0');
        this.updateElement('avg-session-time', Math.round(stats.avg_session_duration || 0));
        this.updateElement('completion-rate', `${stats.completion_rate || 0}%`);
        this.updateElement('learning-velocity', (stats.learning_velocity || 0).toFixed(1));
        this.updateElement('active-sessions', stats.active_sessions || 0);
        this.updateElement('movies-completed', stats.movies_completed || 0);
        this.updateElement('total-study-time', Math.round((stats.total_study_minutes || 0) / 60));
        
        // Update legacy dashboard elements
        this.updateElement('movies-studied', stats.active_sessions || 0);
        this.updateElement('total-minutes', stats.total_study_minutes || 0);
        
        // Update progress bar
        const progressBar = document.getElementById('overall-progress-bar');
        const progressText = document.getElementById('overall-progress-text');
        
        if (progressBar && progressText) {
            const overallProgress = stats.completion_rate || 0;
            progressBar.style.width = `${overallProgress}%`;
            progressText.textContent = `${Math.round(overallProgress)}%`;
        }
    }
    
    updateStreakDisplay() {
        if (!this.streakData) return;
        
        this.updateElement('current-streak', this.streakData.current_streak || 0);
    }
    
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
    
    renderProgressChart(chartData) {
        const canvas = document.getElementById('progress-chart');
        if (!canvas) return;
        
        // Destroy existing chart if it exists
        if (this.progressChart) {
            this.progressChart.destroy();
        }
        
        const ctx = canvas.getContext('2d');
        
        this.progressChart = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `Learning Progress - ${this.chartPeriod.charAt(0).toUpperCase() + this.chartPeriod.slice(1)} View`
                    },
                    legend: {
                        position: 'bottom',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Value'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time Period'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index',
                }
            }
        });
    }
    
    showStatsError() {
        // Show error message for stats
        const elements = [
            'total-alignments-completed', 'current-streak', 'avg-session-time',
            'completion-rate', 'learning-velocity', 'active-sessions',
            'movies-completed', 'total-study-time'
        ];
        
        elements.forEach(id => {
            this.updateElement(id, 'Error');
        });
    }
    
    showChartError() {
        const canvas = document.getElementById('progress-chart');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.font = '16px Arial';
            ctx.fillStyle = '#6c757d';
            ctx.textAlign = 'center';
            ctx.fillText('Unable to load chart data', canvas.width / 2, canvas.height / 2);
        }
    }
    
    bindEvents() {
        // Refresh analytics button
        const refreshBtn = document.getElementById('refresh-analytics');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', async () => {
                refreshBtn.disabled = true;
                const icon = refreshBtn.querySelector('i');
                if (icon) icon.classList.add('fa-spin');
                
                await this.loadDashboardStats();
                await this.loadStreakData();
                await this.loadProgressChart();
                
                refreshBtn.disabled = false;
                if (icon) icon.classList.remove('fa-spin');
            });
        }
        
        // Chart period toggle
        const periodInputs = document.querySelectorAll('input[name="chart-period"]');
        periodInputs.forEach(input => {
            input.addEventListener('change', async (e) => {
                if (e.target.checked) {
                    this.chartPeriod = e.target.value;
                    await this.loadProgressChart();
                }
            });
        });
    }
    
    async refreshAll() {
        await this.loadDashboardStats();
        await this.loadStreakData();
        await this.loadProgressChart();
    }
}