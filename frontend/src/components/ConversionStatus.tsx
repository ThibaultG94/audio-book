'use client'

import { useState, useEffect } from 'react'
import { api, ConversionStatusResponse } from '@/lib/api'

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
        
        // Continue polling if processing
        if (response.status === 'processing' || response.status === 'pending') {
          setTimeout(checkStatus, 2000)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erreur inconnue')
      } finally {
        setLoading(false)
      }
    }

    if (jobId) {
      checkStatus()
    }
  }, [jobId])

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mr-3"></div>
        <span>Chargement du statut...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-red-800 font-medium">Erreur</h3>
        <p className="text-red-700">{error}</p>
      </div>
    )
  }

  if (!status) return null

  const getStatusColor = (statusValue: string) => {
    switch (statusValue) {
      case 'completed': return 'text-green-600 bg-green-50'
      case 'processing': return 'text-blue-600 bg-blue-50'
      case 'failed': return 'text-red-600 bg-red-50'
      case 'pending': return 'text-yellow-600 bg-yellow-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getStatusText = (statusValue: string) => {
    switch (statusValue) {
      case 'pending': return 'En attente'
      case 'processing': return 'En cours'
      case 'completed': return 'Terminée'
      case 'failed': return 'Échouée'
      default: return statusValue
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold">Conversion en cours</h2>
        <p className="text-gray-600">Job ID: {status.job_id}</p>
      </div>

      <div className={`rounded-lg p-4 mb-6 ${getStatusColor(status.status)}`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-medium">Statut: {getStatusText(status.status)}</h3>
            <p className="text-sm opacity-75">
              Démarré: {new Date(status.started_at).toLocaleString('fr-FR')}
            </p>
            {status.completed_at && (
              <p className="text-sm opacity-75">
                Terminé: {new Date(status.completed_at).toLocaleString('fr-FR')}
              </p>
            )}
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{status.progress}%</div>
          </div>
        </div>
        
        <div className="mt-4">
          <div className="bg-white bg-opacity-50 rounded-full h-2">
            <div 
              className="h-2 rounded-full bg-current transition-all duration-500"
              style={{ width: `${status.progress}%` }}
            ></div>
          </div>
        </div>
      </div>

      {status.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 className="text-red-800 font-medium">Erreur</h4>
          <p className="text-red-700">{status.error}</p>
        </div>
      )}

      {status.status === 'completed' && (
        <div className="text-center bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="text-green-800 font-medium text-lg mb-2">
            ✅ Conversion terminée !
          </h3>
          <p className="text-green-700 mb-4">
            Votre livre audio est prêt
          </p>
          <button className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700">
            📥 Télécharger l'audio
          </button>
        </div>
      )}
    </div>
  )
}