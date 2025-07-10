import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import './App.css'

// Components
import Dashboard from './components/Dashboard'
import DocumentTester from './components/DocumentTester'
import MLModelManager from './components/MLModelManager'
import DatabaseManager from './components/DatabaseManager'
import SystemHealth from './components/SystemHealth'
import APITester from './components/APITester'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <nav className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <h1 className="text-xl font-bold text-gray-900">PDF Pipeline Admin</h1>
                </div>
                <div className="flex items-center space-x-8">
                  <Link to="/" className="text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium">
                    Dashboard
                  </Link>
                  <Link to="/documents" className="text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium">
                    Document Tester
                  </Link>
                  <Link to="/ml-models" className="text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium">
                    ML Models
                  </Link>
                  <Link to="/database" className="text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium">
                    Database
                  </Link>
                  <Link to="/system" className="text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium">
                    System Health
                  </Link>
                  <Link to="/api" className="text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium">
                    API Tester
                  </Link>
                </div>
              </div>
            </div>
          </nav>

          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/documents" element={<DocumentTester />} />
              <Route path="/ml-models" element={<MLModelManager />} />
              <Route path="/database" element={<DatabaseManager />} />
              <Route path="/system" element={<SystemHealth />} />
              <Route path="/api" element={<APITester />} />
            </Routes>
          </main>
        </div>
        <Toaster />
      </Router>
    </QueryClientProvider>
  )
}

export default App