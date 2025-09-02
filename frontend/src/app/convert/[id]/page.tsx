'use client'

import { useParams, useRouter } from 'next/navigation'
import ConversionStatus from '@/components/ConversionStatus'

export default function ConversionPage() {
  const params = useParams()
  const router = useRouter()
  const jobId = params.id as string

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => router.push('/')}
                className="text-gray-600 hover:text-gray-900"
              >
                ← Retour
              </button>
              <h1 className="text-2xl font-bold text-gray-900">
                Statut de conversion
              </h1>
            </div>
            <span className="text-sm text-gray-500">
              ID: {jobId.slice(0, 8)}...
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <ConversionStatus jobId={jobId} />
      </main>
    </div>
  )
}