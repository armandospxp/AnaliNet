import { useState } from 'react'
import { MagnifyingGlassIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

interface TestResult {
  id: number
  patientName: string
  testName: string
  value: number
  unit: string
  date: string
  status: 'Normal' | 'Abnormal' | 'Critical'
  aiAnalysis: string | null
}

const mockResults: TestResult[] = [
  {
    id: 1,
    patientName: 'John Doe',
    testName: 'Blood Glucose',
    value: 95,
    unit: 'mg/dL',
    date: '2025-03-19',
    status: 'Normal',
    aiAnalysis: null
  },
  {
    id: 2,
    patientName: 'Jane Smith',
    testName: 'Blood Glucose',
    value: 180,
    unit: 'mg/dL',
    date: '2025-03-19',
    status: 'Critical',
    aiAnalysis: 'Significant deviation from normal range. Recommend immediate review.'
  }
]

export default function Results() {
  const [searchTerm, setSearchTerm] = useState('')
  const [results] = useState<TestResult[]>(mockResults)

  const filteredResults = results.filter(result =>
    result.patientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    result.testName.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div>
      <div className="mb-8 sm:flex sm:items-center sm:justify-between">
        <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
          Test Results
        </h2>
        <div className="mt-4 sm:ml-4 sm:mt-0">
          <button
            type="button"
            className="btn-primary flex items-center"
          >
            <ArrowPathIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
            Sync Results
          </button>
        </div>
      </div>

      <div className="card">
        <div className="mb-4">
          <div className="relative mt-1 rounded-md shadow-sm">
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
            </div>
            <input
              type="text"
              className="block w-full rounded-md border-gray-300 pl-10 focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              placeholder="Search results..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="mt-8 flow-root">
          <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
            <div className="inline-block min-w-full py-2 align-middle">
              <table className="min-w-full divide-y divide-gray-300">
                <thead>
                  <tr>
                    <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">
                      Patient
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Test
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Result
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Date
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredResults.map((result) => (
                    <tr key={result.id} className="hover:bg-gray-50">
                      <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900">
                        {result.patientName}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        {result.testName}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        {result.value} {result.unit}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        {result.date}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm">
                        <span
                          className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                            result.status === 'Normal'
                              ? 'bg-green-100 text-green-800'
                              : result.status === 'Critical'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {result.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* AI Analysis Section */}
        {filteredResults.some(result => result.aiAnalysis) && (
          <div className="mt-6 border-t border-gray-200 pt-6">
            <h3 className="text-lg font-medium text-gray-900">AI Analysis</h3>
            <div className="mt-4 space-y-4">
              {filteredResults
                .filter(result => result.aiAnalysis)
                .map(result => (
                  <div key={`analysis-${result.id}`} className="rounded-md bg-yellow-50 p-4">
                    <div className="flex">
                      <div className="ml-3">
                        <h4 className="text-sm font-medium text-yellow-800">
                          Analysis for {result.patientName}'s {result.testName}
                        </h4>
                        <div className="mt-2 text-sm text-yellow-700">
                          <p>{result.aiAnalysis}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
