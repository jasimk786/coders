import React from 'react'
import { Link } from 'react-router-dom'

export default function About() {
  return (
    <div className="max-w-4xl mx-auto py-16">
      <div className="grid md:grid-cols-2 gap-8 items-center">
        <div>
          <h1 className="text-4xl font-bold mb-4">AI Fake News Detector</h1>
          <p className="text-gray-600 dark:text-gray-300 mb-4">Analyze news articles text using an AI model to detect fake or real news. Login to try the analyzer and view your past analyses.</p>
          <div className="flex gap-3">
            <Link to="/login" className="px-4 py-2 bg-indigo-600 text-white rounded">Login</Link>
            <Link to="/signup" className="px-4 py-2 border rounded">Signup</Link>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded shadow">
          <h3 className="font-semibold mb-2">Welcome Our Fake new Detector </h3>
          {/* <ol className="list-decimal list-inside text-gray-600 dark:text-gray-300">
            <li>Submit text or upload image of a news article.</li>
            <li>Backend AI model analyzes content and returns prediction.</li>
            <li>Results saved to your history.</li>
          </ol> */}
        </div>
      </div>
    </div>
  )
}
