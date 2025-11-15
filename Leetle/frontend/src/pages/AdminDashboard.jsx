import React, { useEffect, useState } from 'react'
import { useAuth } from '../components/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function AdminDashboard() {
  const { user, makeAuthenticatedRequest } = useAuth()
  const navigate = useNavigate()
  const [problems, setProblems] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingProblem, setEditingProblem] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    difficulty: 'Easy',
    input_example: '',
    output_example: '',
    test_cases: []
  })

  useEffect(() => {
    if (!user) {
      navigate('/login')
      return
    }

    if (user.role !== 'admin') {
      navigate('/')
      return
    }

    fetchData()
  }, [user, navigate])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [problemsRes, analyticsRes] = await Promise.all([
        makeAuthenticatedRequest('http://localhost:5001/api/admin/problems'),
        makeAuthenticatedRequest('http://localhost:5001/api/admin/analytics')
      ])

      const problemsData = await problemsRes.json()
      const analyticsData = await analyticsRes.json()

      setProblems(problemsData.problems || [])
      setAnalytics(analyticsData)
    } catch (error) {
      console.error('Error fetching admin data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateProblem = async (e) => {
    e.preventDefault()

    try {
      let testCases = []
      try {
        testCases = JSON.parse(formData.test_cases)
      } catch (err) {
        alert('Invalid JSON format for test cases')
        return
      }

      const response = await makeAuthenticatedRequest('http://localhost:5001/api/admin/problems', {
        method: 'POST',
        body: JSON.stringify({
          ...formData,
          test_cases: testCases
        })
      })

      if (response.ok) {
        alert('Problem created successfully!')
        setShowCreateModal(false)
        setFormData({
          title: '',
          description: '',
          difficulty: 'Easy',
          input_example: '',
          output_example: '',
          test_cases: []
        })
        fetchData()
      } else {
        alert('Failed to create problem')
      }
    } catch (error) {
      console.error('Error creating problem:', error)
      alert('Error creating problem')
    }
  }

  const handleDeleteProblem = async (problemId) => {
    if (!confirm('Are you sure you want to delete this problem?')) return

    try {
      const response = await makeAuthenticatedRequest(`http://localhost:5001/api/admin/problems/${problemId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        alert('Problem deleted successfully!')
        fetchData()
      } else {
        alert('Failed to delete problem')
      }
    } catch (error) {
      console.error('Error deleting problem:', error)
      alert('Error deleting problem')
    }
  }

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      difficulty: 'Easy',
      input_example: '',
      output_example: '',
      test_cases: []
    })
    setEditingProblem(null)
    setShowCreateModal(false)
  }

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Easy': return 'text-green-600 bg-green-50'
      case 'Medium': return 'text-yellow-600 bg-yellow-50'
      case 'Hard': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  if (!user || user.role !== 'admin') {
    return <div>Access denied</div>
  }

  return (
    <div className="container mx-auto mt-6 p-6 max-w-6xl">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Create Problem
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <>
          {/* Analytics Overview */}
          {analytics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-2xl font-bold text-blue-600">{analytics.overview.total_users}</div>
                <div className="text-sm text-gray-600">Total Users</div>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-2xl font-bold text-green-600">{analytics.overview.total_problems}</div>
                <div className="text-sm text-gray-600">Total Problems</div>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-2xl font-bold text-purple-600">{analytics.overview.total_submissions}</div>
                <div className="text-sm text-gray-600">Total Submissions</div>
              </div>
              <div className={`bg-white rounded-lg shadow p-6 ${analytics.overview.overall_success_rate >= 70 ? 'border-l-4 border-green-500' : analytics.overview.overall_success_rate >= 50 ? 'border-l-4 border-yellow-500' : 'border-l-4 border-red-500'}`}>
                <div className="text-2xl font-bold text-gray-900">{analytics.overview.overall_success_rate.toFixed(1)}%</div>
                <div className="text-sm text-gray-600">Success Rate</div>
              </div>
            </div>
          )}

          {/* Problems Management */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Problems Management</h2>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Problem
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Difficulty
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Attempts
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Success Rate
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {problems.map((problem) => (
                    <tr key={problem.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{problem.title}</div>
                        <div className="text-sm text-gray-500">ID: {problem.id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getDifficultyColor(problem.difficulty)}`}>
                          {problem.difficulty}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          problem.is_active
                            ? 'text-green-800 bg-green-100'
                            : 'text-red-800 bg-red-100'
                        }`}>
                          {problem.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {problem.total_attempts}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {problem.success_rate.toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button
                          onClick={() => handleDeleteProblem(problem.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Create Problem Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Create New Problem</h3>
              <button
                onClick={resetForm}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateProblem} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  rows={4}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Difficulty</label>
                  <select
                    value={formData.difficulty}
                    onChange={(e) => setFormData({...formData, difficulty: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="Easy">Easy</option>
                    <option value="Medium">Medium</option>
                    <option value="Hard">Hard</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Input Example</label>
                  <input
                    type="text"
                    value={formData.input_example}
                    onChange={(e) => setFormData({...formData, input_example: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Output Example</label>
                  <input
                    type="text"
                    value={formData.output_example}
                    onChange={(e) => setFormData({...formData, output_example: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Test Cases (JSON format)
                  <span className="text-xs text-gray-500 ml-1">{"Example: " + JSON.stringify([{"input": "2\n3", "output": "5"}])}</span>
                </label>
                <textarea
                  value={Array.isArray(formData.test_cases) ? JSON.stringify(formData.test_cases, null, 2) : formData.test_cases}
                  onChange={(e) => setFormData({...formData, test_cases: e.target.value})}
                  rows={6}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                  placeholder='[{"input": "2\n3", "output": "5"}, {"input": "10\n20", "output": "30"}]'
                  required
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={resetForm}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
                >
                  Create Problem
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
