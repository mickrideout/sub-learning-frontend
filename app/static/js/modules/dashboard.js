export class Dashboard {
  constructor() {
    this.userStats = {}
    this.lastMovie = null

    this.init()
  }

  async init() {
    this.bindEvents()
    await this.loadDashboardData()
  }

  bindEvents() {
    // Continue learning button
    document.getElementById("continueBtn").addEventListener("click", () => {
      if (this.lastMovie) {
        window.location.href = `/learning/${this.lastMovie.sub_link_id}`
      }
    })

    // View bookmarks button
    document.getElementById("viewBookmarks").addEventListener("click", () => {
      // This would navigate to a bookmarks page
      window.app.showToast("Bookmarks feature coming soon!", "info")
    })
  }

  async loadDashboardData() {
    try {
      // Load user statistics
      await this.loadUserStats()

      // Load last movie progress
      await this.loadLastMovie()
    } catch (error) {
      console.error("Failed to load dashboard data:", error)
      window.app.showToast("Failed to load dashboard data", "error")
    }
  }

  async loadUserStats() {
    try {
      const stats = await window.app.apiCall("/api/user/stats")
      this.userStats = stats
      this.updateStatsDisplay()
    } catch (error) {
      console.error("Failed to load user stats:", error)
      // Set default values
      this.userStats = {
        movies_completed: 0,
        hours_learned: 0,
        current_streak: 0,
      }
      this.updateStatsDisplay()
    }
  }

  async loadLastMovie() {
    try {
      const lastMovie = await window.app.apiCall("/api/user/last-movie")
      this.lastMovie = lastMovie
      this.updateContinueCard()
    } catch (error) {
      console.error("Failed to load last movie:", error)
      this.updateContinueCard(null)
    }
  }

  updateStatsDisplay() {
    document.getElementById("moviesCompleted").textContent = this.userStats.movies_completed || 0
    document.getElementById("hoursLearned").textContent = Math.round(this.userStats.hours_learned || 0)
    document.getElementById("currentStreak").textContent = this.userStats.current_streak || 0
  }

  updateContinueCard() {
    const continueBtn = document.getElementById("continueBtn")
    const lastMovieInfo = document.getElementById("lastMovieInfo")
    const progressBar = document.getElementById("lastMovieProgress")

    if (this.lastMovie) {
      const progress = (this.lastMovie.current_alignment_index / this.lastMovie.total_alignments) * 100

      lastMovieInfo.textContent = `Continue watching "${this.lastMovie.title}" - ${Math.round(progress)}% complete`
      progressBar.style.width = `${progress}%`
      continueBtn.disabled = false
    } else {
      lastMovieInfo.textContent = "No recent movies found. Start learning by browsing our catalog!"
      progressBar.style.width = "0%"
      continueBtn.disabled = true
      continueBtn.textContent = "Browse Movies"
      continueBtn.addEventListener("click", () => {
        window.location.href = "/movies"
      })
    }
  }
}
