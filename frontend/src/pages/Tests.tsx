import { useState } from 'react'
import { PlusIcon, BeakerIcon } from '@heroicons/react/24/outline'

interface TestType {
  id: number
  name: string
  code: string
  description: string
  referenceRange: {
    min: number
    max: number
    unit: string
  }
  machineInterface: string
}

const mockTestTypes: TestType[] = [
  {
    id: 1,
    name: 'Blood Glucose',
    code: 'GLU',
    description: 'Measures the amount of glucose in blood',
    referenceRange: {
      min: 70,
      max: 100,
      unit: 'mg/dL'
    },
    machineInterface: 'GLUC-1000'
  },
  {
    id: 2,
    name: 'Complete Blood Count',
    code: 'CBC',
    description: 'Measures different components of blood',
    referenceRange: {
      min: 4.5,
      max: 11.0,
      unit: 'K/µL'
    },
    machineInterface: 'CBC-3000'
  }
]

export default function Tests() {
  const [testTypes] = useState<TestType[]>(mockTestTypes)

  return (
    <div>
      <div className="mb-8 sm:flex sm:items-center sm:justify-between">
        <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
          Laboratory Tests
        </h2>
        <div className="mt-4 sm:ml-4 sm:mt-0">
          <button
            type="button"
            className="btn-primary flex items-center"
          >
            <PlusIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
            Add Test Type
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {testTypes.map((test) => (
          <div key={test.id} className="card hover:shadow-lg transition-shadow duration-200">
            <div className="flex items-center mb-4">
              <BeakerIcon className="h-6 w-6 text-primary-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">{test.name}</h3>
            </div>
            
            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-500">Test Code</p>
                <p className="mt-1 text-sm text-gray-900">{test.code}</p>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-500">Description</p>
                <p className="mt-1 text-sm text-gray-900">{test.description}</p>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-500">Reference Range</p>
                <p className="mt-1 text-sm text-gray-900">
                  {test.referenceRange.min} - {test.referenceRange.max} {test.referenceRange.unit}
                </p>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-500">Equipment Interface</p>
                <p className="mt-1 text-sm text-gray-900">{test.machineInterface}</p>
              </div>

              <div className="pt-3">
                <button
                  type="button"
                  className="w-full rounded-md bg-primary-50 px-3 py-2 text-sm font-semibold text-primary-600 shadow-sm hover:bg-primary-100"
                >
                  View Details
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
