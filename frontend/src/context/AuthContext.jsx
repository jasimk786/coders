import React, { createContext, useContext, useEffect, useState } from 'react'
import axios from '../utils/axiosInstance'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const t = localStorage.getItem('token')
    if (t) {
      setToken(t)
      // fetch profile
      axios.get('/profile')
        .then(res => setUser(res.data.user))
        .catch(() => {
          setUser(null)
          setToken(null)
          localStorage.removeItem('token')
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    const res = await axios.post('/login', { email, password })
    const t = res.data.token
    localStorage.setItem('token', t)
    setToken(t)
    const profile = await axios.get('/profile')
    setUser(profile.data.user)
    return res
  }

  const signup = async (name, email, password) => {
    const res = await axios.post('/signup', { name, email, password })
    return res
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
    window.location.href = '/login'
  }

  const updateProfile = async (data) => {
    const res = await axios.put('/profile', data)
    setUser(res.data.user)
    return res
  }

  const value = { user, token, loading, login, signup, logout, updateProfile }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => useContext(AuthContext)
