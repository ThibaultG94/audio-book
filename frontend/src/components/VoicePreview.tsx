'use client'

import { useState, useRef, useEffect } from 'react'
import { api, ApiError } from '@/lib/api'
import type { TTSPreviewRequest, TTSPreviewResponse } from '@/lib/types'
import VoiceSelector from './VoiceSelector'

interface VoiceSettings {
  length_scale: number
  noise_scale: number
  noise_w: number
  sentence_silence: number
}

interface VoicePreviewProps {
  onVoiceTest?: (voice: string, settings: VoiceSettings) => void
  className?: string
}

export default function VoicePreview({ onVoiceTest, className = "" }: VoicePreviewProps) {
  const [selectedVoice, setSelectedVoice] = useState<string>("")
  const [previewText, setPreviewText] = useState(
    "Bonjour ! Ceci est un aperçu de la voix française pour la conversion de vos livres audio. Vous pouvez ajuster la vitesse, l'expressivité et d'autres paramètres selon vos préférences."
  )
  const [settings, setSettings] = useState<VoiceSettings>({
    length_scale: 1.0,
    noise_scale: 0.667,
    noise_w: 0.8,
    sentence_silence: 0.35
  })
  const [isGenerating, setIsGenerating] = useState(false)
  const [currentAudioUrl, setCurrentAudioUrl] = useState<string | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const audioRef = useRef<HTMLAudioElement>(null)

  // Handle audio playback events
  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)
    const handleEnded = () => setIsPlaying(false)

    audio.addEventListener('play', handlePlay)
    audio.addEventListener('pause', handlePause)
    audio.addEventListener('ended', handleEnded)

    return () => {
      audio.removeEventListener('play', handlePlay)
      audio.removeEventListener('pause', handlePause)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [])

  const generatePreview = async () => {
    if (!previewText.trim()) {
      setError("Veuillez entrer du texte pour l'aperçu")
      return
    }

    if (previewText.length > 500) {
      setError("Le texte est trop long (maximum 500 caractères)")
      return
    }

    if (!selectedVoice) {
      setError("Veuillez sélectionner une voix")
      return
    }

    setIsGenerating(true)
    setError(null)

    try {
      const request: TTSPreviewRequest = {
        text: previewText,
        voice_model: selectedVoice,
        length_scale: settings.length_scale,
        noise_scale: settings.noise_scale,
        noise_w: settings.noise_w,
        sentence_silence: settings.sentence_silence
      }

      const response: TTSPreviewResponse = await api.generateTTSPreview(request)
      
      if (!response.audio_url) {
        throw new Error("Réponse invalide - pas d'URL audio")
      }
      
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const fullAudioUrl = `${API_BASE_URL}${response.audio_url}`
      setCurrentAudioUrl(fullAudioUrl)
      
      // Auto-play the preview
      if (audioRef.current) {
        audioRef.current.src = fullAudioUrl
        try {
          await audioRef.current.play()
          setIsPlaying(true)
        } catch (playError) {
          console.warn("Auto-play failed:", playError)
        }
      }

      // Notify parent component
      onVoiceTest?.(selectedVoice, settings)

    } catch (err) {
      console.error("Preview generation error:", err)
      
      let errorMessage = "Erreur inconnue"
      if (err instanceof ApiError) {
        errorMessage = err.message
      } else if (err instanceof Error) {
        errorMessage = err.message
      }
      
      if (errorMessage.includes("fetch") || errorMessage.includes("NetworkError")) {
        errorMessage = "Backend non accessible - vérifiez que FastAPI tourne sur le port 8000"
      }
      
      setError(errorMessage)
    } finally {
      setIsGenerating(false)
    }
  }

  const togglePlayback = async () => {
    if (!audioRef.current || !currentAudioUrl) return

    try {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        await audioRef.current.play()
      }
    } catch (err) {
      console.error("Playback error:", err)
      setError("Erreur de lecture audio")
    }
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Voice Selection */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3">
          1. Sélection de la voix
        </h3>
        <VoiceSelector
          onVoiceSelect={setSelectedVoice}
          selectedVoice={selectedVoice}
        />
      </div>

      {/* Preview Text */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3">
          2. Texte d'aperçu
        </h3>
        <div className="space-y-2">
          <textarea
            value={previewText}
            onChange={(e) => setPreviewText(e.target.value)}
            placeholder="Entrez le texte à synthétiser..."
            rows={4}
            maxLength={500}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
          <div className="flex justify-between text-sm text-gray-500">
            <span>{previewText.length}/500 caractères</span>
            <button
              onClick={() => setPreviewText("Bonjour ! Ceci est un aperçu de la voix française pour la conversion de vos livres audio. Vous pouvez ajuster la vitesse, l'expressivité et d'autres paramètres selon vos préférences.")}
              className="text-blue-600 hover:text-blue-800"
            >
              Texte par défaut
            </button>
          </div>
        </div>
      </div>

      {/* Voice Settings */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3">
          3. Paramètres de la voix
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Vitesse de lecture: {settings.length_scale}
            </label>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={settings.length_scale}
              onChange={(e) => setSettings(prev => ({ ...prev, length_scale: parseFloat(e.target.value) }))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Rapide</span>
              <span>Normal</span>
              <span>Lent</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Expressivité: {settings.noise_scale}
            </label>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.1"
              value={settings.noise_scale}
              onChange={(e) => setSettings(prev => ({ ...prev, noise_scale: parseFloat(e.target.value) }))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Monotone</span>
              <span>Naturel</span>
              <span>Expressif</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Pause entre phrases: {settings.sentence_silence}s
            </label>
            <input
              type="range"
              min="0.0"
              max="2.0"
              step="0.05"
              value={settings.sentence_silence}
              onChange={(e) => setSettings(prev => ({ ...prev, sentence_silence: parseFloat(e.target.value) }))}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Variation phonétique: {settings.noise_w}
            </label>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.1"
              value={settings.noise_w}
              onChange={(e) => setSettings(prev => ({ ...prev, noise_w: parseFloat(e.target.value) }))}
              className="w-full"
            />
          </div>
        </div>
      </div>

      {/* Generate and Play */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3">
          4. Génération et écoute
        </h3>
        
        <div className="space-y-4">
          <button
            onClick={generatePreview}
            disabled={isGenerating || !selectedVoice || !previewText.trim()}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Génération en cours...
              </>
            ) : (
              <>
                🎤 Générer aperçu
              </>
            )}
          </button>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <div className="flex items-center space-x-2">
                <div className="text-red-600">⚠️</div>
                <span className="text-sm text-red-700">{error}</span>
              </div>
            </div>
          )}

          {currentAudioUrl && (
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-4">
                <button
                  onClick={togglePlayback}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  {isPlaying ? "⏸️ Pause" : "▶️ Lire"}
                </button>
                
                <span className="text-sm text-gray-600">
                  Aperçu généré avec la voix {selectedVoice}
                </span>
              </div>
              
              <audio
                ref={audioRef}
                className="w-full mt-3"
                controls
                preload="metadata"
              >
                Votre navigateur ne supporte pas l'élément audio.
              </audio>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}