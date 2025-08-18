/**
 * Movie Discovery Component
 * Handles movie catalog display, filtering, and selection
 */
class MovieDiscovery {
    constructor() {
        this.movies = [];
        this.selectedMovie = null;
        this.isLoading = false;
        
        // DOM elements
        this.loadingIndicator = null;
        this.errorMessage = null;
        this.movieListContainer = null;
        this.movieList = null;
        this.emptyState = null;
        this.languagePair = null;
        this.modal = null;
        this.selectedMovieTitle = null;
        this.confirmButton = null;
    }

    /**
     * Initialize the component
     */
    init() {
        this.bindElements();
        this.setupEventListeners();
        this.loadMovies();
    }

    /**
     * Bind DOM elements
     */
    bindElements() {
        this.loadingIndicator = document.getElementById('loading-indicator');
        this.errorMessage = document.getElementById('error-message');
        this.movieListContainer = document.getElementById('movie-list-container');
        this.movieList = document.getElementById('movie-list');
        this.emptyState = document.getElementById('empty-state');
        this.languagePair = document.getElementById('language-pair');
        this.selectedMovieTitle = document.getElementById('selected-movie-title');
        this.confirmButton = document.getElementById('confirm-movie-selection');

        // Initialize Bootstrap modal
        const modalElement = document.getElementById('movieSelectionModal');
        if (modalElement) {
            this.modal = new bootstrap.Modal(modalElement);
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        if (this.confirmButton) {
            this.confirmButton.addEventListener('click', () => {
                this.handleMovieConfirmation();
            });
        }
    }

    /**
     * Load movies from API
     */
    async loadMovies() {
        this.setLoadingState(true);
        this.hideError();

        try {
            const response = await fetch('/api/movies', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.movies = data.movies || [];
            this.displayLanguagePair(data.language_pair);
            this.renderMovies();

        } catch (error) {
            console.error('Error loading movies:', error);
            this.showError(error.message);
        } finally {
            this.setLoadingState(false);
        }
    }

    /**
     * Display language pair information
     */
    displayLanguagePair(languagePair) {
        if (this.languagePair && languagePair) {
            this.languagePair.textContent = `${languagePair.native_language_id} → ${languagePair.target_language_id}`;
        }
    }

    /**
     * Render movies list
     */
    renderMovies() {
        if (!this.movieList) return;

        // Clear existing content
        this.movieList.innerHTML = '';

        if (this.movies.length === 0) {
            this.showEmptyState();
            return;
        }

        this.hideEmptyState();
        this.showMovieList();

        // Create movie list items
        this.movies.forEach(movie => {
            const movieItem = this.createMovieItem(movie);
            this.movieList.appendChild(movieItem);
        });
    }

    /**
     * Create a movie list item element
     */
    createMovieItem(movie) {
        const item = document.createElement('div');
        item.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
        item.style.cursor = 'pointer';
        
        // Add hover effect classes
        item.addEventListener('mouseenter', () => {
            item.classList.add('bg-light');
        });
        
        item.addEventListener('mouseleave', () => {
            item.classList.remove('bg-light');
        });

        item.innerHTML = `
            <div>
                <h6 class="mb-1">${this.escapeHtml(movie.title)}</h6>
                <small class="text-muted">
                    <i class="fas fa-closed-captioning me-1"></i>
                    Subtitles available
                </small>
            </div>
            <div>
                <i class="fas fa-play-circle text-primary fa-lg"></i>
            </div>
        `;

        // Add click event listener
        item.addEventListener('click', () => {
            this.selectMovie(movie);
        });

        return item;
    }

    /**
     * Handle movie selection
     */
    selectMovie(movie) {
        this.selectedMovie = movie;
        
        if (this.selectedMovieTitle) {
            this.selectedMovieTitle.textContent = movie.title;
        }

        // Show confirmation modal
        if (this.modal) {
            this.modal.show();
        }
    }

    /**
     * Handle movie selection confirmation
     */
    handleMovieConfirmation() {
        if (!this.selectedMovie) return;

        // Store selected movie in session storage
        sessionStorage.setItem('selectedMovie', JSON.stringify(this.selectedMovie));

        // Hide modal
        if (this.modal) {
            this.modal.hide();
        }

        // Navigate to learning interface (placeholder for Epic 3)
        // For now, just show a success message
        this.showSuccessMessage();
    }

    /**
     * Show success message for movie selection
     */
    showSuccessMessage() {
        // Create temporary success alert
        const successAlert = document.createElement('div');
        successAlert.className = 'alert alert-success alert-dismissible fade show';
        successAlert.innerHTML = `
            <strong>Movie Selected!</strong> ${this.escapeHtml(this.selectedMovie.title)} has been selected for your learning session.
            <small class="d-block mt-1">Learning interface will be available in Epic 3.</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at the top of the container
        const container = document.querySelector('.container .row .col-md-8');
        if (container) {
            container.insertBefore(successAlert, container.firstChild);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (successAlert.parentNode) {
                    successAlert.remove();
                }
            }, 5000);
        }
    }

    /**
     * Set loading state
     */
    setLoadingState(loading) {
        this.isLoading = loading;
        
        if (this.loadingIndicator) {
            this.loadingIndicator.style.display = loading ? 'block' : 'none';
        }
        
        if (this.movieListContainer) {
            this.movieListContainer.style.display = loading ? 'none' : 'block';
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        if (this.errorMessage) {
            this.errorMessage.classList.remove('d-none');
            const errorText = this.errorMessage.querySelector('#error-text');
            if (errorText) {
                errorText.textContent = message;
            }
        }
    }

    /**
     * Hide error message
     */
    hideError() {
        if (this.errorMessage) {
            this.errorMessage.classList.add('d-none');
        }
    }

    /**
     * Show movie list
     */
    showMovieList() {
        if (this.movieListContainer) {
            this.movieListContainer.classList.remove('d-none');
        }
    }

    /**
     * Show empty state
     */
    showEmptyState() {
        if (this.emptyState) {
            this.emptyState.classList.remove('d-none');
        }
        if (this.movieListContainer) {
            this.movieListContainer.classList.add('d-none');
        }
    }

    /**
     * Hide empty state
     */
    hideEmptyState() {
        if (this.emptyState) {
            this.emptyState.classList.add('d-none');
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}