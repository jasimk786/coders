import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Signup() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const { signup } = useAuth()
  const navigate = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await signup(name, email, password)
      navigate('/login')
    } catch (err) {
      setError(err.response?.data?.message || 'Signup failed')
    } finally { setLoading(false) }
  }

  return (
    <div className="max-w-md mx-auto py-16">
      <div className="bg-white dark:bg-gray-800 p-6 rounded shadow">
        <h2 className="text-2xl font-bold mb-4">Signup</h2>
        {error && <div className="text-red-600 mb-2">{error}</div>}
        <form onSubmit={submit} className="flex flex-col gap-3">
          <input className="p-2 border rounded bg-gray-50 dark:bg-gray-900" placeholder="Name" value={name} onChange={e=>setName(e.target.value)} />
          <input className="p-2 border rounded bg-gray-50 dark:bg-gray-900" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
          <input type="password" className="p-2 border rounded bg-gray-50 dark:bg-gray-900" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
          <button type="submit" disabled={loading} className="px-4 py-2 bg-indigo-600 text-white rounded">{loading? 'Signing...':'Signup'}</button>
        </form>
        <div className="mt-4 text-sm">Already have an account? <Link to="/login" className="text-indigo-600">Login</Link></div>
      </div>
    </div>
  )
}
