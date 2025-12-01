/*
  File Overview: This file defines a responsive navigation bar component for the application.
  It displays navigation links conditionally based on authentication state, includes mobile menu
  functionality, and supports user logout handling. Authors: Daniel Neugent, Brett Balquist,
  Tej Gumaste, Jay Patel, Arnav Jain
*/

import React, {useState} from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from './AuthContext'

/*
  Component Function: Nav
  Description: Renders the main site navigation bar with desktop and mobile layouts.
  Inputs: None (uses internal state and authentication context)
  Outputs: UI elements and user interface interactions
  Contributors: Daniel Neugent, Jay Patel, Arnav Jain
*/
export default function Nav(){
  const [open, setOpen] = useState(false)
  const { user, logout } = useAuth()

  /*
    Function: handleLogout
    Description: Logs out the current user and closes the mobile navigation menu.
    Inputs: None
    Outputs: None (performs side-effects via context and state updates)
    Contributors: Brett Balquist, Tej Gumaste
  */
  const handleLogout = () => {
    logout()
    setOpen(false)
  }

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
          {user ? (
            <>
              <Link to="/problem" className="text-sm text-white/90 hover:text-white">Problem</Link>
              <Link to="/leaderboard" className="text-sm text-white/90 hover:text-white">Leaderboard</Link>
              <Link to="/user-profile" className="text-sm text-white/90 hover:text-white">Profile</Link>
              {user.role === 'admin' && (
                <Link to="/admin" className="text-sm text-white/90 hover:text-white bg-white/10 px-3 py-1 rounded">
                  Admin
                </Link>
              )}
              <button
                onClick={handleLogout}
                className="text-sm text-white/90 hover:text-white bg-white/10 px-3 py-1 rounded"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm text-white/90 hover:text-white">Login</Link>
              <Link to="/signup" className="text-sm text-white bg-[#5a944f] hover:bg-[#4a7a3f] px-3 py-1 rounded">Sign Up</Link>
            </>
          )}
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
            <Link to="/" className="text-white" onClick={() => setOpen(false)}>Home</Link>
            {user ? (
              <>
                <Link to="/problem" className="text-white" onClick={() => setOpen(false)}>Problem</Link>
                <Link to="/user-profile" className="text-white" onClick={() => setOpen(false)}>Profile</Link>
                <button
                  onClick={handleLogout}
                  className="text-left text-white bg-white/10 px-3 py-2 rounded w-full"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-white" onClick={() => setOpen(false)}>Login</Link>
                <Link to="signup" className="text-white bg-[#5a944f] px-3 py-2 rounded block text-center" onClick={() => setOpen(false)}>Sign Up</Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  )
}
