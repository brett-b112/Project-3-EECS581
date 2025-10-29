import React, {useEffect, useState, useRef} from 'react'
import CodeEditor from '../components/CodeEditor'
import Toast from '../components/Toast'

function getTodayProblemIndex(list){
  const idx = (new Date()).toISOString().slice(0,10).split('-').join('')
  return parseInt(idx) % list.length
}

export default function Problem(){
  const [problem, setProblem] = useState(null)
  const [code, setCode] = useState('# write your solution here')
  const [language, setLanguage] = useState('python')
  const [result, setResult] = useState(null)
  const [toasts, setToasts] = useState([])
  const [submitting, setSubmitting] = useState(false)
  const confettiRef = useRef(null)

  useEffect(()=>{
    fetch('/mock/problems.json')
      .then(r=>r.json())
      .then(list=> setProblem(list[getTodayProblemIndex(list)]))
      .catch(()=> setProblem(null))
  }, [])

  function handleSubmit(){
    setSubmitting(true)
    setResult(null)
    // Simulate execution time and result
    const simulatedMs = Math.floor(Math.random()*2000) + 100
    setTimeout(()=>{
      const passed = Math.random() > 0.35
      const entry = {
        id: Date.now(),
        user: 'DemoUser',
        language,
        runtime_ms: simulatedMs,
        passed,
        submitted_at: new Date().toISOString()
      }
      // save to localStorage for leaderboard demo
      const all = JSON.parse(localStorage.getItem('leetle_submissions')||'[]')
      all.push(entry)
      localStorage.setItem('leetle_submissions', JSON.stringify(all))
      setResult(entry)
      setSubmitting(false)
      // show toast and confetti for pass
      addToast(entry.passed ? 'Solution passed 🎉' : 'Solution failed — try again', entry.passed ? 'success' : 'error')
      if(entry.passed) launchConfetti()
    }, 800 + Math.random()*1200)
  }

  function addToast(message, type='info'){
    const id = Date.now()+Math.random()
    setToasts(t=>[...t, {id, message, type}])
  }

  function removeToast(id){ setToasts(t=>t.filter(x=>x.id!==id)) }

  function launchConfetti(){
    const c = confettiRef.current
    if(!c) return
    for(let i=0;i<26;i++){
      const el = document.createElement('span')
      el.className = 'confetti-piece'
      el.style.left = `${50 + (Math.random()*160-80)}%`
      el.style.background = ['#F97316','#F59E0B','#84CC16','#06B6D4','#7C3AED'][Math.floor(Math.random()*5)]
      c.appendChild(el)
      setTimeout(()=> el.remove(), 2200)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2 bg-gray-200">Problem</h1>
      {problem ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="card">
            <h2 className="text-lg font-semibold">{problem.title}</h2>
            <p className="text-sm text-gray-600">Difficulty: {problem.difficulty}</p>
            <p className="mt-2 text-gray-800">{problem.description}</p>
          </div>
          <div className="editor-card">
            <label className="block text-sm font-medium text-gray-700">Language</label>
            <select value={language} onChange={e=>setLanguage(e.target.value)} className="mt-1 block w-full rounded border-gray-300">
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="cpp">C++</option>
            </select>

            <div className="flex items-center justify-between">
              <label className="block text-sm font-medium text-gray-700 mt-3">Code</label>
              <div className="text-sm text-gray-500 mt-3">Tip: <kbd className="px-1 py-0.5 bg-gray-100 rounded">Ctrl/⌘</kbd> + <kbd className="px-1 py-0.5 bg-gray-100 rounded">Enter</kbd> to run</div>
            </div>
            <div className="mt-2">
              <div className="flex items-center gap-2 mb-2">
                <button onClick={handleSubmit} disabled={submitting} className="btn-primary">{submitting ? 'Running...' : 'Run (Ctrl/⌘+Enter)'}</button>
                <button onClick={()=>{setCode('# write your solution here'); setResult(null)}} className="btn-ghost">Reset</button>
                <button onClick={()=> downloadCode(code, language)} className="btn-ghost">Download</button>
              </div>
              <CodeEditor value={code} onChange={setCode} language={language} onRun={handleSubmit} />
            </div>

            <div className="mt-3">
              <h4 className="text-sm font-medium">Sample Tests</h4>
              <div className="mt-2 grid grid-cols-1 gap-2">
                {getSampleTests().map((t, idx)=> (
                  <div key={idx} className="p-2 border rounded flex items-center justify-between bg-gray-50">
                    <div className="text-sm">
                      <div className="font-medium">Test #{idx+1}</div>
                      <div className="text-xs text-gray-600">Input: {t.input}</div>
                      <div className="text-xs text-gray-600">Expected: {t.output}</div>
                    </div>
                    <div className="text-sm font-mono text-gray-700">—</div>
                  </div>
                ))}
              </div>
            </div>

            {result && (
              <div className="mt-3 p-3 border rounded bg-white">
                <p>Result: <strong className={result.passed? 'text-green-600': 'text-red-600'}>{result.passed ? 'Passed' : 'Failed'}</strong></p>
                <p>Runtime: {result.runtime_ms} ms</p>
                <p>Language: {result.language}</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        <p className="text-gray-500">Loading problem...</p>
      )}
      <div className="fixed top-4 right-4 flex flex-col gap-2 z-50">
        {toasts.map(t => (
          <Toast key={t.id} id={t.id} message={t.message} type={t.type} onClose={removeToast} />
        ))}
      </div>

      <div ref={confettiRef} className="pointer-events-none fixed inset-0 z-40"></div>
    </div>
  )
}

function getSampleTests(){
  return [
    {input: '[2,7,11,15], target=9', output: '[0,1]'},
    {input: '[3,2,4], target=6', output: '[1,2]'}
  ]
}

function downloadCode(code, language){
  const ext = language === 'python' ? 'py' : language === 'javascript' ? 'js' : 'cpp'
  const blob = new Blob([code], {type: 'text/plain'})
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `solution.${ext}`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
