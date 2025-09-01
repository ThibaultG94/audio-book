'use client'

import { useState, useEffect } from 'react'
import VoiceCard from './VoiceCard'
import { api } from '@/lib/api'
import type { PreviewVoiceInfo, PreviewVoicesListResponse } from '@/lib/types'

interface VoiceSelectionPanelProps {
  onVoiceSelect: (voice: PreviewVoiceInfo) => void
  onStartConversion: () => void
}

export default function VoiceSelectionPanel({
  onVoiceSelect,
  onStartConversion
}: VoiceSelectionPanelProps) {
  const [voices, setVoices] = useState<PreviewVoiceInfo[]>([])
  const [selectedVoice, setSelectedVoice] = useState<PreviewVoiceInfo | null>(null)
  const [recommendations, setRecommendations] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'male' | 'female'>('all')
  const [audioPreview, setAudioPreview] = useState<HTMLAudioElement | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  
  useEffect(() => {
    loadVoices()
  }, [])
  
  const loadVoices = async () => {
    try {
      const response: PreviewVoicesListResponse = await api.getPreviewVoices()
      setVoices(response.voices)
      setRecommendations(response.recommendations)
      
      // Auto-select recommended voice
      if (response.recommendations?.french_best) {
        const recommendedVoice = response.voices.find(
          v => v.model_path === response.recommendations.french_best
        )
        if (recommendedVoice) {
          setSelectedVoice(recommendedVoice)
          onVoiceSelect(recommendedVoice)
        }
      }
    } catch (error) {
      console.error('Error loading voices:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleVoiceSelect = (voice: PreviewVoiceInfo) => {
    setSelectedVoice(voice)
    onVoiceSelect(voice)
  }
  
  const handlePreview = async (voice: PreviewVoiceInfo) => {
    setPreviewLoading(true)
    
    // Stop current preview if playing
    if (audioPreview) {
      audioPreview.pause()
      audioPreview.currentTime = 0
    }
    
    try {
      const response = await api.generateTTSPreview({
        text: "Bonjour, je suis une voix de synthèse française. Écoutez comment je peux lire vos livres avec une prononciation naturelle et fluide.",
        voice_model: voice.model_path,
        length_scale: 1.0,
        noise_scale: 0.667,
        noise_w: 0.8,
        sentence_silence: 0.35
      })
      
      // Create and play audio
      const audio = new Audio(response.audio_url)
      setAudioPreview(audio)
      await audio.play()
    } catch (error) {
      console.error('Preview error:', error)
    } finally {
      setPreviewLoading(false)
    }
  }
  
  const getFilteredVoices = () => {
    if (filter === 'all') return voices
    
    return voices.filter(voice => {
      const gender = voice.dataset?.includes('siwis') || voice.dataset?.includes('mls') 
        ? 'female' 
        : voice.dataset?.includes('tom') || voice.dataset?.includes('gilles')
        ? 'male'
        : 'neutral'
      
      return filter === gender
    })
  }
  
  const getRecommendationText = (voice: PreviewVoiceInfo): string | null => {
    if (!recommendations) return null
    
    if (recommendations.fastest === voice.model_path) return 'Plus rapide'
    if (recommendations.highest_quality === voice.model_path) return 'Meilleure qualité'
    if (recommendations.most_natural === voice.model_path) return 'Plus naturel'
    if (recommendations.french_best === voice.model_path) return 'Recommandé'
    
    return null
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des voix disponibles...</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Header with Filters */}
      <div className="bg-gradient-to-r from-purple-500 to-blue-500 text-white p-6 rounded-xl shadow-lg">
        <h2 className="text-2xl font-bold mb-4">🎤 Sélection de la voix</h2>
        
        <div className="flex items-center justify-between">
          <p className="text-blue-100">
            Choisissez une voix pour votre livre audio parmi nos {voices.length} voix françaises
          </p>
          
          {/* Filter Buttons */}
          <div className="flex space-x-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === 'all' 
                  ? 'bg-white text-purple-600' 
                  : 'bg-white/20 text-white hover:bg-white/30'
              }`}
            >
              Toutes
            </button>
            <button
              onClick={() => setFilter('female')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === 'female' 
                  ? 'bg-white text-purple-600' 
                  : 'bg-white/20 text-white hover:bg-white/30'
              }`}
            >
              👩 Féminines
            </button>
            <button
              onClick={() => setFilter('male')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === 'male' 
                  ? 'bg-white text-purple-600' 
                  : 'bg-white/20 text-white hover:bg-white/30'
              }`}
            >
              👨 Masculines
            </button>
          </div>
        </div>
      </div>
      
      {/* Voice Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {getFilteredVoices().map((voice) => (
          <VoiceCard
            key={voice.model_path}
            voice={voice}
            isSelected={selectedVoice?.model_path === voice.model_path}
            isRecommended={getRecommendationText(voice)}
            onSelect={() => handleVoiceSelect(voice)}
            onPreview={() => handlePreview(voice)}
          />
        ))}
      </div>
      
      {/* Selected Voice Summary */}
      {selectedVoice && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-gray-800 mb-2">
                ✅ Voix sélectionnée : {selectedVoice.name}
              </h3>
              <p className="text-gray-600">
                Prête pour la conversion de votre livre audio
              </p>
            </div>
            
            <button
              onClick={onStartConversion}
              className="px-8 py-3 bg-gradient-to-r from-green-500 to-blue-500 text-white font-bold rounded-lg hover:from-green-600 hover:to-blue-600 transition shadow-lg"
            >
              🚀 Lancer la conversion
            </button>
          </div>
        </div>
      )}
    </div>
  )
}