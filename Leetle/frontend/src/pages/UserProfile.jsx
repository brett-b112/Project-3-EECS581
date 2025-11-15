import React, { useEffect, useState } from 'react';
import { useAuth } from '../components/AuthContext';
import { useNavigate } from 'react-router-dom';
import FeedbackModal from '../components/FeedbackModal';

const UserProfile = () => {
  const { user, makeAuthenticatedRequest } = useAuth();
  const navigate = useNavigate();
  const [userStats, setUserStats] = useState(null);
  const [achievements, setAchievements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    fetchUserProfile();
  }, [user, navigate]);

  const fetchUserProfile = async () => {
    setLoading(true);
    try {
      // Fetch user stats
      const statsResponse = await makeAuthenticatedRequest(
        `http://localhost:5001/api/user/stats/${user.id}`
      );
      const statsData = await statsResponse.json();

      // Fetch available achievements
      const achievementsResponse = await makeAuthenticatedRequest(
        'http://localhost:5001/api/achievements'
      );
      const achievementsData = await achievementsResponse.json();

      setUserStats(statsData);
      setAchievements(achievementsData.achievements || []);
    } catch (error) {
      console.error('Error fetching user profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStreakIcon = (streak) => {
    if (streak >= 7) return '🔥';
    if (streak >= 3) return '⚡';
    return '✨';
  };

  const getSuccessRateColor = (rate) => {
    if (rate >= 80) return 'text-green-600';
    if (rate >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (!user) {
    return <div className="animate-pulse">Loading...</div>;
  }

  if (loading) {
    return (
      <div className="container mx-auto mt-10">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse">
            <div className="h-32 bg-gray-200 rounded-lg mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-24 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
            <div className="h-64 bg-gray-200 rounded-lg"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto mt-6 p-6 max-w-4xl">
      {/* Profile Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-3xl font-bold mr-6">
            {user.email.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">{user.email.split('@')[0]}</h1>
            <p className="text-gray-600">{user.email}</p>
            <p className="text-sm text-gray-500">
              Member since {new Date(user.created_at || Date.now()).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      {userStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Current Streak */}
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="flex items-center justify-center mb-2">
              <span className="text-3xl mr-2">{getStreakIcon(userStats.stats.current_streak)}</span>
              <div className="text-3xl font-bold text-blue-600">{userStats.stats.current_streak}</div>
            </div>
            <div className="text-sm text-gray-600">Current Streak</div>
            <div className="text-xs text-gray-500 mt-1">
              Best: {userStats.stats.longest_streak} days
            </div>
          </div>

          {/* Problems Solved */}
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">{userStats.stats.total_solutions}</div>
            <div className="text-sm text-gray-600">Problems Solved</div>
            <div className="text-xs text-gray-500 mt-1">
              {userStats.stats.problems_attempted} attempted
            </div>
          </div>

          {/* Success Rate */}
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className={`text-3xl font-bold mb-2 ${getSuccessRateColor(userStats.stats.success_rate)}`}>
              {userStats.stats.success_rate}%
            </div>
            <div className="text-sm text-gray-600">Success Rate</div>
            <div className="text-xs text-gray-500 mt-1">
              {userStats.stats.total_correct}/{userStats.stats.total_attempts} correct
            </div>
          </div>

          {/* Favorite Language */}
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {userStats.stats.favorite_language === 'python' ? '🐍' :
               userStats.stats.favorite_language === 'javascript' ? '🟨' :
               userStats.stats.favorite_language === 'java' ? '☕' : '💻'}
            </div>
            <div className="text-sm text-gray-600 capitalize">{userStats.stats.favorite_language}</div>
            <div className="text-xs text-gray-500 mt-1">Favorite Language</div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Achievements */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <span className="mr-2">🏆</span>
              Achievements
            </h2>
          </div>
          <div className="p-6">
            {achievements.length === 0 ? (
              <p className="text-gray-500">No achievements available</p>
            ) : (
              <div className="space-y-3">
                {achievements.map((achievement) => (
                  <div
                    key={achievement.id}
                    className={`p-4 rounded-lg border transition-colors ${
                      achievement.earned
                        ? 'border-green-200 bg-green-50'
                        : 'border-gray-200 bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center">
                      <div className={`text-2xl mr-3 ${achievement.earned ? 'grayscale-0' : 'grayscale'}`}>
                        {achievement.icon === 'trophy' ? '🏆' :
                         achievement.icon === 'star' ? '⭐' :
                         achievement.icon === 'fire' ? '🔥' :
                         achievement.icon === 'flame' ? '🔥' :
                         achievement.icon === 'target' ? '🎯' :
                         achievement.icon === 'medal' ? '🥇' : '🏅'}
                      </div>
                      <div className="flex-1">
                        <div className={`font-medium ${achievement.earned ? 'text-green-800' : 'text-gray-600'}`}>
                          {achievement.name}
                        </div>
                        <div className="text-sm text-gray-600">{achievement.description}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-gray-900">+{achievement.points}</div>
                        <div className={`text-xs ${achievement.earned ? 'text-green-600' : 'text-gray-400'}`}>
                          {achievement.earned ? 'Earned!' : 'Locked'}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Language Statistics */}
        {userStats && userStats.language_stats && (
          <div className="bg-white rounded-lg shadow-md">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <span className="mr-2">📊</span>
                Language Stats
              </h2>
            </div>
            <div className="p-6">
              {Object.keys(userStats.language_stats).length === 0 ? (
                <p className="text-gray-500">No submissions yet</p>
              ) : (
                <div className="space-y-4">
                  {Object.entries(userStats.language_stats).map(([lang, stats]) => (
                    <div key={lang} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="text-lg mr-3">
                          {lang === 'python' ? '🐍' : lang === 'javascript' ? '🟨' : lang === 'java' ? '☕' : '💻'}
                        </div>
                        <div>
                          <div className="font-medium capitalize">{lang}</div>
                          <div className="text-sm text-gray-600">
                            {stats.correct}/{stats.attempts} correct
                          </div>
                        </div>
                      </div>
                      <div className={`text-sm font-medium ${getSuccessRateColor((stats.correct/stats.attempts)*100)}`}>
                        {((stats.correct/stats.attempts)*100).toFixed(1)}%
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Feedback Button */}
      <div className="mt-8 text-center">
        <button
          onClick={() => setShowFeedbackModal(true)}
          className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors shadow-md"
        >
          📝 Share Feedback
        </button>
        <p className="text-sm text-gray-500 mt-2">
          Help us improve Leetle by sharing your thoughts
        </p>
      </div>

      {/* Feedback Modal */}
      <FeedbackModal
        isOpen={showFeedbackModal}
        onClose={() => setShowFeedbackModal(false)}
      />
    </div>
  );
};

export default UserProfile;
