"use client"

import { useState, useEffect } from "react"
import { Search, BookOpen, Languages, Play } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"

// Mock data for demonstration
const mockLanguages = [
  { id: 1, display_name: "English", code: "en" },
  { id: 2, display_name: "Spanish", code: "es" },
  { id: 3, display_name: "French", code: "fr" },
  { id: 4, display_name: "German", code: "de" },
  { id: 5, display_name: "Italian", code: "it" },
  { id: 6, display_name: "Portuguese", code: "pt" },
  { id: 7, display_name: "Chinese", code: "zh" },
  { id: 8, display_name: "Japanese", code: "ja" },
]

const mockMovies = [
  { sub_link_id: 1, title: "The Shawshank Redemption", year: 1994, genre: "Drama" },
  { sub_link_id: 2, title: "The Godfather", year: 1972, genre: "Crime" },
  { sub_link_id: 3, title: "Pulp Fiction", year: 1994, genre: "Crime" },
  { sub_link_id: 4, title: "The Dark Knight", year: 2008, genre: "Action" },
  { sub_link_id: 5, title: "Forrest Gump", year: 1994, genre: "Drama" },
  { sub_link_id: 6, title: "Inception", year: 2010, genre: "Sci-Fi" },
  { sub_link_id: 7, title: "The Matrix", year: 1999, genre: "Sci-Fi" },
  { sub_link_id: 8, title: "Goodfellas", year: 1990, genre: "Crime" },
  { sub_link_id: 9, title: "Schindler's List", year: 1993, genre: "Drama" },
  { sub_link_id: 10, title: "The Lord of the Rings", year: 2001, genre: "Fantasy" },
]

export default function LandingPage() {
  const [nativeLanguage, setNativeLanguage] = useState("")
  const [targetLanguage, setTargetLanguage] = useState("")
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedLetter, setSelectedLetter] = useState("")
  const [filteredMovies, setFilteredMovies] = useState(mockMovies)

  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("")

  useEffect(() => {
    let filtered = mockMovies

    if (searchTerm) {
      filtered = filtered.filter((movie) => 
        movie.title.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (selectedLetter) {
      filtered = filtered.filter((movie) => 
        movie.title.charAt(0).toUpperCase() === selectedLetter
      )
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

  const canShowMovies = nativeLanguage && targetLanguage && nativeLanguage !== targetLanguage

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <BookOpen className="h-8 w-8 text-primary" />
              <h1 className="text-2xl font-bold text-primary">SubLearning</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" className="text-muted-foreground">
                Dashboard
              </Button>
              <Button>Login</Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto text-center">
          <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-6xl mb-6">
            Learn Languages Through
            <span className="text-primary"> Movie Subtitles</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Interactive language learning with authentic movie content. 
            Practice reading comprehension through dual-language subtitles in a professional, 
            distraction-free environment.
          </p>
          <div className="flex flex-wrap justify-center gap-4 mb-8">
            <Badge variant="secondary" className="text-sm px-3 py-1">
              <Languages className="h-4 w-4 mr-1" />
              Multiple Languages
            </Badge>
            <Badge variant="secondary" className="text-sm px-3 py-1">
              <Play className="h-4 w-4 mr-1" />
              Interactive Learning
            </Badge>
            <Badge variant="secondary" className="text-sm px-3 py-1">
              <BookOpen className="h-4 w-4 mr-1" />
              Progress Tracking
            </Badge>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        {/* Language Selector */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Languages className="h-5 w-5" />
              Choose Your Language Pair
            </CardTitle>
            <CardDescription>
              Select your native language and the language you want to learn
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="native-language">I speak (Native Language)</Label>
                <Select value={nativeLanguage} onValueChange={setNativeLanguage}>
                  <SelectTrigger id="native-language">
                    <SelectValue placeholder="Select your native language..." />
                  </SelectTrigger>
                  <SelectContent>
                    {mockLanguages.map((lang) => (
                      <SelectItem key={lang.id} value={lang.id.toString()}>
                        {lang.display_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="target-language">I want to learn (Target Language)</Label>
                <Select value={targetLanguage} onValueChange={setTargetLanguage}>
                  <SelectTrigger id="target-language">
                    <SelectValue placeholder="Select target language..." />
                  </SelectTrigger>
                  <SelectContent>
                    {mockLanguages.map((lang) => (
                      <SelectItem key={lang.id} value={lang.id.toString()}>
                        {lang.display_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Search and Filters */}
        {canShowMovies && (
          <>
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                  <Input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search for movies..."
                    className="pl-10"
                  />
                </div>
              </div>
              <Button variant="outline" onClick={clearFilters}>
                Clear Filters
              </Button>
            </div>

            {/* Alphabetical Filter */}
            <div className="flex flex-wrap gap-2 mb-8 justify-center">
              {alphabet.map((letter) => (
                <Button
                  key={letter}
                  variant={selectedLetter === letter ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleLetterFilter(letter)}
                  className="w-10 h-10 p-0"
                >
                  {letter}
                </Button>
              ))}
            </div>

            {/* Movies Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredMovies.map((movie) => (
                <Card 
                  key={movie.sub_link_id}
                  className="cursor-pointer transition-all hover:shadow-lg hover:scale-105 group"
                >
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg leading-tight group-hover:text-primary transition-colors">
                      {movie.title}
                    </CardTitle>
                    <CardDescription>
                      {movie.year} • {movie.genre}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="flex items-center justify-between">
                      <Badge variant="secondary" className="text-xs">
                        {mockLanguages.find((l) => l.id.toString() === nativeLanguage)?.display_name} → {" "}
                        {mockLanguages.find((l) => l.id.toString() === targetLanguage)?.display_name}
                      </Badge>
                      <Button size="sm" variant="ghost" className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <Play className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {filteredMovies.length === 0 && (
              <Card className="p-12 text-center">
                <CardContent>
                  <p className="text-muted-foreground">
                    No movies found matching your search criteria.
                  </p>
                  <Button variant="outline" onClick={clearFilters} className="mt-4">
                    Clear Filters
                  </Button>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {/* Language Selection Required */}
        {!canShowMovies && (
          <Card className="p-12 text-center">
            <CardContent>
              <Languages className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground text-lg">
                {!nativeLanguage || !targetLanguage
                  ? "Select your language pair above to discover movies"
                  : nativeLanguage === targetLanguage
                    ? "Please select different languages to continue"
                    : "Loading movies..."}
              </p>
            </CardContent>
          </Card>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-center md:text-left">
              <div className="flex items-center justify-center md:justify-start space-x-2 mb-2">
                <BookOpen className="h-5 w-5 text-primary" />
                <h3 className="font-semibold text-foreground">SubLearning</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Learn languages through movie subtitles
              </p>
            </div>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <Button variant="ghost" size="sm">About</Button>
              <Button variant="ghost" size="sm">Help</Button>
              <Button variant="ghost" size="sm">Contact</Button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}