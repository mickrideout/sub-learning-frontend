/**
 * Movie Discovery Component
 * Handles movie catalog display, filtering, and selection
 */
class MovieDiscovery {
    constructor() {
        this.movies = [];
        this.allMovies = []; // Store all movies for highlighting
        this.selectedMovie = null;
        this.isLoading = false;
        this.searchQuery = '';
        this.searchTimeout = null;
        
        // DOM elements
        this.loadingIndicator = null;
        this.errorMessage = null;
        this.movieListContainer = null;
        this.movieList = null;
        this.emptyState = null;
        this.noSearchResults = null;
        this.languagePair = null;
        this.modal = null;
        this.selectedMovieTitle = null;
        this.confirmButton = null;
        this.searchContainer = null;
        this.searchInput = null;
        this.clearSearchButton = null;
        this.searchResultsInfo = null;
        this.searchResultCount = null;
        this.searchQueryDisplay = null;
        this.clearSearchFromNoResults = null;
    }

    /**
     * Initialize the component
     */
    init() {
        this.bindElements();
        this.setupEventListeners();
        this.initializeSearchFromURL();
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
        this.noSearchResults = document.getElementById('no-search-results');
        this.languagePair = document.getElementById('language-pair');
        this.selectedMovieTitle = document.getElementById('selected-movie-title');
        this.confirmButton = document.getElementById('confirm-movie-selection');
        this.searchContainer = document.getElementById('search-container');
        this.searchInput = document.getElementById('movie-search');
        this.clearSearchButton = document.getElementById('clear-search');
        this.searchResultsInfo = document.getElementById('search-results-info');
        this.searchResultCount = document.getElementById('search-result-count');
        this.searchQueryDisplay = document.getElementById('search-query-display');
        this.clearSearchFromNoResults = document.getElementById('clear-search-from-no-results');

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

        // Search input event listener with debouncing
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.handleSearchInput(e.target.value);
            });

            // Handle Enter key for immediate search
            this.searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.performSearch(e.target.value);
                }
            });
        }

        // Clear search button
        if (this.clearSearchButton) {
            this.clearSearchButton.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // Clear search from no results state
        if (this.clearSearchFromNoResults) {
            this.clearSearchFromNoResults.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // Handle browser back/forward navigation
        window.addEventListener('popstate', () => {
            this.initializeSearchFromURL();
            this.loadMovies();
        });
    }

    /**
     * Initialize search from URL parameters
     */
    initializeSearchFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const searchQuery = urlParams.get('search') || '';
        this.searchQuery = searchQuery;
        
        if (this.searchInput) {
            this.searchInput.value = searchQuery;
        }
    }

    /**
     * Handle search input with debouncing
     */
    handleSearchInput(value) {
        // Clear existing timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        // Set new timeout for debounced search
        this.searchTimeout = setTimeout(() => {
            this.performSearch(value);
        }, 300); // 300ms debounce delay
    }

    /**
     * Perform search and update URL
     */
    performSearch(query) {
        const trimmedQuery = query.trim();
        this.searchQuery = trimmedQuery;

        // Update URL parameters
        this.updateURLParams(trimmedQuery);

        // Load movies with search query
        this.loadMovies();
    }

    /**
     * Clear search
     */
    clearSearch() {
        this.searchQuery = '';
        if (this.searchInput) {
            this.searchInput.value = '';
        }
        this.updateURLParams('');
        this.loadMovies();
    }

    /**
     * Update URL parameters for search
     */
    updateURLParams(searchQuery) {
        const url = new URL(window.location);
        if (searchQuery) {
            url.searchParams.set('search', searchQuery);
        } else {
            url.searchParams.delete('search');
        }
        
        // Update URL without reloading page
        window.history.pushState({}, '', url);
    }

    /**
     * Load movies from API
     */
    async loadMovies() {
        this.setLoadingState(true);
        this.hideError();

        try {
            // Build API URL with search parameter if needed
            let apiUrl = '/api/movies';
            if (this.searchQuery) {
                const params = new URLSearchParams({ search: this.searchQuery });
                apiUrl += '?' + params.toString();
            }

            const response = await fetch(apiUrl, {
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
            this.allMovies = this.movies; // Store for highlighting
            this.displayLanguagePair(data.language_pair);
            this.displaySearchResults(data);
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
     * Display search results information
     */
    displaySearchResults(data) {
        // Show search container once movies are loaded
        if (this.searchContainer) {
            this.searchContainer.classList.remove('d-none');
        }

        // Update search results info if search was performed
        if (data.search && this.searchResultsInfo) {
            this.searchResultsInfo.classList.remove('d-none');
            if (this.searchResultCount) {
                const resultText = data.search.result_count === 1 
                    ? `Found 1 movie matching "${data.search.query}"` 
                    : `Found ${data.search.result_count} movies matching "${data.search.query}"`;
                this.searchResultCount.textContent = resultText;
            }
        } else if (this.searchResultsInfo) {
            this.searchResultsInfo.classList.add('d-none');
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
            // Show appropriate empty state based on whether we're searching
            if (this.searchQuery) {
                this.showNoSearchResults();
            } else {
                this.showEmptyState();
            }
            return;
        }

        this.hideEmptyState();
        this.hideNoSearchResults();
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

        // Get highlighted title if search query exists
        const displayTitle = this.searchQuery ? 
            this.highlightSearchTerm(movie.title, this.searchQuery) :
            this.escapeHtml(movie.title);

        item.innerHTML = `
            <div>
                <h6 class="mb-1">${displayTitle}</h6>
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
     * Highlight search term in text with XSS protection
     */
    highlightSearchTerm(text, searchTerm) {
        if (!searchTerm) return this.escapeHtml(text);
        
        // Escape both text and search term to prevent XSS
        const escapedText = this.escapeHtml(text);
        const escapedSearchTerm = this.escapeHtml(searchTerm);
        
        // Create regex for case-insensitive highlighting
        const regex = new RegExp(`(${escapedSearchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        
        // Replace with highlighted version
        return escapedText.replace(regex, '<mark class="bg-warning">$1</mark>');
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
     * Show no search results state
     */
    showNoSearchResults() {
        if (this.noSearchResults) {
            this.noSearchResults.classList.remove('d-none');
            
            // Update search query display
            if (this.searchQueryDisplay) {
                this.searchQueryDisplay.textContent = this.searchQuery;
            }
        }
        if (this.movieListContainer) {
            this.movieListContainer.classList.add('d-none');
        }
    }

    /**
     * Hide no search results state
     */
    hideNoSearchResults() {
        if (this.noSearchResults) {
            this.noSearchResults.classList.add('d-none');
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