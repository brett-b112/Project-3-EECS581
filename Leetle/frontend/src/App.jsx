import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Nav from './components/Nav'
import Home from './pages/Home'
import Problem from './pages/Problem'
import UserProfile from './pages/UserProfile'
import Login from './components/Login'
import Signup from './components/Signup'
import { AuthProvider } from './components/AuthContext'

export default function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-50">
        <Nav />
        <main className="p-4 max-w-4xl mx-auto">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/problem" element={<Problem />} />
            <Route path="/user-profile" element={<UserProfile />} />
          </Routes>
        </main>
      </div>
    </AuthProvider>
  )
}
