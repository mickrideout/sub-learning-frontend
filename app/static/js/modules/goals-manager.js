/**
 * Goals Manager Module
 * Handles learning goals CRUD operations and progress display
 */

export class GoalsManager {
    constructor() {
        this.goals = [];
        this.goalModal = null;
        
        this.init();
    }
    
    async init() {
        console.log('Goals Manager initializing...');
        this.goalModal = new bootstrap.Modal(document.getElementById('goalModal'));
        await this.loadGoals();
        this.bindEvents();
        console.log('Goals Manager initialized');
    }
    
    async loadGoals() {
        try {
            const response = await fetch('/api/goals?active_only=true', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.goals = data.goals || [];
                this.updateGoalsDisplay();
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            console.error('Failed to load goals:', error);
            this.showGoalsError();
        } finally {
            this.hideGoalsLoader();
        }
    }
    
    updateGoalsDisplay() {
        const container = document.getElementById('goals-container');
        if (!container) return;
        
        if (this.goals.length === 0) {
            this.showNoGoalsMessage();
            return;
        }
        
        const html = this.goals.map(goal => {
            const progressColor = this.getGoalProgressColor(goal.progress_percentage);
            const deadlineText = goal.deadline ? new Date(goal.deadline).toLocaleDateString() : 'No deadline';
            const isOverdue = goal.deadline && new Date(goal.deadline) < new Date() && !goal.is_completed;
            
            return `
                <div class="border rounded p-3 mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div>
                            <h6 class="mb-1">${this.formatGoalType(goal.goal_type)}</h6>
                            <small class="text-muted">Target: ${goal.target_value.toLocaleString()}</small>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-${progressColor}">${goal.progress_percentage.toFixed(1)}%</span>
                            ${goal.is_completed ? '<span class="badge bg-success ms-1">Completed</span>' : ''}
                            ${isOverdue ? '<span class="badge bg-danger ms-1">Overdue</span>' : ''}
                        </div>
                    </div>
                    
                    <div class="progress mb-2" style="height: 6px;">
                        <div class="progress-bar bg-${progressColor}" 
                             style="width: ${goal.progress_percentage}%" 
                             role="progressbar"></div>
                    </div>
                    
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="small text-muted">
                            <div>Progress: ${goal.current_value.toLocaleString()} / ${goal.target_value.toLocaleString()}</div>
                            <div>Deadline: ${deadlineText}</div>
                        </div>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="goalsManager.editGoal(${goal.id})" 
                                    title="Edit goal">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="goalsManager.deleteGoal(${goal.id})" 
                                    title="Delete goal">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = html;
    }
    
    formatGoalType(goalType) {
        const typeMap = {
            'daily_minutes': 'Daily Minutes',
            'weekly_alignments': 'Weekly Alignments',
            'movie_completion': 'Movie Completion'
        };
        return typeMap[goalType] || goalType;
    }
    
    getGoalProgressColor(percentage) {
        if (percentage >= 100) return 'success';
        if (percentage >= 75) return 'info';
        if (percentage >= 50) return 'warning';
        if (percentage >= 25) return 'secondary';
        return 'light';
    }
    
    showNoGoalsMessage() {
        const container = document.getElementById('goals-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-target fa-3x text-muted mb-3"></i>
                <h6 class="text-muted">No Learning Goals Set</h6>
                <p class="text-muted mb-3">Create your first learning goal to track your progress!</p>
                <button class="btn btn-primary btn-sm" id="create-first-goal">
                    <i class="fas fa-plus"></i> Create Your First Goal
                </button>
            </div>
        `;
        
        // Bind event for the new button
        document.getElementById('create-first-goal').addEventListener('click', () => {
            this.showCreateGoalModal();
        });
    }
    
    showGoalsError() {
        const container = document.getElementById('goals-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-exclamation-triangle fa-2x text-warning mb-3"></i>
                <p class="text-muted">Unable to load goals</p>
                <button class="btn btn-outline-primary btn-sm" onclick="window.location.reload()">
                    Try Again
                </button>
            </div>
        `;
    }
    
    hideGoalsLoader() {
        const loader = document.getElementById('goals-loader');
        if (loader && loader.parentElement) {
            loader.parentElement.style.display = 'none';
        }
    }
    
    showCreateGoalModal(goalData = null) {
        const modalTitle = document.getElementById('goalModalLabel');
        const saveBtn = document.getElementById('save-goal');
        
        if (goalData) {
            // Editing existing goal
            modalTitle.textContent = 'Edit Learning Goal';
            saveBtn.textContent = 'Update Goal';
            this.populateGoalForm(goalData);
        } else {
            // Creating new goal
            modalTitle.textContent = 'Create Learning Goal';
            saveBtn.textContent = 'Create Goal';
            this.resetGoalForm();
        }
        
        this.goalModal.show();
    }
    
    populateGoalForm(goalData) {
        document.getElementById('goal-type').value = goalData.goal_type;
        document.getElementById('target-value').value = goalData.target_value;
        document.getElementById('deadline').value = goalData.deadline || '';
        
        // Store goal ID for editing
        document.getElementById('goal-form').dataset.goalId = goalData.id;
    }
    
    resetGoalForm() {
        document.getElementById('goal-form').reset();
        delete document.getElementById('goal-form').dataset.goalId;
    }
    
    async saveGoal() {
        const form = document.getElementById('goal-form');
        const goalId = form.dataset.goalId;
        
        const goalData = {
            goal_type: document.getElementById('goal-type').value,
            target_value: parseInt(document.getElementById('target-value').value),
            deadline: document.getElementById('deadline').value || null
        };
        
        // Validate form
        if (!goalData.goal_type || !goalData.target_value || goalData.target_value <= 0) {
            this.showFormError('Please fill in all required fields with valid values.');
            return;
        }
        
        try {
            const url = goalId ? `/api/goals/${goalId}` : '/api/goals';
            const method = goalId ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin',
                body: JSON.stringify(goalData)
            });
            
            if (response.ok) {
                this.goalModal.hide();
                await this.loadGoals();
                this.showSuccessMessage(goalId ? 'Goal updated successfully!' : 'Goal created successfully!');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to save goal');
            }
            
        } catch (error) {
            console.error('Failed to save goal:', error);
            this.showFormError(error.message);
        }
    }
    
    async editGoal(goalId) {
        const goal = this.goals.find(g => g.id === goalId);
        if (goal) {
            this.showCreateGoalModal(goal);
        }
    }
    
    async deleteGoal(goalId) {
        if (!confirm('Are you sure you want to delete this goal? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/goals/${goalId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                await this.loadGoals();
                this.showSuccessMessage('Goal deleted successfully!');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to delete goal');
            }
            
        } catch (error) {
            console.error('Failed to delete goal:', error);
            alert('Failed to delete goal: ' + error.message);
        }
    }
    
    showFormError(message) {
        // Remove existing error messages
        const existingError = document.querySelector('.goal-form-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger goal-form-error';
        errorDiv.textContent = message;
        
        const modalBody = document.querySelector('#goalModal .modal-body');
        modalBody.insertBefore(errorDiv, modalBody.firstChild);
    }
    
    showSuccessMessage(message) {
        // Simple success notification (could be enhanced with a toast library)
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show position-fixed';
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (alertDiv.parentElement) {
                alertDiv.remove();
            }
        }, 3000);
    }
    
    bindEvents() {
        // Create goal button
        const createBtn = document.getElementById('create-goal-btn');
        if (createBtn) {
            createBtn.addEventListener('click', () => {
                this.showCreateGoalModal();
            });
        }
        
        // Save goal button
        const saveBtn = document.getElementById('save-goal');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveGoal();
            });
        }
        
        // Goal type change - update help text
        const goalTypeSelect = document.getElementById('goal-type');
        if (goalTypeSelect) {
            goalTypeSelect.addEventListener('change', (e) => {
                this.updateGoalTypeHelp(e.target.value);
            });
        }
    }
    
    updateGoalTypeHelp(goalType) {
        const helpText = document.getElementById('target-help');
        if (!helpText) return;
        
        const helpMessages = {
            'daily_minutes': 'Enter the number of minutes you want to study each day.',
            'weekly_alignments': 'Enter the number of alignments you want to complete each week.',
            'movie_completion': 'Enter the number of movies you want to complete.'
        };
        
        helpText.textContent = helpMessages[goalType] || 'Enter the target number for your goal.';
    }
    
    toggleGoalsSection() {
        const goalsSection = document.getElementById('goals-section');
        if (goalsSection) {
            const isVisible = goalsSection.style.display !== 'none';
            goalsSection.style.display = isVisible ? 'none' : 'block';
            
            // Load goals if showing for first time
            if (!isVisible && this.goals.length === 0) {
                this.loadGoals();
            }
        }
    }
    
    getGoalsSummary() {
        return {
            total: this.goals.length,
            completed: this.goals.filter(g => g.is_completed).length,
            active: this.goals.filter(g => g.is_active && !g.is_completed).length,
            overdue: this.goals.filter(g => {
                return g.deadline && new Date(g.deadline) < new Date() && !g.is_completed;
            }).length
        };
    }
}