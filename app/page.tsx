"use client"

import { useState, useEffect } from "react"

// Mock data for demonstration
const mockLanguages = [
  { id: 1, display_name: "English", code: "en" },
  { id: 2, display_name: "Spanish", code: "es" },
  { id: 3, display_name: "French", code: "fr" },
  { id: 4, display_name: "German", code: "de" },
  { id: 5, display_name: "Italian", code: "it" },
]

const mockMovies = [
  { sub_link_id: 1, title: "The Shawshank Redemption" },
  { sub_link_id: 2, title: "The Godfather" },
  { sub_link_id: 3, title: "Pulp Fiction" },
  { sub_link_id: 4, title: "The Dark Knight" },
  { sub_link_id: 5, title: "Forrest Gump" },
  { sub_link_id: 6, title: "Inception" },
  { sub_link_id: 7, title: "The Matrix" },
  { sub_link_id: 8, title: "Goodfellas" },
]

export default function Page() {
  const [nativeLanguage, setNativeLanguage] = useState("")
  const [targetLanguage, setTargetLanguage] = useState("")
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedLetter, setSelectedLetter] = useState("")
  const [filteredMovies, setFilteredMovies] = useState(mockMovies)

  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("")

  useEffect(() => {
    let filtered = mockMovies

    if (searchTerm) {
      filtered = filtered.filter((movie) => movie.title.toLowerCase().includes(searchTerm.toLowerCase()))
    }

    if (selectedLetter) {
      filtered = filtered.filter((movie) => movie.title.charAt(0).toUpperCase() === selectedLetter)
    }

    setFilteredMovies(filtered)
  }, [searchTerm, selectedLetter])

  const handleLetterFilter = (letter: string) => {
    setSelectedLetter(selectedLetter === letter ? "" : letter)
  }

  const clearFilters = () => {
    setSearchTerm("")
    setSelectedLetter("")
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600">SubLearning</h1>
            </div>
            <div className="flex items-center space-x-4">
              <a href="#" className="text-gray-600 hover:text-gray-900">
                Dashboard
              </a>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">Login</button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Language Selector */}
        <div className="bg-gray-50 rounded-xl p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Choose Your Language Pair</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">I speak (Native Language)</label>
              <select
                value={nativeLanguage}
                onChange={(e) => setNativeLanguage(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select your native language...</option>
                {mockLanguages.map((lang) => (
                  <option key={lang.id} value={lang.id}>
                    {lang.display_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">I want to learn (Target Language)</label>
              <select
                value={targetLanguage}
                onChange={(e) => setTargetLanguage(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select target language...</option>
                {mockLanguages.map((lang) => (
                  <option key={lang.id} value={lang.id}>
                    {lang.display_name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search for movies..."
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
            </div>
          </div>
          <button
            onClick={clearFilters}
            className="px-6 py-2 border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50"
          >
            Clear Filters
          </button>
        </div>

        {/* Alphabetical Filter */}
        <div className="flex flex-wrap gap-2 mb-6 justify-center">
          {alphabet.map((letter) => (
            <button
              key={letter}
              onClick={() => handleLetterFilter(letter)}
              className={`w-10 h-10 border rounded-md flex items-center justify-center font-medium transition-colors ${
                selectedLetter === letter
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white text-gray-600 border-gray-300 hover:bg-blue-600 hover:text-white hover:border-blue-600"
              }`}
            >
              {letter}
            </button>
          ))}
        </div>

        {/* Movies Grid */}
        {nativeLanguage && targetLanguage && nativeLanguage !== targetLanguage ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredMovies.map((movie) => (
              <div
                key={movie.sub_link_id}
                className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg hover:border-blue-600 transition-all cursor-pointer transform hover:-translate-y-1"
              >
                <h3 className="font-semibold text-gray-800 mb-2">{movie.title}</h3>
                <p className="text-sm text-gray-500">
                  {mockLanguages.find((l) => l.id.toString() === nativeLanguage)?.display_name} →{" "}
                  {mockLanguages.find((l) => l.id.toString() === targetLanguage)?.display_name}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">
              {!nativeLanguage || !targetLanguage
                ? "Select your language pair to discover movies"
                : nativeLanguage === targetLanguage
                  ? "Please select different languages"
                  : "Loading movies..."}
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-100 border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div>
              <h3 className="font-semibold text-gray-800">SubLearning</h3>
              <p className="text-sm text-gray-600">Learn languages through movie subtitles</p>
            </div>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a href="#" className="text-gray-600 hover:text-gray-900">
                About
              </a>
              <a href="#" className="text-gray-600 hover:text-gray-900">
                Help
              </a>
              <a href="#" className="text-gray-600 hover:text-gray-900">
                Contact
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
