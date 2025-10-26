import React, { useEffect, useState } from 'react'
import axios from '../utils/axiosInstance'
import Loader from '../components/Loader'

export default function Dashboard() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [recent, setRecent] = useState([])
  const [wordCount, setWordCount] = useState(0)

  useEffect(() => { fetchRecent() }, [])
  useEffect(() => { setWordCount(text.trim().split(/\s+/).filter(w => w).length) }, [text])

  const fetchRecent = async () => {
    try {
      const res = await axios.get('/history')
      setRecent(res.data.history.slice(0,5))
    } catch (err) {
      console.error(err)
    }
  }

  const analyzeText = async () => {
    if (!text.trim()) return
    setLoading(true)
    setResult(null)
    try {
      const res = await axios.post('/analyzeText', { text })
      setResult(res.data)
      fetchRecent()
    } catch (err) {
      console.error(err)
    } finally { setLoading(false) }
  }

  const clearText = () => {
    setText('')
    setResult(null)
  }

  const getResultColor = (prediction) => {
    return prediction === 'Real' ? 'text-green-600' : 'text-red-600'
  }

  const getResultBg = (prediction) => {
    return prediction === 'Real' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Hero Section */}
      <div className="text-center py-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
          AI Fake News Detector
        </h1>
        <p className="text-gray-600 dark:text-gray-300 text-lg">Powered by Fine-tuned BERT Model</p>
      </div>

      {/* Main Analysis Card */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold flex items-center gap-3">
            <span className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
              🔍
            </span>
            Text Analysis
          </h2>
          <div className="text-sm text-gray-500">
            {wordCount} words
          </div>
        </div>
        
        <div className="space-y-4">
          <textarea 
            value={text} 
            onChange={e=>setText(e.target.value)}
            placeholder="Paste your news article or text here to check if it's real or fake..."
            className="w-full p-4 h-48 border-2 border-gray-200 dark:border-gray-600 rounded-xl bg-gray-50 dark:bg-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all resize-none"
          />
          
          <div className="flex gap-3">
            <button 
              onClick={analyzeText} 
              disabled={!text.trim() || loading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
            >
              {loading ? 'Analyzing...' : 'Analyze Text'}
            </button>
            <button 
              onClick={clearText}
              className="px-6 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-all"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-center space-x-3">
            <Loader />
            <span className="text-lg">AI is analyzing your text...</span>
          </div>
        </div>
      )}

      {/* Result Card */}
      {result && (
        <div className={`rounded-2xl shadow-xl p-8 border-2 ${getResultBg(result.prediction)}`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-2xl font-bold">Analysis Result</h3>
            <div className="text-sm text-gray-500">ID: {result.historyId?.slice(-8)}</div>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <div className="text-sm text-gray-600 mb-2">Prediction</div>
              <div className={`text-4xl font-bold ${getResultColor(result.prediction)} flex items-center gap-3`}>
                <span>{result.prediction === 'Real' ? '✅' : '❌'}</span>
                {result.prediction}
              </div>
            </div>
            
            <div>
              <div className="text-sm text-gray-600 mb-2">Confidence Score</div>
              <div className="text-3xl font-bold text-gray-800 dark:text-gray-200">
                {Math.round(result.confidence)}%
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 mt-2">
                <div 
                  className={`h-3 rounded-full ${result.prediction === 'Real' ? 'bg-green-500' : 'bg-red-500'}`}
                  style={{width: `${result.confidence}%`}}
                ></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Analyses */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-700">
        <h3 className="text-2xl font-semibold mb-6 flex items-center gap-3">
          <span className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
            📊
          </span>
          Recent Analyses
        </h3>
        
        <div className="space-y-4">
          {recent.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No analyses yet. Start by analyzing some text above!
            </div>
          ) : (
            recent.map(r => (
              <div key={r._id} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-xl hover:shadow-md transition-all">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className={`text-2xl ${r.prediction === 'Real' ? '✅' : '❌'}`}></span>
                    <div>
                      <div className={`font-semibold ${getResultColor(r.prediction)}`}>
                        {r.prediction}
                      </div>
                      <div className="text-sm text-gray-500">
                        {Math.round(r.confidence)}% confidence
                      </div>
                    </div>
                  </div>
                  <div className="text-sm text-gray-400">
                    {new Date(r.createdAt).toLocaleDateString()}
                  </div>
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300 line-clamp-2">
                  {r.text?.slice(0, 120)}...
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}