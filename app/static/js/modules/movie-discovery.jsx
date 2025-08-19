export class MovieDiscovery {
  constructor() {
    this.languages = []
    this.movies = []
    this.filteredMovies = []
    this.currentNativeLanguage = ""
    this.currentTargetLanguage = ""
    this.currentSearchTerm = ""
    this.currentLetter = ""

    this.init()
  }

  async init() {
    this.bindEvents()
    this.createAlphabetFilter()
    await this.loadLanguages()
  }

  bindEvents() {
    // Language selectors
    document.getElementById("nativeLanguage").addEventListener("change", (e) => {
      this.currentNativeLanguage = e.target.value
      this.loadMovies()
    })

    document.getElementById("targetLanguage").addEventListener("change", (e) => {
      this.currentTargetLanguage = e.target.value
      this.loadMovies()
    })

    // Search functionality
    const searchInput = document.getElementById("movieSearch")
    const searchBtn = document.getElementById("searchBtn")

    searchInput.addEventListener("input", (e) => {
      this.currentSearchTerm = e.target.value
      this.filterMovies()
    })

    searchBtn.addEventListener("click", () => {
      this.filterMovies()
    })

    // Clear filters
    document.getElementById("clearFilters").addEventListener("click", () => {
      this.clearAllFilters()
    })
  }

  createAlphabetFilter() {
    const container = document.getElementById("alphabetFilter")
    const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("")

    alphabet.forEach((letter) => {
      const btn = document.createElement("a")
      btn.href = "#"
      btn.className = "alphabet-btn"
      btn.textContent = letter
      btn.addEventListener("click", (e) => {
        e.preventDefault()
        this.filterByLetter(letter)
      })
      container.appendChild(btn)
    })
  }

  async loadLanguages() {
    try {
      const languages = await window.app.apiCall("/api/languages")
      this.languages = languages
      this.populateLanguageSelectors()
    } catch (error) {
      console.error("Failed to load languages:", error)
      window.app.showToast("Failed to load languages", "error")
    }
  }

  populateLanguageSelectors() {
    const nativeSelect = document.getElementById("nativeLanguage")
    const targetSelect = document.getElementById("targetLanguage")

    // Clear existing options (except first)
    nativeSelect.innerHTML = '<option value="">Select your native language...</option>'
    targetSelect.innerHTML = '<option value="">Select target language...</option>'

    this.languages.forEach((language) => {
      const nativeOption = new Option(language.display_name, language.id)
      const targetOption = new Option(language.display_name, language.id)

      nativeSelect.appendChild(nativeOption)
      targetSelect.appendChild(targetOption)
    })
  }

  async loadMovies() {
    if (!this.currentNativeLanguage || !this.currentTargetLanguage) {
      this.displayEmptyState()
      return
    }

    if (this.currentNativeLanguage === this.currentTargetLanguage) {
      window.app.showToast("Please select different languages", "warning")
      return
    }

    this.showLoading(true)

    try {
      const params = new URLSearchParams({
        native_language: this.currentNativeLanguage,
        target_language: this.currentTargetLanguage,
      })

      const movies = await window.app.apiCall(`/api/movies?${params}`)
      this.movies = movies
      this.filteredMovies = [...movies]
      this.renderMovies()
    } catch (error) {
      console.error("Failed to load movies:", error)
      window.app.showToast("Failed to load movies", "error")
    } finally {
      this.showLoading(false)
    }
  }

  filterMovies() {
    this.filteredMovies = this.movies.filter((movie) => {
      const matchesSearch =
        !this.currentSearchTerm || movie.title.toLowerCase().includes(this.currentSearchTerm.toLowerCase())

      const matchesLetter = !this.currentLetter || movie.title.charAt(0).toUpperCase() === this.currentLetter

      return matchesSearch && matchesLetter
    })

    this.renderMovies()
  }

  filterByLetter(letter) {
    // Update active state
    document.querySelectorAll(".alphabet-btn").forEach((btn) => {
      btn.classList.remove("active")
    })

    if (this.currentLetter === letter) {
      // Clicking same letter clears filter
      this.currentLetter = ""
    } else {
      this.currentLetter = letter
      event.target.classList.add("active")
    }

    this.filterMovies()
  }

  renderMovies() {
    const container = document.getElementById("moviesGrid")

    if (this.filteredMovies.length === 0) {
      container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <p class="text-muted">No movies found matching your criteria</p>
                </div>
            `
      return
    }

    const moviesHtml = this.filteredMovies
      .map(
        (movie) => `
            <div class="col-md-6 col-lg-4 col-xl-3 mb-4">
                <div class="movie-card card h-100" data-sub-link-id="${movie.sub_link_id}">
                    <div class="card-body">
                        <h6 class="card-title">${movie.title}</h6>
                        <p class="card-text text-muted small">
                            ${this.getLanguageName(this.currentNativeLanguage)} → 
                            ${this.getLanguageName(this.currentTargetLanguage)}
                        </p>
                    </div>
                </div>
            </div>
        `,
      )
      .join("")

    container.innerHTML = moviesHtml

    // Add click handlers
    container.querySelectorAll(".movie-card").forEach((card) => {
      card.addEventListener("click", () => {
        const subLinkId = card.dataset.subLinkId
        window.location.href = `/learning/${subLinkId}`
      })
    })
  }

  getLanguageName(languageId) {
    const language = this.languages.find((lang) => lang.id == languageId)
    return language ? language.display_name : "Unknown"
  }

  clearAllFilters() {
    this.currentSearchTerm = ""
    this.currentLetter = ""

    document.getElementById("movieSearch").value = ""
    document.querySelectorAll(".alphabet-btn").forEach((btn) => {
      btn.classList.remove("active")
    })

    this.filteredMovies = [...this.movies]
    this.renderMovies()
  }

  displayEmptyState() {
    const container = document.getElementById("moviesGrid")
    container.innerHTML = `
            <div class="col-12 text-center py-5">
                <p class="text-muted">Select your language pair to discover movies</p>
            </div>
        `
  }

  showLoading(show) {
    const loadingState = document.getElementById("loadingState")
    const moviesGrid = document.getElementById("moviesGrid")

    if (show) {
      loadingState.classList.remove("d-none")
      moviesGrid.classList.add("d-none")
    } else {
      loadingState.classList.add("d-none")
      moviesGrid.classList.remove("d-none")
    }
  }
}
