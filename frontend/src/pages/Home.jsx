import React, {useEffect, useState} from 'react'
import { Link } from 'react-router-dom'

export default function Home(){
  const [problem, setProblem] = useState(null)

  useEffect(()=>{
    fetch('/mock/problems.json')
      .then(r=>r.json())
      .then(list=>{
        const idx = (new Date()).toISOString().slice(0,10).split('-').join('')
        const i = parseInt(idx) % list.length
        setProblem(list[i])
      })
      .catch(()=> setProblem(null))
  }, [])

  return (
    <div>
      <section className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-lg mb-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 max-w-4xl mx-auto">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900">Leetle — Daily Coding Challenge</h1>
            <p className="mt-2 text-gray-700">A playful daily coding challenge inspired by Wordle, built as a demo with React + Tailwind. Try today's problem, compete on the leaderboard, and have fun learning.</p>
            <div className="mt-4 flex gap-3">
              <Link to="/problem" className="px-4 py-2 bg-indigo-600 text-white rounded shadow">Try Today's Problem</Link>
              <Link to="/leaderboard" className="px-4 py-2 border rounded">View Leaderboard</Link>
            </div>
          </div>
          <div className="hidden md:block bg-white p-4 rounded shadow w-80">
            <h3 className="font-semibold">Today's Problem</h3>
            {problem ? (
              <div className="mt-2">
                <div className="font-medium">{problem.title}</div>
                <div className="text-sm text-gray-500">{problem.difficulty}</div>
                <p className="mt-2 text-sm text-gray-700 line-clamp-3">{problem.description}</p>
              </div>
            ) : (
              <p className="text-gray-500 mt-2">Loading...</p>
            )}
          </div>
        </div>
      </section>

      <section className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded shadow">
          <h4 className="font-semibold">Practice</h4>
          <p className="text-sm text-gray-600 mt-2">Solve the daily problem and build streaks.</p>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <h4 className="font-semibold">Compete</h4>
          <p className="text-sm text-gray-600 mt-2">Compare runtimes on the leaderboard.</p>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <h4 className="font-semibold">Learn</h4>
          <p className="text-sm text-gray-600 mt-2">See example solutions and improve over time.</p>
        </div>
      </section>
    </div>
  )
}
