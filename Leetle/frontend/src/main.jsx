/* Application Entry Point
  Initializes the React DOM root, configures global routing via BrowserRouter, and renders the main App component.
  Authors: Daniel Neugent, Brett Balquist, Tej Gumaste, Jay Patel, and Arnav Jain
*/
import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App'
import './styles/index.css'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/*" element={<App />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
)
