import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Nav from './components/Nav'
import Home from './pages/Home'
import Problem from './pages/Problem'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* <Nav /> */}
      <main className="p-4 max-w-4xl mx-auto">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/problem" element={<Problem />} />
        </Routes>
      </main>
    </div>
  )
}
