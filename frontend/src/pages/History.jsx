import React, { useEffect, useState } from 'react'
import axios from '../utils/axiosInstance'
import Loader from '../components/Loader'

export default function History() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { fetchHistory() }, [])

  const fetchHistory = async () => {
    setLoading(true)
    try {
      const res = await axios.get('/history')
      setHistory(res.data.history)
    } catch (err) {
      console.error(err)
    } finally { setLoading(false) }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">History</h1>
      {loading && <Loader />}
      <div className="grid gap-3">
        {history.map(h => (
          <div key={h._id} className="p-4 bg-white dark:bg-gray-800 rounded shadow flex gap-4 items-start">
            <div className="w-24 h-24 bg-gray-100 dark:bg-gray-700 rounded overflow-hidden flex items-center justify-center text-xs text-gray-500">
              {h.imageUrl ? <img src={h.imageUrl} alt="thumb" className="object-cover w-full h-full" /> : <span>Text</span>}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <div className="font-medium">{h.prediction} <span className="text-sm text-gray-500">({Math.round(h.confidence*100)}%)</span></div>
                <div className="text-sm text-gray-400">{new Date(h.createdAt).toLocaleString()}</div>
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-300 mt-2">{h.text ? h.text : 'Image analysis'}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
