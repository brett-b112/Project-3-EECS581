/*
 * File: Home.jsx
 * Description: This file contains the Home component, which serves as the landing page for the application.
 * It displays the daily coding challenge, introduction to Leetle, and practice/learn info cards.
 * Authors: Daniel Neugent, Brett Balquist, Tej Gumaste, Jay Patel, Arnav Jain
 */
import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import '../styles/Home.css'

/*
 * Function: Home
 * Description: Renders the home page, fetches the daily problem title/description, and provides navigation.
 * Inputs: None
 * Outputs: JSX Element (Home Page UI)
 * Contributors: Daniel Neugent, Brett Balquist, Tej Gumaste, Jay Patel, Arnav Jain
 */
export default function Home() {
  const [problem, setProblem] = useState(null)
  
  useEffect(() => {
    fetch('http://localhost:5001/problem')
      .then(r => r.json())
      .then(problem => {
        setProblem(problem)
      })
      .catch(() => setProblem(null))
  }, [])
  
  return (
    <div className="home-container">
      {/* Header Section */}
      <section className="home-header">
        <h1 className="home-title">Leetle</h1>
        <p className="home-description">
          A daily coding challenge inspired by Wordle. Solve a new Leet Code Inspired problem every day to build your coding skills. 
        </p>
        
        <Link to="/problem" className="home-play-button">
          Play Today
        </Link>
      </section>

      {/* Today's Problem Card */}
      {problem && (
        <section className="problem-card">
          <h3 className="problem-card-label">Today's Problem</h3>
          <div>
            <div className="problem-title">{problem.title}</div>
            <div className={`problem-difficulty ${problem.difficulty.toLowerCase()}`}>
              {problem.difficulty}
            </div>
            <p className="problem-description">{problem.description}</p>
          </div>
        </section>
      )}

      {/* Info Cards */}
      <section className="info-cards-grid">
        <div className="info-card">
          <h4 className="info-card-title">Practice</h4>
          <p className="info-card-description">
            Solve the daily problem and build streaks.
          </p>
        </div>
        
        <div className="info-card">
          <h4 className="info-card-title">Learn</h4>
          <p className="info-card-description">
            See example solutions and improve over time.
          </p>
        </div>
      </section>
    </div>
  )
}