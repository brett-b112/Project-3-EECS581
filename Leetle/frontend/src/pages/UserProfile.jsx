import React, { useEffect, useState } from 'react';
import { useAuth } from '../components/AuthContext';
import { useNavigate } from 'react-router-dom';

const UserProfile = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalSubmissions: 0,
    successfulSubmissions: 0,
    favoriteLanguage: 'Python'
  });

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    // In a real app, you'd fetch user stats from the API
    // For now, we'll show placeholder stats
    setStats({
      totalSubmissions: 15,
      successfulSubmissions: 8,
      favoriteLanguage: 'Python'
    });
  }, [user, navigate]);

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto mt-10">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center mb-6">
          <div className="w-16 h-16 bg-[#6aaa64] rounded-full flex items-center justify-center text-white text-2xl font-bold mr-4">
            {user.email.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{user.email.split('@')[0]}</h2>
            <p className="text-gray-600">{user.email}</p>
            <p className="text-sm text-gray-500">Member since {new Date(user.created_at || Date.now()).toLocaleDateString()}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-[#6aaa64]">{stats.totalSubmissions}</div>
            <div className="text-sm text-gray-600">Total Submissions</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-[#6aaa64]">{stats.successfulSubmissions}</div>
            <div className="text-sm text-gray-600">Successful Solutions</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-[#6aaa64]">{stats.favoriteLanguage}</div>
            <div className="text-sm text-gray-600">Favorite Language</div>
          </div>
        </div>

        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">About Me</h3>
          <p className="text-gray-700">
            Hello! I'm a passionate coder who loves solving algorithmic problems and building
            applications. I enjoy tackling challenging problems and learning new technologies.
            Welcome to my coding journey!
          </p>
        </div>

        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Recent Activity</h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between py-2 border-b border-gray-100">
              <span className="text-gray-700">Solved "Two Sum" problem</span>
              <span className="text-sm text-gray-500">2 days ago</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-gray-100">
              <span className="text-gray-700">Joined Leetle platform</span>
              <span className="text-sm text-gray-500">1 week ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
