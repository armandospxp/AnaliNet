import { ChartBarIcon, UserGroupIcon, BeakerIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'

const stats = [
  { name: 'Total Patients', value: '2,145', icon: UserGroupIcon },
  { name: 'Tests Today', value: '48', icon: BeakerIcon },
  { name: 'Pending Results', value: '12', icon: ChartBarIcon },
  { name: 'Anomalies Detected', value: '3', icon: ExclamationTriangleIcon },
]

export default function Dashboard() {
  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
          Dashboard
        </h2>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <dt className="flex items-center gap-x-3 text-base font-semibold leading-6 text-gray-900">
              <stat.icon className="h-6 w-6 text-primary-600" aria-hidden="true" />
              {stat.name}
            </dt>
            <dd className="mt-2 text-3xl font-semibold tracking-tight text-primary-600">
              {stat.value}
            </dd>
          </div>
        ))}
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Activity */}
        <div className="card">
          <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Recent Activity</h3>
          <div className="flow-root">
            <ul role="list" className="-mb-8">
              <li className="relative pb-8">
                <div className="relative flex space-x-3">
                  <div>
                    <span className="h-8 w-8 rounded-full bg-primary-500 flex items-center justify-center ring-8 ring-white">
                      <BeakerIcon className="h-5 w-5 text-white" aria-hidden="true" />
                    </span>
                  </div>
                  <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                    <div>
                      <p className="text-sm text-gray-500">
                        New test results added for <span className="font-medium text-gray-900">John Doe</span>
                      </p>
                    </div>
                    <div className="whitespace-nowrap text-right text-sm text-gray-500">
                      <time dateTime="2025-03-19T20:00:00">1 hour ago</time>
                    </div>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>

        {/* AI Insights */}
        <div className="card">
          <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">AI Insights</h3>
          <div className="rounded-md bg-yellow-50 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" aria-hidden="true" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">Anomaly Detected</h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p>
                    Unusual pattern detected in blood glucose test results for 3 patients.
                    Consider reviewing these cases.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
