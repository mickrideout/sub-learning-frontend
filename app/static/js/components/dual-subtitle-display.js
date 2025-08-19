/**
 * DualSubtitleDisplay Component
 * Handles side-by-side subtitle rendering with Bootstrap grid system
 */
class DualSubtitleDisplay {
    constructor(sourceColumnId = 'source-content', targetColumnId = 'target-content') {
        this.sourceColumn = document.getElementById(sourceColumnId);
        this.targetColumn = document.getElementById(targetColumnId);
        this.sourceLangTitle = document.getElementById('source-lang-title');
        this.targetLangTitle = document.getElementById('target-lang-title');
        
        this.currentAlignment = null;
        this.alignmentData = [];
        this.currentIndex = 0;
        
        // Font size and layout preferences
        this.fontSize = this.loadPreference('fontSize', 'font-large');
        this.columnLayout = this.loadPreference('columnLayout', 'equal');
        
        this.initializeEventListeners();
        this.applyUserPreferences();
    }
    
    /**
     * Initialize event listeners for user interactions
     */
    initializeEventListeners() {
        // Font size controls
        const fontButtons = document.querySelectorAll('[id^="font-"]');
        fontButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.setFontSize(e.target.id);
            });
        });
        
        // Column width controls
        const widthButtons = document.querySelectorAll('[id^="width-"]');
        widthButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.setColumnLayout(e.target.id);
            });
        });
        
        // Subtitle line click handlers (delegated)
        this.sourceColumn.addEventListener('click', (e) => {
            if (e.target.classList.contains('subtitle-line')) {
                const index = parseInt(e.target.dataset.index);
                this.highlightAlignment(index);
            }
        });
        
        this.targetColumn.addEventListener('click', (e) => {
            if (e.target.classList.contains('subtitle-line')) {
                const index = parseInt(e.target.dataset.index);
                this.highlightAlignment(index);
            }
        });
    }
    
    /**
     * Set language titles for the display columns
     */
    setLanguageTitles(sourceLanguage, targetLanguage) {
        if (this.sourceLangTitle) {
            this.sourceLangTitle.textContent = sourceLanguage;
        }
        if (this.targetLangTitle) {
            this.targetLangTitle.textContent = targetLanguage;
        }
    }
    
    /**
     * Load alignment data and render dual subtitle display
     */
    renderAlignments(alignmentData, sourceLines, targetLines) {
        this.alignmentData = alignmentData;
        
        if (!alignmentData || alignmentData.length === 0) {
            this.showPlaceholder('No subtitle alignments available');
            return;
        }
        
        this.clearContent();
        
        // Render source and target subtitle lines
        alignmentData.forEach((alignment, index) => {
            this.renderAlignmentPair(alignment, sourceLines, targetLines, index);
        });
        
        // Highlight first alignment if none is selected
        if (this.currentIndex < alignmentData.length) {
            this.highlightAlignment(this.currentIndex);
        }
    }
    
    /**
     * Render a single alignment pair (source and target lines)
     */
    renderAlignmentPair(alignment, sourceLines, targetLines, index) {
        try {
            const sourceLineIds = alignment.source_lines || [];
            const targetLineIds = alignment.target_lines || [];
            
            // Create source subtitle lines
            const sourceContent = this.createSubtitleLines(sourceLineIds, sourceLines, index, 'source');
            const targetContent = this.createSubtitleLines(targetLineIds, targetLines, index, 'target');
            
            this.sourceColumn.appendChild(sourceContent);
            this.targetColumn.appendChild(targetContent);
            
        } catch (error) {
            console.error('Error rendering alignment pair:', error);
            this.showError('Error rendering subtitle alignment');
        }
    }
    
    /**
     * Create subtitle line elements for display
     */
    createSubtitleLines(lineIds, allLines, alignmentIndex, type) {
        const container = document.createElement('div');
        container.className = 'subtitle-alignment';
        container.dataset.alignmentIndex = alignmentIndex;
        
        if (!lineIds || lineIds.length === 0) {
            const emptyLine = document.createElement('div');
            emptyLine.className = 'subtitle-line empty-line';
            emptyLine.dataset.index = alignmentIndex;
            emptyLine.innerHTML = '<em>No text</em>';
            container.appendChild(emptyLine);
            return container;
        }
        
        lineIds.forEach(lineId => {
            const line = allLines.find(l => l.id === lineId);
            if (line) {
                const lineElement = document.createElement('div');
                lineElement.className = 'subtitle-line';
                lineElement.dataset.index = alignmentIndex;
                lineElement.dataset.lineId = lineId;
                lineElement.dataset.type = type;
                
                // Sanitize and set content
                lineElement.textContent = line.content || '';
                
                container.appendChild(lineElement);
            }
        });
        
        return container;
    }
    
    /**
     * Highlight current alignment and sync between columns
     */
    highlightAlignment(index) {
        if (index < 0 || index >= this.alignmentData.length) {
            return;
        }
        
        // Remove previous highlights
        this.clearHighlights();
        
        // Highlight current alignment in both columns
        const sourceLines = this.sourceColumn.querySelectorAll(`[data-index="${index}"]`);
        const targetLines = this.targetColumn.querySelectorAll(`[data-index="${index}"]`);
        
        sourceLines.forEach(line => line.classList.add('active'));
        targetLines.forEach(line => line.classList.add('active'));
        
        this.currentIndex = index;
        
        // Scroll to ensure visibility
        if (sourceLines.length > 0) {
            this.scrollToElement(sourceLines[0]);
        }
        if (targetLines.length > 0) {
            this.scrollToElement(targetLines[0]);
        }
        
        // Trigger alignment change event
        this.onAlignmentChange(index);
    }
    
    /**
     * Clear all highlights from subtitle lines
     */
    clearHighlights() {
        const allLines = document.querySelectorAll('.subtitle-line.active');
        allLines.forEach(line => line.classList.remove('active'));
    }
    
    /**
     * Scroll element into view smoothly
     */
    scrollToElement(element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }
    
    /**
     * Set font size and apply to display
     */
    setFontSize(fontSizeId) {
        // Remove previous font size classes
        const fontClasses = ['font-small', 'font-medium', 'font-large', 'font-xlarge'];
        document.body.classList.remove(...fontClasses);
        
        // Add new font size class
        const fontSize = fontSizeId;
        document.body.classList.add(fontSize);
        this.fontSize = fontSize;
        
        // Update button states
        const fontButtons = document.querySelectorAll('[id^="font-"]');
        fontButtons.forEach(btn => btn.classList.remove('active'));
        document.getElementById(fontSizeId).classList.add('active');
        
        // Save preference
        this.savePreference('fontSize', fontSize);
    }
    
    /**
     * Set column layout and apply visual changes
     */
    setColumnLayout(layoutId) {
        const subtitleRow = document.getElementById('subtitle-row');
        
        // Remove previous layout classes
        subtitleRow.classList.remove('width-left-favor', 'width-right-favor');
        
        // Apply new layout
        switch(layoutId) {
            case 'width-left':
                subtitleRow.classList.add('width-left-favor');
                this.columnLayout = 'left';
                break;
            case 'width-right':
                subtitleRow.classList.add('width-right-favor');
                this.columnLayout = 'right';
                break;
            case 'width-equal':
            default:
                this.columnLayout = 'equal';
                break;
        }
        
        // Update button states
        const widthButtons = document.querySelectorAll('[id^="width-"]');
        widthButtons.forEach(btn => btn.classList.remove('active'));
        document.getElementById(layoutId).classList.add('active');
        
        // Save preference
        this.savePreference('columnLayout', this.columnLayout);
    }
    
    /**
     * Apply user preferences from localStorage
     */
    applyUserPreferences() {
        // Apply font size
        this.setFontSize(this.fontSize);
        
        // Apply column layout
        const layoutMap = {
            'left': 'width-left',
            'right': 'width-right',
            'equal': 'width-equal'
        };
        this.setColumnLayout(layoutMap[this.columnLayout] || 'width-equal');
    }
    
    /**
     * Save user preference to localStorage
     */
    savePreference(key, value) {
        try {
            localStorage.setItem(`learning_${key}`, value);
        } catch (error) {
            console.warn('Failed to save preference:', error);
        }
    }
    
    /**
     * Load user preference from localStorage
     */
    loadPreference(key, defaultValue) {
        try {
            return localStorage.getItem(`learning_${key}`) || defaultValue;
        } catch (error) {
            console.warn('Failed to load preference:', error);
            return defaultValue;
        }
    }
    
    /**
     * Clear content from both columns
     */
    clearContent() {
        this.sourceColumn.innerHTML = '';
        this.targetColumn.innerHTML = '';
    }
    
    /**
     * Show placeholder message when no content is available
     */
    showPlaceholder(message) {
        this.clearContent();
        
        const sourcePlaceholder = document.createElement('div');
        sourcePlaceholder.className = 'subtitle-line-placeholder';
        sourcePlaceholder.textContent = message;
        
        const targetPlaceholder = document.createElement('div');
        targetPlaceholder.className = 'subtitle-line-placeholder';
        targetPlaceholder.textContent = message;
        
        this.sourceColumn.appendChild(sourcePlaceholder);
        this.targetColumn.appendChild(targetPlaceholder);
    }
    
    /**
     * Show error message in display
     */
    showError(message) {
        this.clearContent();
        
        const sourceError = document.createElement('div');
        sourceError.className = 'subtitle-line-placeholder text-danger';
        sourceError.textContent = message;
        
        const targetError = document.createElement('div');
        targetError.className = 'subtitle-line-placeholder text-danger';
        targetError.textContent = message;
        
        this.sourceColumn.appendChild(sourceError);
        this.targetColumn.appendChild(targetError);
    }
    
    /**
     * Get current alignment index
     */
    getCurrentIndex() {
        return this.currentIndex;
    }
    
    /**
     * Get total number of alignments
     */
    getTotalAlignments() {
        return this.alignmentData.length;
    }
    
    /**
     * Move to next alignment
     */
    nextAlignment() {
        if (this.currentIndex < this.alignmentData.length - 1) {
            this.highlightAlignment(this.currentIndex + 1);
            return true;
        }
        return false;
    }
    
    /**
     * Move to previous alignment
     */
    previousAlignment() {
        if (this.currentIndex > 0) {
            this.highlightAlignment(this.currentIndex - 1);
            return true;
        }
        return false;
    }
    
    /**
     * Callback for alignment change events
     * Override this method to handle alignment changes
     */
    onAlignmentChange(index) {
        // Default implementation - can be overridden
        console.log('Alignment changed to index:', index);
    }
    
    /**
     * Update alignment highlighting without changing current index
     */
    syncHighlight(index) {
        this.highlightAlignment(index);
    }
    
    /**
     * Get current alignment data
     */
    getCurrentAlignment() {
        if (this.currentIndex >= 0 && this.currentIndex < this.alignmentData.length) {
            return this.alignmentData[this.currentIndex];
        }
        return null;
    }
}