'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'

// Define the type locally if not exported from types
interface ConversionStatusResponse {
  job_id: string
  status: string
  progress: number
  started_at: string
  completed_at?: string
  error?: string
  steps: {
    extraction: { status: string; progress: number }
    processing: { status: string; progress: number }
    synthesis: { status: string; progress: number }
    finalization: { status: string; progress: number }
  }
  output_file?: string
  duration_estimate?: number
  chapters: Array<{
    id: string
    title: string
    status: string
    text_length?: number
    audio_file?: string
  }>
}

interface ConversionStatusProps {
  jobId: string
}

export default function ConversionStatus({ jobId }: ConversionStatusProps) {
  const [status, setStatus] = useState<ConversionStatusResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await api.getConversionStatus(jobId)
        setStatus(response)
        setError(null)
        
        // If still processing, check again in 2 seconds
        if (response.status !== 'completed' && response.status !== 'failed') {
          setTimeout(checkStatus, 2000)
        }
      } catch (err) {
        console.error('Error fetching status:', err)
        setError('Erreur lors de la récupération du statut')
      } finally {
        setLoading(false)
      }
    }

    checkStatus()
  }, [jobId])

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">{error}</p>
      </div>
    )
  }

  if (!status) {
    return null
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600'
      case 'failed': return 'text-red-600'
      case 'processing': 
      case 'synthesizing': return 'text-blue-600'
      default: return 'text-gray-600'
    }
  }

  const getStepIcon = (stepStatus: string) => {
    switch (stepStatus) {
      case 'completed': return '✅'
      case 'in_progress': return '⏳'
      case 'failed': return '❌'
      default: return '⏸️'
    }
  }

  return (
    <div className="space-y-6">
      {/* Overall Progress */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Progression de la conversion</h3>
          <span className={`font-medium ${getStatusColor(status.status)}`}>
            {status.status}
          </span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all duration-500"
            style={{ width: `${status.progress}%` }}
          />
        </div>
        <p className="text-sm text-gray-600 mt-2">{status.progress}% complété</p>
      </div>

      {/* Steps Progress */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Étapes de conversion</h3>
        <div className="space-y-3">
          {Object.entries(status.steps).map(([key, step]) => (
            <div key={key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <span>{getStepIcon(step.status)}</span>
                <span className="font-medium capitalize">{key}</span>
              </div>
              <span className="text-sm text-gray-600">{step.status}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Error Display */}
      {status.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 className="font-medium text-red-800 mb-1">Erreur</h4>
          <p className="text-red-700">{status.error}</p>
        </div>
      )}

      {/* Success with Download */}
      {status.status === 'completed' && status.output_file && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h4 className="font-medium text-green-800 mb-3">✅ Conversion terminée !</h4>
          <button
            onClick={() => window.open(api.downloadAudio(jobId), '_blank')}
            className="px-6 py-3 bg-gradient-to-r from-green-500 to-blue-500 text-white font-medium rounded-lg hover:from-green-600 hover:to-blue-600"
          >
            📥 Télécharger l'audiobook
          </button>
        </div>
      )}
    </div>
  )
}