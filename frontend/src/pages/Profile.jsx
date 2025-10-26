import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'

export default function Profile() {
  const { user, updateProfile, logout } = useAuth()
  const [name, setName] = useState(user?.name || '')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const save = async () => {
    setLoading(true)
    try {
      await updateProfile({ name, ...(password? { password } : {}) })
      alert('Profile updated')
      setPassword('')
    } catch (err) {
      alert('Update failed')
    } finally { setLoading(false) }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Profile</h1>
      <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
        <label className="block mb-2">Name</label>
        <input value={name} onChange={e=>setName(e.target.value)} className="p-2 w-full mb-3 bg-gray-50 dark:bg-gray-900 rounded" />
        <label className="block mb-2">Email</label>
        <input value={user?.email} disabled className="p-2 w-full mb-3 bg-gray-100 dark:bg-gray-700 rounded" />
        <label className="block mb-2">New Password</label>
        <input type="password" value={password} onChange={e=>setPassword(e.target.value)} className="p-2 w-full mb-3 bg-gray-50 dark:bg-gray-900 rounded" />
        <div className="flex gap-2">
          <button onClick={save} disabled={loading} className="px-4 py-2 bg-indigo-600 text-white rounded">Save</button>
          <button onClick={() => { logout() }} className="px-4 py-2 bg-red-500 text-white rounded">Logout</button>
        </div>
      </div>
    </div>
  )
}
