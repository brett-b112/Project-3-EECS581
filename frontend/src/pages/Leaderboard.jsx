import React, {useEffect, useState} from 'react'

export default function Leaderboard(){
  const [entries, setEntries] = useState([])

  useEffect(()=>{
    const all = JSON.parse(localStorage.getItem('leetle_submissions')||'[]')
    // take best (lowest) runtime per user
    const map = {}
    for(const e of all){
      const key = e.user
      if(!map[key] || e.runtime_ms < map[key].runtime_ms){
        map[key] = e
      }
    }
    const list = Object.values(map).sort((a,b)=>a.runtime_ms - b.runtime_ms)
    setEntries(list)
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Leaderboard (Demo)</h1>
      <div className="bg-white p-4 rounded shadow">
        {entries.length === 0 ? (
          <p className="text-gray-500">No submissions yet (try submitting a demo solution on the Problem page).</p>
        ) : (
          <ol className="space-y-3">
            {entries.map((e, i)=> (
              <li key={e.id} className="flex items-center justify-between gap-4 p-2 rounded hover:bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold ${i===0? 'bg-yellow-500': i===1? 'bg-gray-400': i===2? 'bg-amber-400':'bg-indigo-500'}`}>
                    {e.user.slice(0,2).toUpperCase()}
                  </div>
                  <div>
                    <div className="font-medium">{i+1}. {e.user}</div>
                    <div className="text-sm text-gray-500">{e.language} • {new Date(e.submitted_at).toLocaleString()}</div>
                  </div>
                </div>
                <div className="font-mono text-indigo-700">{e.runtime_ms} ms</div>
              </li>
            ))}
          </ol>
        )}
      </div>
    </div>
  )
}
