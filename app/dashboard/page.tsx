"use client"

import { useState } from "react"
import { BookOpen, Play, TrendingUp, Clock, Star, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"

// Mock data for demonstration
const mockUserData = {
  name: "John Doe",
  nativeLanguage: "English",
  targetLanguage: "Spanish",
  totalMoviesCompleted: 12,
  totalHoursLearned: 45,
  currentStreak: 7,
  averageAccuracy: 85,
}

const mockContinueSessions = [
  {
    id: 1,
    movieTitle: "The Shawshank Redemption",
    progress: 75,
    lastPosition: "Chapter 3, Line 142",
    timeLeft: "25 minutes",
  },
  {
    id: 2,
    movieTitle: "Pulp Fiction",
    progress: 40,
    lastPosition: "Chapter 1, Line 67",
    timeLeft: "45 minutes",
  },
]

const mockRecentActivity = [
  {
    id: 1,
    action: "Completed",
    movieTitle: "The Godfather",
    timeAgo: "2 days ago",
    score: 92,
  },
  {
    id: 2,
    action: "Learning Session",
    movieTitle: "Inception",
    timeAgo: "1 week ago",
    duration: "30 minutes",
  },
  {
    id: 3,
    action: "New Movie Started",
    movieTitle: "The Dark Knight",
    timeAgo: "1 week ago",
  },
]

export default function DashboardPage() {
  const [selectedTimeframe, setSelectedTimeframe] = useState("week")

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <BookOpen className="h-8 w-8 text-primary" />
              <h1 className="text-2xl font-bold text-primary">SubLearning</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost">Browse Movies</Button>
              <Button variant="ghost">Settings</Button>
              <Button variant="outline">Logout</Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Welcome back, {mockUserData.name}! 👋
          </h1>
          <p className="text-muted-foreground">
            Continue your {mockUserData.targetLanguage} learning journey through movie subtitles
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Movies Completed
              </CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockUserData.totalMoviesCompleted}</div>
              <p className="text-xs text-muted-foreground">
                +2 from last month
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Hours Learned
              </CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockUserData.totalHoursLearned}h</div>
              <p className="text-xs text-muted-foreground">
                +8h from last month
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Current Streak
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockUserData.currentStreak} days</div>
              <p className="text-xs text-muted-foreground">
                Keep it up! 🔥
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Avg. Accuracy
              </CardTitle>
              <Star className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockUserData.averageAccuracy}%</div>
              <p className="text-xs text-muted-foreground">
                +5% from last month
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Continue Learning */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold">Continue Learning</h2>
              <Button variant="outline" size="sm">
                View All
              </Button>
            </div>
            
            <div className="space-y-4">
              {mockContinueSessions.map((session) => (
                <Card key={session.id} className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="font-semibold">{session.movieTitle}</h3>
                        <p className="text-sm text-muted-foreground">
                          {session.lastPosition}
                        </p>
                      </div>
                      <Button size="sm">
                        <Play className="h-4 w-4 mr-2" />
                        Continue
                      </Button>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Progress</span>
                        <span>{session.progress}%</span>
                      </div>
                      <Progress value={session.progress} className="w-full" />
                      <p className="text-xs text-muted-foreground">
                        Estimated time left: {session.timeLeft}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))}
              
              <Card className="border-dashed">
                <CardContent className="p-6 text-center">
                  <BookOpen className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="font-semibold mb-2">Start a new movie</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Discover new content to continue your learning
                  </p>
                  <Button>
                    Browse Movies
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold">Recent Activity</h2>
              <div className="flex space-x-2">
                {["week", "month", "all"].map((timeframe) => (
                  <Button
                    key={timeframe}
                    variant={selectedTimeframe === timeframe ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedTimeframe(timeframe)}
                  >
                    {timeframe === "all" ? "All Time" : `This ${timeframe}`}
                  </Button>
                ))}
              </div>
            </div>

            <Card>
              <CardContent className="p-6">
                <div className="space-y-4">
                  {mockRecentActivity.map((activity) => (
                    <div key={activity.id} className="flex items-center justify-between py-2">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <Badge variant="secondary" className="text-xs">
                            {activity.action}
                          </Badge>
                          <span className="font-medium">{activity.movieTitle}</span>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {activity.timeAgo}
                          {activity.score && ` • Score: ${activity.score}%`}
                          {activity.duration && ` • Duration: ${activity.duration}`}
                        </p>
                      </div>
                      <Button variant="ghost" size="sm">
                        <ArrowRight className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Actions</CardTitle>
                <CardDescription>
                  Common tasks to enhance your learning
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-start">
                  <BookOpen className="h-4 w-4 mr-2" />
                  Browse New Movies
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  View Progress Report
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Star className="h-4 w-4 mr-2" />
                  Review Bookmarks
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}