'use client'

import { useState, useEffect } from 'react'
import { api, ApiError } from '@/lib/api'
import type { PreviewVoiceInfo, PreviewVoicesListResponse } from '@/lib/types'

interface VoiceSelectorProps {
  onVoiceSelect: (voice: string) => void
  selectedVoice: string
  className?: string
}

export default function VoiceSelector({ 
  onVoiceSelect, 
  selectedVoice, 
  className = "" 
}: VoiceSelectorProps) {
  const [voices, setVoices] = useState<PreviewVoiceInfo[]>([])
  const [recommendations, setRecommendations] = useState<{
    fastest: string;
    highest_quality: string;
    most_natural: string;
    french_best: string;
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<'all' | 'male' | 'female' | 'low' | 'medium' | 'high'>('all')
  const [sortBy, setSortBy] = useState<'name' | 'quality' | 'size'>('name')

  useEffect(() => {
    loadVoices()
  }, [])

  const loadVoices = async () => {
    setLoading(true)
    setError(null)

    try {
      const response: PreviewVoicesListResponse = await api.getPreviewVoices()
      setVoices(response.voices)
      setRecommendations(response.recommendations)
      
      // Auto-select default voice if none selected
      if (!selectedVoice && response.default_voice) {
        onVoiceSelect(response.default_voice)
      }
    } catch (err) {
      console.error('Error loading voices:', err)
      
      let errorMessage = "Erreur lors du chargement des voix"
      if (err instanceof ApiError) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const getGenderFromDataset = (dataset?: string): 'male' | 'female' | 'unknown' => {
    if (!dataset) return 'unknown'
    
    const datasetLower = dataset.toLowerCase()
    
    // Known male voices
    if (['tom', 'bernard', 'gilles'].some(male => datasetLower.includes(male))) {
      return 'male'
    }
    
    // Known female voices  
    if (['siwis', 'mls', 'amy', 'jenny'].some(female => datasetLower.includes(female))) {
      return 'female'
    }
    
    return 'unknown'
  }

  const filteredAndSortedVoices = voices
    .filter(voice => {
      if (filter === 'all') return true
      
      if (filter === 'male' || filter === 'female') {
        return getGenderFromDataset(voice.dataset) === filter
      }
      
      if (filter === 'low' || filter === 'medium' || filter === 'high') {
        return voice.quality === filter
      }
      
      return true
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'quality':
          const qualityOrder = { 'high': 3, 'medium': 2, 'low': 1 }
          return (qualityOrder[b.quality as keyof typeof qualityOrder] || 0) - 
                 (qualityOrder[a.quality as keyof typeof qualityOrder] || 0)
        case 'size':
          return (b.file_size_mb || 0) - (a.file_size_mb || 0)
        case 'name':
        default:
          return a.name.localeCompare(b.name)
      }
    })

  const formatVoiceName = (voice: PreviewVoiceInfo): string => {
    const parts = voice.name.split('-')
    if (parts.length >= 2) {
      const dataset = parts[1]?.charAt(0).toUpperCase() + parts[1]?.slice(1)
      const quality = parts[2] ? ` (${parts[2]})` : ''
      return `${dataset}${quality}`
    }
    return voice.name
  }

  const getVoiceDescription = (voice: PreviewVoiceInfo): string => {
    const gender = getGenderFromDataset(voice.dataset)
    const genderText = gender === 'male' ? '♂️' : gender === 'female' ? '♀️' : '⚲'
    const sizeText = voice.file_size_mb ? `${voice.file_size_mb}MB` : 'N/A'
    const sampleRateText = voice.sample_rate ? `${voice.sample_rate}Hz` : 'N/A'
    
    return `${genderText} ${voice.quality || 'medium'} • ${sampleRateText} • ${sizeText}`
  }

  const getRecommendationBadge = (voiceModelPath: string): string | null => {
    if (!recommendations) return null
    
    if (recommendations.fastest === voiceModelPath) return 'Le plus rapide'
    if (recommendations.highest_quality === voiceModelPath) return 'Meilleure qualité'  
    if (recommendations.most_natural === voiceModelPath) return 'Le plus naturel'
    if (recommendations.french_best === voiceModelPath) return 'Recommandé français'
    
    return null
  }

  if (loading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="flex items-center space-x-3">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
          <span className="text-gray-600">Chargement des voix...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-center space-x-2">
          <div className="text-red-600">⚠️</div>
          <div>
            <p className="text-sm text-red-700 font-medium">Erreur de chargement</p>
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </div>
        <button
          onClick={loadVoices}
          className="mt-3 inline-flex items-center px-3 py-1.5 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
        >
          Réessayer
        </button>
      </div>
    )
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Filters and Sorting */}
      <div className="flex flex-wrap items-center gap-4 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Filtre:</label>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="text-sm border border-gray-300 rounded px-2 py-1"
          >
            <option value="all">Toutes</option>
            <option value="male">Voix masculines</option>
            <option value="female">Voix féminines</option>
            <option value="high">Haute qualité</option>
            <option value="medium">Qualité moyenne</option>
            <option value="low">Qualité basse</option>
          </select>
        </div>
        
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Tri:</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="text-sm border border-gray-300 rounded px-2 py-1"
          >
            <option value="name">Nom</option>
            <option value="quality">Qualité</option>
            <option value="size">Taille</option>
          </select>
        </div>
        
        <div className="text-sm text-gray-500">
          {filteredAndSortedVoices.length} voix disponibles
        </div>
      </div>

      {/* Voice Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {filteredAndSortedVoices.map((voice) => {
          const isSelected = selectedVoice === voice.model_path
          const recommendationBadge = getRecommendationBadge(voice.model_path)
          
          return (
            <div
              key={voice.model_path}
              onClick={() => onVoiceSelect(voice.model_path)}
              className={`relative p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 hover:shadow-md ${
                isSelected
                  ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500 ring-opacity-20'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              {/* Recommendation Badge */}
              {recommendationBadge && (
                <div className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full font-medium shadow-sm">
                  {recommendationBadge}
                </div>
              )}
              
              {/* Voice Info */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className={`font-medium text-sm ${
                    isSelected ? 'text-blue-900' : 'text-gray-900'
                  }`}>
                    {formatVoiceName(voice)}
                  </h4>
                  {isSelected && (
                    <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                      <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>
                
                <p className={`text-xs ${
                  isSelected ? 'text-blue-700' : 'text-gray-600'
                }`}>
                  {getVoiceDescription(voice)}
                </p>
                
                {/* Usage Tags */}
                {voice.recommended_usage && voice.recommended_usage.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {voice.recommended_usage.slice(0, 3).map((usage, idx) => (
                      <span
                        key={idx}
                        className={`inline-block px-2 py-0.5 text-xs rounded-full font-medium ${
                          isSelected
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {usage}
                      </span>
                    ))}
                    {voice.recommended_usage.length > 3 && (
                      <span className={`inline-block px-2 py-0.5 text-xs rounded-full font-medium ${
                        isSelected
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        +{voice.recommended_usage.length - 3}
                      </span>
                    )}
                  </div>
                )}
                
                {/* Language Info */}
                {voice.language && (
                  <div className={`text-xs ${
                    isSelected ? 'text-blue-600' : 'text-gray-500'
                  }`}>
                    🌍 {voice.language.name_native} ({voice.language.country_english})
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {filteredAndSortedVoices.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">🔍</div>
          <p>Aucune voix trouvée avec ces filtres</p>
          <button
            onClick={() => setFilter('all')}
            className="mt-2 text-blue-600 hover:text-blue-800 text-sm underline"
          >
            Réinitialiser les filtres
          </button>
        </div>
      )}
    </div>
  )
}