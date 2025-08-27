'use client'

import { useState, useEffect } from 'react'
import { api, ApiError } from '@/lib/api'
import type { Voice, VoicesListResponse } from '@/lib/types'

interface VoiceSelectorProps {
  onVoiceSelect: (voiceId: string) => void
  selectedVoice: string
  className?: string
}

export default function VoiceSelector({ 
  onVoiceSelect, 
  selectedVoice,
  className = ""
}: VoiceSelectorProps) {
  const [voices, setVoices] = useState<Voice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [qualityFilter, setQualityFilter] = useState<string>('all')
  const [usageFilter, setUsageFilter] = useState<string>('all')

  // Load voices on component mount
  useEffect(() => {
    loadVoices()
  }, [])

  const loadVoices = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response: VoicesListResponse = await api.getVoices()
      
      if (!response.voices || !Array.isArray(response.voices)) {
        throw new Error('Format de réponse invalide')
      }
      
      setVoices(response.voices)
      
      // Auto-select default voice if none selected
      if (!selectedVoice && response.default_voice) {
        onVoiceSelect(response.default_voice)
      }
      
    } catch (err) {
      console.error('Failed to load voices:', err)
      
      if (err instanceof ApiError) {
        setError(err.message)
      } else if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Erreur inconnue lors du chargement des voix')
      }
    } finally {
      setLoading(false)
    }
  }

  // Filter voices based on search and filters
  const filteredVoices = voices.filter(voice => {
    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase()
      const matchesSearch = (
        voice.name.toLowerCase().includes(searchLower) ||
        voice.language.toLowerCase().includes(searchLower) ||
        voice.metadata.dataset.toLowerCase().includes(searchLower)
      )
      if (!matchesSearch) return false
    }
    
    // Quality filter
    if (qualityFilter !== 'all' && voice.quality !== qualityFilter) {
      return false
    }
    
    // Usage filter
    if (usageFilter !== 'all') {
      const hasUsage = voice.metadata.recommended_usage?.includes(usageFilter)
      if (!hasUsage) return false
    }
    
    return true
  })

  if (loading) {
    return (
      <div className={`space-y-4 ${className}`}>
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          <span className="text-sm text-gray-600">Chargement des voix...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`space-y-4 ${className}`}>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <div className="text-red-600">❌</div>
            <h3 className="text-sm font-medium text-red-800">
              Erreur de chargement des voix
            </h3>
          </div>
          <p className="text-sm text-red-700 mb-3">{error}</p>
          <button
            onClick={loadVoices}
            className="text-sm bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded transition-colors"
          >
            Réessayer
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Rechercher
          </label>
          <input
            type="text"
            placeholder="Nom, langue, dataset..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Qualité
          </label>
          <select
            value={qualityFilter}
            onChange={(e) => setQualityFilter(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">Toutes qualités</option>
            <option value="low">Faible (rapide)</option>
            <option value="medium">Moyenne</option>
            <option value="high">Élevée (lente)</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Usage recommandé
          </label>
          <select
            value={usageFilter}
            onChange={(e) => setUsageFilter(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">Tous usages</option>
            <option value="audiobook">Livres audio</option>
            <option value="news">Actualités</option>
            <option value="general">Usage général</option>
            <option value="formal">Formel</option>
          </select>
        </div>
      </div>

      {/* Results count */}
      <div className="text-sm text-gray-600">
        {filteredVoices.length} voix disponibles
      </div>

      {/* Voice list */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
        {filteredVoices.map((voice) => (
          <div
            key={voice.id}
            onClick={() => onVoiceSelect(voice.id)}
            className={`
              p-4 border rounded-lg cursor-pointer transition-all
              ${selectedVoice === voice.id
                ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }
              ${!voice.is_available ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-medium text-gray-900">
                {voice.name} ({voice.quality.charAt(0).toUpperCase() + voice.quality.slice(1)})
              </h3>
              {!voice.is_available && (
                <span className="text-xs text-red-600 bg-red-100 px-2 py-1 rounded">
                  Indisponible
                </span>
              )}
            </div>
            
            <div className="text-sm text-gray-600 space-y-1">
              <div>Langue: {voice.language}</div>
              {voice.gender && <div>Genre: {voice.gender}</div>}
              <div>Dataset: {voice.metadata.dataset}</div>
              <div>Fréquence: {voice.metadata.technical.sample_rate} Hz</div>
            </div>
            
            {voice.metadata.recommended_usage && voice.metadata.recommended_usage.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {voice.metadata.recommended_usage.map((usage: string) => (
                  <span
                    key={usage}
                    className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
                  >
                    {usage}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredVoices.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          Aucune voix trouvée avec les filtres actuels
        </div>
      )}
    </div>
  )
}
