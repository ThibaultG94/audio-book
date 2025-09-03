'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import type { PreviewVoiceInfo, PreviewVoicesListResponse } from '@/lib/api'

interface VoiceSelectionPanelProps {
  onVoiceSelect: (voice: PreviewVoiceInfo) => void
  onStartConversion?: () => void
}

export default function VoiceSelectionPanel({
  onVoiceSelect,
  onStartConversion
}: VoiceSelectionPanelProps) {
  const [voices, setVoices] = useState<PreviewVoiceInfo[]>([])
  const [selectedVoice, setSelectedVoice] = useState<PreviewVoiceInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadVoices()
  }, [])

  const loadVoices = async () => {
    try {
      setLoading(true)
      const response = await api.getPreviewVoices()
      setVoices(response.voices)
      
      // Auto-select first voice
      if (response.voices.length > 0) {
        const firstVoice = response.voices[0]
        setSelectedVoice(firstVoice)
        onVoiceSelect(firstVoice)
      }
      
      setError(null)
    } catch (err) {
      console.error('Error loading voices:', err)
      setError(err instanceof Error ? err.message : 'Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }

  const handleVoiceSelect = (voice: PreviewVoiceInfo) => {
    setSelectedVoice(voice)
    onVoiceSelect(voice)
  }

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p>Chargement des voix...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Erreur: {error}</p>
        <button 
          onClick={loadVoices}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Réessayer
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium">Sélectionnez une voix</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {voices.map((voice) => (
          <div
            key={voice.id}
            onClick={() => handleVoiceSelect(voice)}
            className={`p-4 border rounded-lg cursor-pointer transition-colors ${
              selectedVoice?.id === voice.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <h4 className="font-medium">{voice.name}</h4>
            <p className="text-sm text-gray-600">{voice.description}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className={`px-2 py-1 text-xs rounded ${
                voice.gender === 'female' ? 'bg-pink-100 text-pink-800' : 'bg-blue-100 text-blue-800'
              }`}>
                {voice.gender === 'female' ? '♀' : '♂'} {voice.gender}
              </span>
              <span className={`px-2 py-1 text-xs rounded ${
                voice.quality === 'high' ? 'bg-green-100 text-green-800' :
                voice.quality === 'medium' ? 'bg-yellow-100 text-yellow-800' : 
                'bg-gray-100 text-gray-800'
              }`}>
                {voice.quality}
              </span>
            </div>
          </div>
        ))}
      </div>

      {selectedVoice && onStartConversion && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Voix sélectionnée: {selectedVoice.name}</p>
              <p className="text-sm text-gray-600">{selectedVoice.description}</p>
            </div>
            <button
              onClick={onStartConversion}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Commencer la conversion
            </button>
          </div>
        </div>
      )}
    </div>
  )
}