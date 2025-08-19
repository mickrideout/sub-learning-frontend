export class SubtitlePlayer {
  constructor(subLinkId) {
    this.subLinkId = subLinkId
    this.alignments = []
    this.currentIndex = 0
    this.totalAlignments = 0
    this.isPlaying = false
    this.playbackSpeed = 1
    this.autoPlayInterval = null

    this.init()
  }

  async init() {
    this.bindEvents()
    await this.loadSubtitles()
    this.updateDisplay()
  }

  bindEvents() {
    // Playback controls
    document.getElementById("playPauseBtn").addEventListener("click", () => {
      this.togglePlayPause()
    })

    document.getElementById("nextBtn").addEventListener("click", () => {
      this.nextAlignment()
    })

    document.getElementById("prevBtn").addEventListener("click", () => {
      this.previousAlignment()
    })

    // Speed control
    document.getElementById("speedControl").addEventListener("change", (e) => {
      this.playbackSpeed = Number.parseFloat(e.target.value)
      if (this.isPlaying) {
        this.restartAutoPlay()
      }
    })

    // Bookmark button
    document.getElementById("bookmarkBtn").addEventListener("click", () => {
      this.createBookmark()
    })

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return

      switch (e.code) {
        case "Space":
          e.preventDefault()
          this.togglePlayPause()
          break
        case "ArrowRight":
          e.preventDefault()
          this.nextAlignment()
          break
        case "ArrowLeft":
          e.preventDefault()
          this.previousAlignment()
          break
      }
    })
  }

  async loadSubtitles() {
    try {
      const data = await window.app.apiCall(`/api/subtitles/${this.subLinkId}`)
      this.alignments = data.alignments
      this.totalAlignments = data.total_count
      this.currentIndex = data.current_index || 0

      // Update movie title if available
      if (data.movie_title) {
        document.getElementById("movieTitle").textContent = data.movie_title
      }
    } catch (error) {
      console.error("Failed to load subtitles:", error)
      window.app.showToast("Failed to load subtitles", "error")
    }
  }

  updateDisplay() {
    if (this.alignments.length === 0) return

    const currentAlignment = this.alignments[this.currentIndex]
    if (!currentAlignment) return

    // Update subtitle content
    const nativeContent = currentAlignment.source_lines.map((line) => `<p>${line.content}</p>`).join("")

    const targetContent = currentAlignment.target_lines.map((line) => `<p>${line.content}</p>`).join("")

    document.getElementById("nativeSubtitle").innerHTML = nativeContent
    document.getElementById("targetSubtitle").innerHTML = targetContent

    // Update progress
    const progress = ((this.currentIndex + 1) / this.totalAlignments) * 100
    document.getElementById("progressBar").style.width = `${progress}%`
    document.getElementById("progressText").textContent = `${Math.round(progress)}%`

    // Update button states
    document.getElementById("prevBtn").disabled = this.currentIndex === 0
    document.getElementById("nextBtn").disabled = this.currentIndex >= this.alignments.length - 1

    // Save progress
    this.saveProgress()
  }

  togglePlayPause() {
    if (this.isPlaying) {
      this.pause()
    } else {
      this.play()
    }
  }

  play() {
    this.isPlaying = true
    this.updatePlayPauseButton()
    this.startAutoPlay()
  }

  pause() {
    this.isPlaying = false
    this.updatePlayPauseButton()
    this.stopAutoPlay()
  }

  startAutoPlay() {
    this.stopAutoPlay() // Clear any existing interval

    const interval = 3000 / this.playbackSpeed // Base 3 seconds per alignment
    this.autoPlayInterval = setInterval(() => {
      if (this.currentIndex < this.alignments.length - 1) {
        this.nextAlignment()
      } else {
        this.pause() // Auto-pause at end
      }
    }, interval)
  }

  stopAutoPlay() {
    if (this.autoPlayInterval) {
      clearInterval(this.autoPlayInterval)
      this.autoPlayInterval = null
    }
  }

  restartAutoPlay() {
    if (this.isPlaying) {
      this.stopAutoPlay()
      this.startAutoPlay()
    }
  }

  nextAlignment() {
    if (this.currentIndex < this.alignments.length - 1) {
      this.currentIndex++
      this.updateDisplay()
    }
  }

  previousAlignment() {
    if (this.currentIndex > 0) {
      this.currentIndex--
      this.updateDisplay()
    }
  }

  updatePlayPauseButton() {
    const playIcon = document.getElementById("playIcon")
    const pauseIcon = document.getElementById("pauseIcon")

    if (this.isPlaying) {
      playIcon.classList.add("d-none")
      pauseIcon.classList.remove("d-none")
    } else {
      playIcon.classList.remove("d-none")
      pauseIcon.classList.add("d-none")
    }
  }

  async saveProgress() {
    try {
      await window.app.apiCall(`/api/progress/${this.subLinkId}`, {
        method: "PUT",
        body: JSON.stringify({
          current_alignment_index: this.currentIndex,
          total_alignments_completed: this.currentIndex + 1,
        }),
      })
    } catch (error) {
      console.error("Failed to save progress:", error)
    }
  }

  async createBookmark() {
    try {
      const currentAlignment = this.alignments[this.currentIndex]
      if (!currentAlignment) return

      await window.app.apiCall("/api/bookmarks", {
        method: "POST",
        body: JSON.stringify({
          sub_link_id: this.subLinkId,
          alignment_index: this.currentIndex,
          note: `Bookmarked at alignment ${this.currentIndex + 1}`,
        }),
      })

      window.app.showToast("Bookmark created successfully", "success")
    } catch (error) {
      console.error("Failed to create bookmark:", error)
      window.app.showToast("Failed to create bookmark", "error")
    }
  }
}
