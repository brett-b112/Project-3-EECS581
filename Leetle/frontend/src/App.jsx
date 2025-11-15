import React, { Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import Nav from './components/Nav'
import Login from './components/Login'
import Signup from './components/Signup'
import { AuthProvider } from './components/AuthContext'

// Lazy load pages for performance
const Home = React.lazy(() => import('./pages/Home'))
const Problem = React.lazy(() => import('./pages/Problem'))
const UserProfile = React.lazy(() => import('./pages/UserProfile'))
const Leaderboard = React.lazy(() => import('./pages/Leaderboard'))
const AdminDashboard = React.lazy(() => import('./pages/AdminDashboard'))

// Loading component
const PageLoader = () => (
  <div className="flex justify-center items-center min-h-64">
    <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
  </div>
)

export default function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-50">
        <Nav />
        <main className="p-4 max-w-6xl mx-auto">
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/problem" element={<Problem />} />
              <Route path="/user-profile" element={<UserProfile />} />
              <Route path="/leaderboard" element={<Leaderboard />} />
              <Route path="/admin" element={<AdminDashboard />} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </AuthProvider>
  )
}
