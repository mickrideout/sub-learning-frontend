/**
 * Language Selection Component
 * Handles language selection interface for native and target language preferences
 */

class LanguageSelector {
    constructor() {
        this.languages = [];
        this.selectedNative = null;
        this.selectedTarget = null;
        
        this.elements = {
            form: document.getElementById('language-selection-form'),
            nativeSelect: document.getElementById('native-language'),
            targetSelect: document.getElementById('target-language'),
            sameLanguageError: document.getElementById('same-language-error'),
            saveButton: document.getElementById('save-languages-btn'),
            loadingState: document.getElementById('loading-state'),
            successState: document.getElementById('success-state'),
            nativeLanguageName: document.getElementById('native-language-name'),
            targetLanguageName: document.getElementById('target-language-name')
        };
        
        this.init();
    }
    
    async init() {
        try {
            await this.loadLanguages();
            this.setupEventListeners();
            this.restoreSelectionFromStorage();
        } catch (error) {
            console.error('Failed to initialize language selector:', error);
            this.showError('Failed to load languages. Please refresh the page.');
        }
    }
    
    async loadLanguages() {
        try {
            const response = await fetch('/api/languages');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.languages = data.languages || [];
            
            this.populateLanguageSelects();
            
        } catch (error) {
            console.error('Error loading languages:', error);
            throw error;
        }
    }
    
    populateLanguageSelects() {
        // Clear existing options (except the first placeholder option)
        this.clearSelectOptions(this.elements.nativeSelect);
        this.clearSelectOptions(this.elements.targetSelect);
        
        // Populate both selects with language options
        this.languages.forEach(language => {
            const nativeOption = this.createLanguageOption(language);
            const targetOption = this.createLanguageOption(language);
            
            this.elements.nativeSelect.appendChild(nativeOption);
            this.elements.targetSelect.appendChild(targetOption);
        });
    }
    
    clearSelectOptions(selectElement) {
        // Keep the first option (placeholder), remove all others
        const options = selectElement.querySelectorAll('option:not(:first-child)');
        options.forEach(option => option.remove());
    }
    
    createLanguageOption(language) {
        const option = document.createElement('option');
        option.value = language.id;
        option.textContent = language.display_name;
        option.dataset.code = language.code;
        option.dataset.name = language.name;
        return option;
    }
    
    setupEventListeners() {
        // Native language selection
        this.elements.nativeSelect.addEventListener('change', (e) => {
            this.handleNativeLanguageChange(e.target.value);
        });
        
        // Target language selection
        this.elements.targetSelect.addEventListener('change', (e) => {
            this.handleTargetLanguageChange(e.target.value);
        });
        
        // Form submission
        this.elements.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmit();
        });
    }
    
    handleNativeLanguageChange(languageId) {
        this.selectedNative = languageId ? parseInt(languageId) : null;
        this.saveToSessionStorage();
        this.updateSelectionDisplay('native');
        this.validateSelection();
    }
    
    handleTargetLanguageChange(languageId) {
        this.selectedTarget = languageId ? parseInt(languageId) : null;
        this.saveToSessionStorage();
        this.updateSelectionDisplay('target');
        this.validateSelection();
    }
    
    updateSelectionDisplay(type) {
        const languageId = type === 'native' ? this.selectedNative : this.selectedTarget;
        const displayElement = type === 'native' ? 
            this.elements.nativeLanguageName : 
            this.elements.targetLanguageName;
        const panelElement = document.querySelector(`[data-language-type="${type}"] .selected-language-display`);
        
        if (languageId && displayElement && panelElement) {
            const language = this.languages.find(lang => lang.id === languageId);
            if (language) {
                displayElement.textContent = language.display_name;
                panelElement.classList.remove('d-none');
            }
        } else if (panelElement) {
            panelElement.classList.add('d-none');
        }
    }
    
    validateSelection() {
        const isValid = this.selectedNative && this.selectedTarget;
        const isSameLanguage = this.selectedNative === this.selectedTarget;
        
        // Show/hide same language error
        if (isSameLanguage && this.selectedNative && this.selectedTarget) {
            this.elements.sameLanguageError.classList.remove('d-none');
            this.elements.saveButton.disabled = true;
        } else {
            this.elements.sameLanguageError.classList.add('d-none');
            this.elements.saveButton.disabled = !isValid;
        }
        
        // Update form validation classes
        this.updateValidationClasses(this.elements.nativeSelect, !!this.selectedNative);
        this.updateValidationClasses(this.elements.targetSelect, !!this.selectedTarget);
        
        return isValid && !isSameLanguage;
    }
    
    updateValidationClasses(element, isValid) {
        element.classList.remove('is-valid', 'is-invalid');
        
        if (element.value) {
            if (isValid) {
                element.classList.add('is-valid');
            } else {
                element.classList.add('is-invalid');
            }
        }
    }
    
    saveToSessionStorage() {
        const selectionData = {
            nativeLanguageId: this.selectedNative,
            targetLanguageId: this.selectedTarget,
            timestamp: Date.now()
        };
        
        try {
            sessionStorage.setItem('languageSelection', JSON.stringify(selectionData));
        } catch (error) {
            console.warn('Could not save to sessionStorage:', error);
        }
    }
    
    restoreSelectionFromStorage() {
        try {
            const storedData = sessionStorage.getItem('languageSelection');
            if (storedData) {
                const data = JSON.parse(storedData);
                
                // Restore selections if they exist and are valid
                if (data.nativeLanguageId) {
                    this.elements.nativeSelect.value = data.nativeLanguageId;
                    this.handleNativeLanguageChange(data.nativeLanguageId);
                }
                
                if (data.targetLanguageId) {
                    this.elements.targetSelect.value = data.targetLanguageId;
                    this.handleTargetLanguageChange(data.targetLanguageId);
                }
            }
        } catch (error) {
            console.warn('Could not restore from sessionStorage:', error);
        }
    }
    
    async handleFormSubmit() {
        if (!this.validateSelection()) {
            return;
        }
        
        this.showLoadingState();
        
        try {
            const response = await fetch('/api/user/languages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    native_language_id: this.selectedNative,
                    target_language_id: this.selectedTarget
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showSuccessState();
                this.clearSessionStorage();
                
                // Redirect to dashboard after short delay
                setTimeout(() => {
                    window.location.href = '/auth/dashboard';
                }, 2000);
                
            } else {
                throw new Error(data.error || 'Failed to save language preferences');
            }
            
        } catch (error) {
            console.error('Error saving language preferences:', error);
            this.hideLoadingState();
            this.showError(error.message || 'Failed to save language preferences. Please try again.');
        }
    }
    
    showLoadingState() {
        this.elements.form.classList.add('d-none');
        this.elements.loadingState.classList.remove('d-none');
    }
    
    hideLoadingState() {
        this.elements.form.classList.remove('d-none');
        this.elements.loadingState.classList.add('d-none');
    }
    
    showSuccessState() {
        this.elements.loadingState.classList.add('d-none');
        this.elements.successState.classList.remove('d-none');
    }
    
    showError(message) {
        // Create or update error alert
        let errorAlert = document.getElementById('error-alert');
        if (!errorAlert) {
            errorAlert = document.createElement('div');
            errorAlert.id = 'error-alert';
            errorAlert.className = 'alert alert-danger mt-3';
            this.elements.form.parentNode.appendChild(errorAlert);
        }
        
        errorAlert.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>
            <strong>Error:</strong> ${message}
        `;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (errorAlert && errorAlert.parentNode) {
                errorAlert.parentNode.removeChild(errorAlert);
            }
        }, 5000);
    }
    
    clearSessionStorage() {
        try {
            sessionStorage.removeItem('languageSelection');
        } catch (error) {
            console.warn('Could not clear sessionStorage:', error);
        }
    }
}

// Initialize the language selector when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new LanguageSelector();
});