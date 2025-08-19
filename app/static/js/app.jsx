// Main application entry point
// Global utilities and shared functionality

class App {
  constructor() {
    this.init()
  }

  init() {
    // Global event listeners
    this.setupGlobalErrorHandling()
    this.setupNavigationHighlighting()
  }

  setupGlobalErrorHandling() {
    window.addEventListener("unhandledrejection", (event) => {
      console.error("Unhandled promise rejection:", event.reason)
      this.showToast("An error occurred. Please try again.", "error")
    })
  }

  setupNavigationHighlighting() {
    const currentPath = window.location.pathname
    const navLinks = document.querySelectorAll(".navbar-nav .nav-link")

    navLinks.forEach((link) => {
      if (link.getAttribute("href") === currentPath) {
        link.classList.add("active")
      }
    })
  }

  // Utility method for showing toast notifications
  showToast(message, type = "info") {
    // Create toast element
    const toast = document.createElement("div")
    toast.className = `alert alert-${type === "error" ? "danger" : type} alert-dismissible fade show position-fixed`
    toast.style.cssText = "top: 20px; right: 20px; z-index: 9999; min-width: 300px;"
    toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `

    document.body.appendChild(toast)

    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (toast.parentNode) {
        toast.remove()
      }
    }, 5000)
  }

  // Utility method for API calls
  async apiCall(endpoint, options = {}) {
    const defaultOptions = {
      headers: {
        "Content-Type": "application/json",
      },
    }

    const config = { ...defaultOptions, ...options }

    try {
      const response = await fetch(endpoint, config)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error("API call failed:", error)
      throw error
    }
  }
}

// Initialize app when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.app = new App()
})

// Export for use in modules
export { App }
