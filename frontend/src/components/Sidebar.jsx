import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { FaTachometerAlt, FaHistory, FaUser, FaCog, FaSignOutAlt } from 'react-icons/fa'
import { useAuth } from '../context/AuthContext'

const links = [
  { to: '/dashboard', icon: <FaTachometerAlt />, label: 'Dashboard' },
  { to: '/history', icon: <FaHistory />, label: 'History' },
  { to: '/profile', icon: <FaUser />, label: 'Profile' },
  { to: '/settings', icon: <FaCog />, label: 'Settings' },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  if (!user) return null

  return (
    <aside className="w-64 hidden md:block bg-white dark:bg-gray-800 h-screen p-4 border-r dark:border-gray-700">
      <div className="mb-6">
        <div className="font-bold text-lg">Welcome, {user.name}</div>
        <div className="text-sm text-gray-500">{user.email}</div>
      </div>
      <nav className="flex flex-col gap-2">
        {links.map(l => (
          <NavLink key={l.to} to={l.to} className={({isActive}) => `flex items-center gap-3 px-3 py-2 rounded ${isActive? 'bg-indigo-600 text-white' : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'}`}>
            <span className="w-5">{l.icon}</span>
            <span>{l.label}</span>
          </NavLink>
        ))}
        <button onClick={() => { logout(); navigate('/login') }} className="flex items-center gap-3 px-3 py-2 rounded text-red-600 hover:bg-red-50 dark:hover:bg-red-900">
          <FaSignOutAlt /> <span>Logout</span>
        </button>
      </nav>
    </aside>
  )
}
