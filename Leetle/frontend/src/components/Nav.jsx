import React, {useState} from 'react'
import { Link } from 'react-router-dom'

export default function Nav(){
  const [open, setOpen] = useState(false)
  return (
    <header className="bg-[#6aaa64] text-white shadow">
      <div className="max-w-4xl mx-auto flex items-center justify-between p-4">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c1.657 0 3-1.343 3-3S13.657 2 12 2 9 3.343 9 5s1.343 3 3 3zM6 20v-2a4 4 0 014-4h4a4 4 0 014 4v2" /></svg>
          </div>
          <span className="text-lg font-semibold">Leetle</span>
        </Link>

        <nav className="hidden md:flex items-center gap-4">
          <Link to="/" className="text-sm text-white/90 hover:text-white">Home</Link>
          <Link to="/problem" className="text-sm text-white/90 hover:text-white">Problem</Link>
          <Link to="/user-profile" className="text-sm text-white/90 hover:text-white">User Profile</Link>
        </nav>

        <div className="md:hidden">
          <button onClick={()=>setOpen(!open)} className="p-2 rounded bg-white/20">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={open ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'} /></svg>
          </button>
        </div>
      </div>

      {open && (
        <div className="md:hidden bg-white/5">
          <div className="max-w-4xl mx-auto p-3 flex flex-col gap-2">
            <Link to="/" className="text-white">Home</Link>
            <Link to="/problem" className="text-white">Problem</Link>
            <Link to="/user-profile" className="text-white">User Profile</Link>
          </div>
        </div>
      )}
    </header>
  )
}
