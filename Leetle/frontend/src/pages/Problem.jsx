import React, { useEffect, useState, useRef } from 'react'
import CodeEditor from '../components/CodeEditor'
import Toast from '../components/Toast'
import '../styles/Problem.css'

export default function Problem() {
  const [problem, setProblem] = useState(null)
  const [code, setCode] = useState('# write your solution here')
  const [language, setLanguage] = useState('python')
  const [result, setResult] = useState(null)
  const [toasts, setToasts] = useState([])
  const [submitting, setSubmitting] = useState(false)
  const [loading, setLoading] = useState(true)
  const confettiRef = useRef(null)

  useEffect(() => {
    const fetchProblem = async () => {
      try {
        const response = await fetch('http://localhost:5001/problem')
        if (!response.ok) {
          throw new Error('Failed to fetch problem')
        }
        const problem = await response.json()
        setProblem(problem)
      } catch (error) {
        console.error('Error fetching problem:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchProblem()
  }, [])

  function handleSubmit() {
    setSubmitting(true)
    setResult(null)
    
    const simulatedMs = Math.floor(Math.random() * 2000) + 100
    setTimeout(() => {
      const passed = Math.random() > 0.35
      const entry = {
        id: Date.now(),
        user: 'DemoUser',
        language,
        runtime_ms: simulatedMs,
        passed,
        submitted_at: new Date().toISOString()
      }
      
      const all = JSON.parse(localStorage.getItem('leetle_submissions') || '[]')
      all.push(entry)
      localStorage.setItem('leetle_submissions', JSON.stringify(all))
      
      setResult(entry)
      setSubmitting(false)
      addToast(
        entry.passed ? 'Solution passed 🎉' : 'Solution failed — try again',
        entry.passed ? 'success' : 'error'
      )
      if (entry.passed) launchConfetti()
    }, 800 + Math.random() * 1200)
  }

  function addToast(message, type = 'info') {
    const id = Date.now() + Math.random()
    setToasts(t => [...t, { id, message, type }])
  }

  function removeToast(id) {
    setToasts(t => t.filter(x => x.id !== id))
  }

  function launchConfetti() {
    const c = confettiRef.current
    if (!c) return
    
    const colors = [
      'var(--green, #6aaa64)',
      'var(--yellow, #c9b458)',
      '#84CC16',
      '#06B6D4',
      '#7C3AED'
    ]
    
    for (let i = 0; i < 26; i++) {
      const el = document.createElement('span')
      el.className = 'confetti-piece'
      el.style.left = `${50 + (Math.random() * 160 - 80)}%`
      el.style.background = colors[Math.floor(Math.random() * colors.length)]
      c.appendChild(el)
      setTimeout(() => el.remove(), 2200)
    }
  }

  if (loading) {
    return <div className="problem-loading">Loading...</div>
  }

  if (!problem) {
    return <div className="problem-error">Error loading problem</div>
  }

  return (
    <div className="problem-container">
      <h1 className="problem-page-title">Today's Problem</h1>

      <div className="problem-grid">
        {/* Problem Description */}
        <div className="problem-description-card">
          <h2 className="problem-title">{problem.title}</h2>
          <p className={`problem-difficulty ${problem.difficulty.toLowerCase()}`}>
            Difficulty: {problem.difficulty}
          </p>
          <p className="problem-text">{problem.description}</p>

          <div className="problem-example">
            <h3 className="problem-example-title">Example Input:</h3>
            <pre className="problem-example-code">{problem.input_example}</pre>
          </div>

          <div className="problem-example">
            <h3 className="problem-example-title">Example Output:</h3>
            <pre className="problem-example-code">{problem.output_example}</pre>
          </div>
        </div>

        {/* Code Editor */}
        <div className="problem-editor-card">
          <label className="problem-label">Language</label>
          <select
            value={language}
            onChange={e => setLanguage(e.target.value)}
            className="problem-select"
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="cpp">C++</option>
          </select>

          <div className="problem-editor-header">
            <label className="problem-label">Code</label>
            <div className="problem-keyboard-hint">
              Tip: <span className="problem-kbd">Ctrl/⌘</span> +{' '}
              <span className="problem-kbd">Enter</span> to run
            </div>
          </div>

          <div className="problem-actions">
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="problem-btn-primary"
            >
              {submitting ? 'Running...' : 'Run (Ctrl/⌘+Enter)'}
            </button>
            <button
              onClick={() => {
                setCode('# write your solution here')
                setResult(null)
              }}
              className="problem-btn-ghost"
            >
              Reset
            </button>
            <button
              onClick={() => downloadCode(code, language)}
              className="problem-btn-ghost"
            >
              Download
            </button>
          </div>

          <div className="problem-editor-wrapper">
            <CodeEditor
              value={code}
              onChange={setCode}
              language={language}
              onRun={handleSubmit}
            />
          </div>

          {result && (
            <div className="problem-result">
              <p>
                Result:{' '}
                <strong
                  className={
                    result.passed
                      ? 'problem-result-passed'
                      : 'problem-result-failed'
                  }
                >
                  {result.passed ? 'Passed' : 'Failed'}
                </strong>
              </p>
              <p>Runtime: {result.runtime_ms} ms</p>
              <p>Language: {result.language}</p>
            </div>
          )}
        </div>
      </div>

      {/* Toast Notifications */}
      <div className="problem-toast-container">
        {toasts.map(t => (
          <Toast
            key={t.id}
            id={t.id}
            message={t.message}
            type={t.type}
            onClose={removeToast}
          />
        ))}
      </div>

      {/* Confetti Container */}
      <div ref={confettiRef} className="problem-confetti-container"></div>
    </div>
  )
}

function downloadCode(code, language) {
  const ext = language === 'python' ? 'py' : language === 'javascript' ? 'js' : 'cpp'
  const blob = new Blob([code], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `solution.${ext}`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}