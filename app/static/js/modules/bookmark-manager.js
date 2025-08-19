/**
 * BookmarkManager Module
 * Manages bookmark creation, removal, and integration with learning interface
 */
class BookmarkManager {
    constructor(subLinkId) {
        this.subLinkId = subLinkId;
        this.bookmarks = new Map(); // Cache for bookmarked alignment indices
        this.rateLimitCount = 0;
        this.rateLimitWindow = Date.now();
        this.maxBookmarksPerHour = 50;
        
        // UI elements
        this.bookmarkModal = null;
        this.bookmarkForm = null;
        this.bookmarkNote = null;
        
        this.initializeUI();
        this.loadUserBookmarks();
    }
    
    /**
     * Initialize bookmark UI components
     */
    initializeUI() {
        // Create bookmark modal if it doesn't exist
        this.createBookmarkModal();
        
        // Add bookmark buttons to existing alignments
        this.addBookmarkButtons();
        
        // Set up event listeners
        this.initializeEventListeners();
    }
    
    /**
     * Create bookmark creation modal
     */
    createBookmarkModal() {
        // Check if modal already exists
        if (document.getElementById('bookmark-modal')) {
            this.bookmarkModal = document.getElementById('bookmark-modal');
            this.bookmarkForm = this.bookmarkModal.querySelector('#bookmark-form');
            this.bookmarkNote = this.bookmarkModal.querySelector('#bookmark-note');
            return;
        }
        
        const modalHtml = `
            <div class="modal fade" id="bookmark-modal" tabindex="-1" role="dialog" aria-labelledby="bookmark-modal-label" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="bookmark-modal-label">
                                <i class="fas fa-bookmark text-warning"></i> Add Bookmark
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <form id="bookmark-form">
                                <div class="mb-3">
                                    <label class="form-label text-muted small">Content Preview:</label>
                                    <div id="bookmark-preview" class="p-2 bg-light rounded small"></div>
                                </div>
                                <div class="mb-3">
                                    <label for="bookmark-note" class="form-label">Note (optional):</label>
                                    <textarea 
                                        id="bookmark-note" 
                                        class="form-control" 
                                        rows="3" 
                                        placeholder="Add a personal note about why you bookmarked this alignment..."
                                        maxlength="1000"
                                    ></textarea>
                                    <div class="form-text text-muted">
                                        <span id="note-char-count">0</span>/1000 characters
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-warning" id="save-bookmark-btn">
                                <i class="fas fa-bookmark"></i> Save Bookmark
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to document
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Get references
        this.bookmarkModal = document.getElementById('bookmark-modal');
        this.bookmarkForm = document.getElementById('bookmark-form');
        this.bookmarkNote = document.getElementById('bookmark-note');
    }
    
    /**
     * Add bookmark buttons to existing subtitle alignments
     */
    addBookmarkButtons() {
        // Add bookmark buttons to each alignment
        document.querySelectorAll('.subtitle-alignment').forEach((alignment, index) => {
            if (!alignment.querySelector('.bookmark-btn')) {
                const bookmarkBtn = this.createBookmarkButton(index);
                alignment.appendChild(bookmarkBtn);
            }
        });
    }
    
    /**
     * Create bookmark button for an alignment
     */
    createBookmarkButton(alignmentIndex) {
        const button = document.createElement('button');
        button.className = 'btn btn-sm bookmark-btn';
        button.dataset.alignmentIndex = alignmentIndex;
        button.title = 'Bookmark this alignment';
        button.innerHTML = '<i class="fas fa-bookmark"></i>';
        
        // Set initial state based on existing bookmarks
        this.updateBookmarkButtonState(button, alignmentIndex);
        
        return button;
    }
    
    /**
     * Initialize event listeners for bookmark functionality
     */
    initializeEventListeners() {
        // Bookmark button clicks (delegated)
        document.addEventListener('click', (e) => {
            if (e.target.closest('.bookmark-btn')) {
                const button = e.target.closest('.bookmark-btn');
                const alignmentIndex = parseInt(button.dataset.alignmentIndex);
                this.handleBookmarkClick(alignmentIndex, button);
            }
        });
        
        // Save bookmark button in modal
        document.addEventListener('click', (e) => {
            if (e.target.id === 'save-bookmark-btn') {
                this.saveBookmark();
            }
        });
        
        // Note character count
        if (this.bookmarkNote) {
            this.bookmarkNote.addEventListener('input', () => {
                this.updateCharacterCount();
            });
        }
        
        // Listen for alignment changes to update bookmark button states
        document.addEventListener('alignmentChanged', (e) => {
            this.onAlignmentChanged(e.detail.index);
        });
    }
    
    /**
     * Handle bookmark button click
     */
    handleBookmarkClick(alignmentIndex, button) {
        if (this.isBookmarked(alignmentIndex)) {
            // Remove bookmark
            this.removeBookmark(alignmentIndex);
        } else {
            // Show bookmark creation modal
            this.showBookmarkModal(alignmentIndex);
        }
    }
    
    /**
     * Show bookmark creation modal
     */
    showBookmarkModal(alignmentIndex) {
        this.currentAlignmentIndex = alignmentIndex;
        
        // Set content preview
        const preview = document.getElementById('bookmark-preview');
        if (preview) {
            preview.innerHTML = this.getAlignmentPreview(alignmentIndex);
        }
        
        // Clear previous note
        if (this.bookmarkNote) {
            this.bookmarkNote.value = '';
            this.updateCharacterCount();
        }
        
        // Show modal
        if (typeof bootstrap !== 'undefined') {
            const modal = new bootstrap.Modal(this.bookmarkModal);
            modal.show();
        } else {
            // Fallback for direct display
            this.bookmarkModal.style.display = 'block';
            this.bookmarkModal.classList.add('show');
        }
    }
    
    /**
     * Get alignment content preview for modal
     */
    getAlignmentPreview(alignmentIndex) {
        const sourceLines = document.querySelectorAll(`[data-index="${alignmentIndex}"][data-type="source"]`);
        const targetLines = document.querySelectorAll(`[data-index="${alignmentIndex}"][data-type="target"]`);
        
        let sourceContent = '';
        let targetContent = '';
        
        sourceLines.forEach(line => {
            sourceContent += line.textContent + ' ';
        });
        
        targetLines.forEach(line => {
            targetContent += line.textContent + ' ';
        });
        
        return `
            <div class="row">
                <div class="col-6">
                    <strong>Source:</strong><br>
                    <span class="text-muted">${sourceContent.trim() || 'No content'}</span>
                </div>
                <div class="col-6">
                    <strong>Target:</strong><br>
                    <span class="text-muted">${targetContent.trim() || 'No content'}</span>
                </div>
            </div>
        `;
    }
    
    /**
     * Save bookmark with API call
     */
    async saveBookmark() {
        if (!this.canCreateBookmark()) {
            this.showError('Rate limit reached. Please wait before creating more bookmarks.');
            return;
        }
        
        try {
            const note = this.bookmarkNote ? this.bookmarkNote.value.trim() : '';
            
            const response = await fetch('/api/bookmarks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    sub_link_id: this.subLinkId,
                    alignment_index: this.currentAlignmentIndex,
                    note: note || null
                })
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                if (response.status === 409) {
                    this.showError('This alignment is already bookmarked.');
                } else {
                    this.showError(result.error || 'Failed to create bookmark');
                }
                return;
            }
            
            // Update local cache
            this.bookmarks.set(this.currentAlignmentIndex, result.bookmark);
            
            // Update UI
            this.updateBookmarkButtonState(
                document.querySelector(`[data-alignment-index="${this.currentAlignmentIndex}"]`),
                this.currentAlignmentIndex
            );
            
            // Update rate limit
            this.updateRateLimit();
            
            // Hide modal
            this.hideBookmarkModal();
            
            // Show success message
            this.showSuccess('Bookmark created successfully!');
            
        } catch (error) {
            console.error('Error creating bookmark:', error);
            this.showError('Network error. Please try again.');
        }
    }
    
    /**
     * Remove bookmark
     */
    async removeBookmark(alignmentIndex) {
        try {
            const bookmark = this.bookmarks.get(alignmentIndex);
            if (!bookmark) {
                this.showError('Bookmark not found.');
                return;
            }
            
            const response = await fetch(`/api/bookmarks/${bookmark.id}`, {
                method: 'DELETE',
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                const result = await response.json();
                this.showError(result.error || 'Failed to remove bookmark');
                return;
            }
            
            // Update local cache
            this.bookmarks.delete(alignmentIndex);
            
            // Update UI
            this.updateBookmarkButtonState(
                document.querySelector(`[data-alignment-index="${alignmentIndex}"]`),
                alignmentIndex
            );
            
            this.showSuccess('Bookmark removed successfully!');
            
        } catch (error) {
            console.error('Error removing bookmark:', error);
            this.showError('Network error. Please try again.');
        }
    }
    
    /**
     * Load user bookmarks for this subtitle link
     */
    async loadUserBookmarks() {
        try {
            const response = await fetch(`/api/bookmarks?limit=100`, {
                method: 'GET',
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                console.warn('Failed to load bookmarks');
                return;
            }
            
            const result = await response.json();
            
            // Filter bookmarks for current sub_link_id and populate cache
            this.bookmarks.clear();
            result.bookmarks
                .filter(bookmark => bookmark.sub_link_id === this.subLinkId)
                .forEach(bookmark => {
                    this.bookmarks.set(bookmark.alignment_index, bookmark);
                });
            
            // Update all bookmark button states
            this.updateAllBookmarkButtons();
            
        } catch (error) {
            console.warn('Error loading bookmarks:', error);
        }
    }
    
    /**
     * Check if alignment is bookmarked
     */
    isBookmarked(alignmentIndex) {
        return this.bookmarks.has(alignmentIndex);
    }
    
    /**
     * Update bookmark button state
     */
    updateBookmarkButtonState(button, alignmentIndex) {
        if (!button) return;
        
        const isBookmarked = this.isBookmarked(alignmentIndex);
        
        if (isBookmarked) {
            button.classList.remove('btn-outline-warning');
            button.classList.add('btn-warning');
            button.title = 'Remove bookmark';
            button.innerHTML = '<i class="fas fa-bookmark"></i>';
        } else {
            button.classList.remove('btn-warning');
            button.classList.add('btn-outline-warning');
            button.title = 'Bookmark this alignment';
            button.innerHTML = '<i class="far fa-bookmark"></i>';
        }
    }
    
    /**
     * Update all bookmark buttons
     */
    updateAllBookmarkButtons() {
        document.querySelectorAll('.bookmark-btn').forEach(button => {
            const alignmentIndex = parseInt(button.dataset.alignmentIndex);
            this.updateBookmarkButtonState(button, alignmentIndex);
        });
    }
    
    /**
     * Handle alignment changes to maintain bookmark button visibility
     */
    onAlignmentChanged(currentIndex) {
        // Add bookmark buttons to newly loaded alignments
        this.addBookmarkButtons();
        
        // Update button states for visible alignments
        this.updateAllBookmarkButtons();
    }
    
    /**
     * Rate limiting for bookmark creation
     */
    canCreateBookmark() {
        const now = Date.now();
        
        // Reset counter if window has passed
        if (now - this.rateLimitWindow > 60 * 60 * 1000) { // 1 hour
            this.rateLimitCount = 0;
            this.rateLimitWindow = now;
        }
        
        return this.rateLimitCount < this.maxBookmarksPerHour;
    }
    
    /**
     * Update rate limit counter
     */
    updateRateLimit() {
        this.rateLimitCount++;
    }
    
    /**
     * Update character count display
     */
    updateCharacterCount() {
        const charCountDisplay = document.getElementById('note-char-count');
        if (charCountDisplay && this.bookmarkNote) {
            const count = this.bookmarkNote.value.length;
            charCountDisplay.textContent = count;
            
            // Update color based on limit
            if (count > 800) {
                charCountDisplay.classList.add('text-warning');
            } else {
                charCountDisplay.classList.remove('text-warning');
            }
        }
    }
    
    /**
     * Hide bookmark modal
     */
    hideBookmarkModal() {
        if (typeof bootstrap !== 'undefined') {
            const modal = bootstrap.Modal.getInstance(this.bookmarkModal);
            if (modal) {
                modal.hide();
            }
        } else {
            this.bookmarkModal.style.display = 'none';
            this.bookmarkModal.classList.remove('show');
        }
    }
    
    /**
     * Show success message
     */
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.showToast(message, 'error');
    }
    
    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        // Create toast element
        const toastId = `toast-${Date.now()}`;
        const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';
        
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        
        // Add to toast container or create one
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '1055';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.insertAdjacentHTML('afterbegin', toastHtml);
        
        // Show toast
        const toastElement = document.getElementById(toastId);
        if (typeof bootstrap !== 'undefined') {
            const toast = new bootstrap.Toast(toastElement, {
                autohide: true,
                delay: type === 'error' ? 5000 : 3000
            });
            toast.show();
            
            // Clean up after hide
            toastElement.addEventListener('hidden.bs.toast', () => {
                toastElement.remove();
            });
        } else {
            // Fallback - show and auto-hide
            toastElement.style.display = 'block';
            setTimeout(() => {
                toastElement.remove();
            }, type === 'error' ? 5000 : 3000);
        }
    }
    
    /**
     * Get bookmarks for current sub_link
     */
    getBookmarks() {
        return Array.from(this.bookmarks.values());
    }
    
    /**
     * Navigate to a bookmarked alignment
     */
    navigateToBookmark(alignmentIndex) {
        // Trigger alignment change event for subtitle player
        const event = new CustomEvent('navigateToAlignment', {
            detail: { index: alignmentIndex }
        });
        document.dispatchEvent(event);
    }
    
    /**
     * Clean up resources
     */
    destroy() {
        // Remove event listeners and clean up
        this.bookmarks.clear();
        
        // Remove modal if it was created
        if (this.bookmarkModal) {
            this.bookmarkModal.remove();
        }
        
        // Remove toast container
        const toastContainer = document.getElementById('toast-container');
        if (toastContainer) {
            toastContainer.remove();
        }
    }
}