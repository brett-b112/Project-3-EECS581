/*
 * File: Leaderboard.jsx
 * Description: This file contains the Leaderboard component, which displays user rankings, streaks, and success rates.
 * It supports filtering by time period (all-time, weekly, daily) and highlights the current user's rank.
 * Authors: Daniel Neugent, Brett Balquist, Tej Gumaste, Jay Patel, Arnav Jain
 */
import React, { useEffect, useState } from 'react'
import { useAuth } from '../components/AuthContext'

/*
 * Function: Leaderboard
 * Description: Main component for the leaderboard. Fetches and displays ranking data.
 * Inputs: None
 * Outputs: JSX Element (Leaderboard UI)
 * Contributors: Daniel Neugent, Brett Balquist, Tej Gumaste, Jay Patel, Arnav Jain
 */
export default function Leaderboard() {
  const { user, makeAuthenticatedRequest } = useAuth()
  const [leaderboard, setLeaderboard] = useState([])
  const [currentUserRank, setCurrentUserRank] = useState(null)
  const [period, setPeriod] = useState('all-time')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchLeaderboard()
  }, [period])

  /*
   * Function: fetchLeaderboard
   * Description: Fetches leaderboard data from the API based on the selected time period.
   * Inputs: None (Uses 'period' state)
   * Outputs: Updates state (leaderboard, currentUserRank, loading)
   * Contributors: Tej Gumaste, Daniel Neugent
   */
  const fetchLeaderboard = async () => {
    setLoading(true)
    try {
      const response = await makeAuthenticatedRequest(
        `http://localhost:5001/api/leaderboard?period=${period}&limit=50`
      )
      const data = await response.json()
      setLeaderboard(data.leaderboard || [])
      setCurrentUserRank(data.current_user_rank)
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
      setLeaderboard([])
    } finally {
      setLoading(false)
    }
  }
  /*
   * Function: getDifficultyColor
   * Description: Determines the color styling for success rate badges.
   * Inputs: successRate (Number)
   * Outputs: String (Tailwind CSS classes)
   * Contributors: Brett Balquist
   */
  const getDifficultyColor = (successRate) => {
    if (successRate >= 80) return 'text-green-600 bg-green-50 border-green-200'
    if (successRate >= 60) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  /*
   * Function: getRankBadge
   * Description: Generates a badge UI element for the top 3 ranks or a standard badge for others.
   * Inputs: rank (Number), isCurrentUser (Boolean)
   * Outputs: JSX Element (Span with styles)
   * Contributors: Arnav Jain, Jay Patel
   */
  const getRankBadge = (rank, isCurrentUser) => {
    let badgeClass = 'px-2 py-1 rounded-full text-xs font-medium '
    let badgeText = rank.toString()

    if (rank === 1) {
      badgeClass += 'bg-yellow-100 text-yellow-800 border border-yellow-300'
      badgeText = '🥇 1st'
    } else if (rank === 2) {
      badgeClass += 'bg-gray-100 text-gray-800 border border-gray-300'
      badgeText = '🥈 2nd'
    } else if (rank === 3) {
      badgeClass += 'bg-orange-100 text-orange-800 border border-orange-300'
      badgeText = '🥉 3rd'
    } else {
      badgeClass += 'bg-blue-100 text-blue-800 border border-blue-300'
    }

    if (isCurrentUser) {
      badgeClass += ' ring-2 ring-blue-400'
    }

    return <span className={badgeClass}>{badgeText}</span>
  }

  /*
   * Function: getStreakIcon
   * Description: Returns an emoji icon representing the user's current streak intensity.
   * Inputs: streak (Number)
   * Outputs: String (Emoji character)
   * Contributors: Daniel Neugent, Tej Gumaste
   */
  const getStreakIcon = (streak) => {
    if (streak >= 7) return '🔥'
    if (streak >= 3) return '⚡'
    return '✨'
  }

  if (!user) {
    return (
      <div className="container mx-auto mt-10 p-6">
        <div className="text-center">
          <p className="text-gray-600">Please log in to view the leaderboard.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto mt-6 p-6 max-w-4xl">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Leaderboard</h1>

      {/* Period selector */}
      <div className="mb-6">
        <div className="flex space-x-2">
          {[
            { key: 'all-time', label: 'All Time' },
            { key: 'weekly', label: 'This Week' },
            { key: 'daily', label: 'Today' }
          ].map((option) => (
            <button
              key={option.key}
              onClick={() => setPeriod(option.key)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                period === option.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Current user position highlight */}
      {currentUserRank && currentUserRank > 10 && (
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-lg">📍</span>
              <div>
                <p className="font-medium text-blue-900">Your Position</p>
                <p className="text-blue-700">You're ranked #{currentUserRank}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loading state */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : leaderboard.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No leaderboard data available for this period.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {/* Header */}
          <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
            <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-500">
              <div className="col-span-2">Rank</div>
              <div className="col-span-3">User</div>
              <div className="col-span-2 text-center">Streak</div>
              <div className="col-span-2 text-center">Solutions</div>
              <div className="col-span-3 text-center">Success Rate</div>
            </div>
          </div>

          {/* Leaderboard rows */}
          <div className="divide-y divide-gray-200">
            {leaderboard.map((entry, index) => {
              const isCurrentUser = entry.id === user.id
              return (
                <div
                  key={entry.id}
                  className={`px-6 py-4 grid grid-cols-12 gap-4 items-center hover:bg-gray-50 transition-colors ${
                    isCurrentUser ? 'bg-blue-50' : ''
                  }`}
                >
                  {/* Rank */}
                  <div className="col-span-2">
                    {getRankBadge(entry.rank, isCurrentUser)}
                  </div>

                  {/* User */}
                  <div className="col-span-3">
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                        isCurrentUser ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-700'
                      }`}>
                        {entry.email.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className={`text-sm font-medium ${isCurrentUser ? 'text-blue-900' : 'text-gray-900'}`}>
                          {entry.email.split('@')[0]}
                          {isCurrentUser && <span className="ml-1 text-blue-600">(You)</span>}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Streak */}
                  <div className="col-span-2 text-center">
                    <div className="flex items-center justify-center space-x-1">
                      <span className="text-lg">{getStreakIcon(entry.current_streak)}</span>
                      <span className="font-semibold text-gray-900">{entry.current_streak}</span>
                    </div>
                    {entry.longest_streak > entry.current_streak && (
                      <div className="text-xs text-gray-500">
                        Best: {entry.longest_streak}
                      </div>
                    )}
                  </div>

                  {/* Solutions */}
                  <div className="col-span-2 text-center">
                    <span className="font-semibold text-gray-900">{entry.total_solutions}</span>
                  </div>

                  {/* Success Rate */}
                  <div className="col-span-3 text-center">
                    <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium border ${getDifficultyColor(entry.success_rate)}`}>
                      {entry.success_rate.toFixed(1)}%
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Footer info */}
      <div className="mt-8 text-sm text-gray-500 text-center">
        <p>
          Rankings are based on current streak length plus success rate.
          Keep solving daily to climb the leaderboard!
        </p>
      </div>
    </div>
  )
}
