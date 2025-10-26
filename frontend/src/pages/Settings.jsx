import React, { useState, useEffect } from 'react'
import axios from '../utils/axiosInstance'
import { useAuth } from '../context/AuthContext'

export default function Settings() {
  const { user } = useAuth()
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark')
  const [saving, setSaving] = useState(false)

  useEffect(() => { document.documentElement.classList.toggle('dark', theme === 'dark') }, [theme])

  const save = async () => {
    setSaving(true)
    try {
      await axios.put('/settings', { theme })
      localStorage.setItem('theme', theme)
      alert('Settings saved')
    } catch (err) {
      console.error(err)
      alert('Failed to save settings')
    } finally { setSaving(false) }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Settings</h1>
      <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
        <label className="flex items-center justify-between">
          <span>Theme</span>
          <select value={theme} onChange={e=>setTheme(e.target.value)} className="p-2 bg-gray-50 dark:bg-gray-900 rounded">
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </label>
        <div className="mt-4">
          <button onClick={save} disabled={saving} className="px-4 py-2 bg-indigo-600 text-white rounded">{saving? 'Saving...':'Save Settings'}</button>
        </div>
      </div>
    </div>
  )
}
