'use client'

import React, { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import type { Voice } from '@/lib/types'

interface SimpleVoiceSelectorProps {
  onVoiceSelect: (voice: Voice) => void
  selectedVoice?: Voice | null
}

export default function SimpleVoiceSelector({ onVoiceSelect, selectedVoice }: SimpleVoiceSelectorProps) {
  const [voices, setVoices] = useState<Voice[]>([])
  const [loading, setLoading] = useState(true)
  const [previewLoading, setPreviewLoading] = useState<string | null>(null)

  useEffect(() => {
    // Délayer le chargement pour éviter l'erreur d'hydratation
    const timer = setTimeout(() => {
      loadVoices()
    }, 100)
    
    return () => clearTimeout(timer)
  }, [])

  const loadVoices = async () => {
    // Ne pas charger côté serveur
    if (typeof window === 'undefined') return
    
    try {
      const response = await api.getVoices()
      setVoices(response.voices)
      
      // Auto-select first French medium voice
      const bestVoice = response.voices.find(v => 
        v.metadata.language_code === 'fr_FR' && 
        v.technical_info.model_size === 'medium'
      ) || response.voices[0]
      
      if (bestVoice && !selectedVoice) {
        onVoiceSelect(bestVoice)
      }
    } catch (error) {
      console.error('Failed to load voices:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePreview = async (voice: Voice) => {
    setPreviewLoading(voice.id)
    try {
      const response = await api.generateTTSPreview({
        text: "Bonjour, voici un aperçu de ma voix.",
        voice_model: voice.model_path.split('/').pop() || voice.id
      })
      
      const audio = new Audio(response.audio_url)
      await audio.play()
    } catch (error) {
      console.error('Preview failed:', error)
    } finally {
      setPreviewLoading(null)
    }
  }

  const getVoiceEmoji = (voice: Voice) => {
    if (voice.metadata.gender === 'male') return '👨'
    if (voice.metadata.gender === 'female') return '👩'
    return '🎤'
  }

  const getQualityColor = (size: string) => {
    switch (size) {
      case 'high': return 'text-green-600 bg-green-50 border-green-200'
      case 'medium': return 'text-blue-600 bg-blue-50 border-blue-200'
      case 'low': return 'text-orange-600 bg-orange-50 border-orange-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div>
        <span className="ml-3 text-gray-600">Chargement des voix...</span>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* French Voices */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3">🇫🇷 Voix Françaises</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {voices.filter(v => v.metadata.language_code === 'fr_FR').map((voice) => (
            <button
              key={voice.id}
              onClick={() => onVoiceSelect(voice)}
              className={`p-4 text-left rounded-lg border-2 transition-all ${
                selectedVoice?.id === voice.id
                  ? 'border-purple-500 bg-purple-50'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">{getVoiceEmoji(voice)}</span>
                  <div>
                    <p className="font-medium text-gray-900">{voice.metadata.name}</p>
                    <p className={`text-xs px-2 py-1 rounded-full border ${getQualityColor(voice.technical_info.model_size)}`}>
                      {voice.technical_info.model_size}
                    </p>
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handlePreview(voice)
                  }}
                  disabled={previewLoading === voice.id}
                  className="p-2 text-gray-400 hover:text-purple-600 transition-colors"
                >
                  {previewLoading === voice.id ? (
                    <div className="w-4 h-4 border-b-2 border-purple-600 rounded-full animate-spin"></div>
                  ) : (
                    <span>🔊</span>
                  )}
                </button>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* English Voices */}
      {voices.some(v => v.metadata.language_code === 'en_US') && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-3">🇺🇸 English Voices</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {voices.filter(v => v.metadata.language_code === 'en_US').map((voice) => (
              <button
                key={voice.id}
                onClick={() => onVoiceSelect(voice)}
                className={`p-4 text-left rounded-lg border-2 transition-all ${
                  selectedVoice?.id === voice.id
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">{getVoiceEmoji(voice)}</span>
                    <div>
                      <p className="font-medium text-gray-900">{voice.metadata.name}</p>
                      <p className={`text-xs px-2 py-1 rounded-full border ${getQualityColor(voice.technical_info.model_size)}`}>
                        {voice.technical_info.model_size}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handlePreview(voice)
                    }}
                    disabled={previewLoading === voice.id}
                    className="p-2 text-gray-400 hover:text-purple-600 transition-colors"
                  >
                    {previewLoading === voice.id ? (
                      <div className="w-4 h-4 border-b-2 border-purple-600 rounded-full animate-spin"></div>
                    ) : (
                      <span>🔊</span>
                    )}
                  </button>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}