import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import ThemeToggle from './ThemeToggle'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/" className="font-bold text-lg">AI Fake News</Link>
        </div>
        <div className="flex items-center gap-4">
          <ThemeToggle />
          {user ? (
            <div className="flex items-center gap-3">
              <span className="text-sm">{user.name}</span>
              <button onClick={() => { logout(); navigate('/login') }} className="text-sm px-3 py-1 bg-red-500 text-white rounded">Logout</button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link to="/login" className="text-sm px-3 py-1 bg-indigo-600 text-white rounded">Login</Link>
              <Link to="/signup" className="text-sm px-3 py-1 border rounded">Signup</Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}
