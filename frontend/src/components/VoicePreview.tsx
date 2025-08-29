'use client'

import { useState, useRef, useEffect } from 'react'
import { api, ApiError } from '@/lib/api'
import type { TTSPreviewRequest, TTSPreviewResponse, DefaultParametersResponse } from '@/lib/types'
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
  const [defaultParams, setDefaultParams] = useState<DefaultParametersResponse | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [currentAudioUrl, setCurrentAudioUrl] = useState<string | null>(null)
  const [currentPreviewId, setCurrentPreviewId] = useState<string | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activePreset, setActivePreset] = useState<string | null>(null)

  const audioRef = useRef<HTMLAudioElement>(null)

  // Load default parameters
  useEffect(() => {
    loadDefaultParameters()
  }, [])

  // Notify parent when settings change (only if voice is already selected)
  useEffect(() => {
    if (selectedVoice && onVoiceTest) {
      onVoiceTest(selectedVoice, settings)
    }
  }, [settings.length_scale, settings.noise_scale, settings.noise_w, settings.sentence_silence])

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

  const loadDefaultParameters = async () => {
    try {
      const params = await api.getDefaultParameters()
      setDefaultParams(params)
      
      // Set default values from API
      setSettings({
        length_scale: params.parameters.length_scale.default,
        noise_scale: params.parameters.noise_scale.default,
        noise_w: params.parameters.noise_w.default,
        sentence_silence: params.parameters.sentence_silence.default,
      })
    } catch (err) {
      console.error('Failed to load default parameters:', err)
    }
  }

  const applyPreset = (presetName: string) => {
    if (!defaultParams?.presets) return
    
    const preset = defaultParams.presets[presetName as keyof typeof defaultParams.presets]
    if (preset) {
      setSettings({
        length_scale: preset.length_scale,
        noise_scale: preset.noise_scale,
        noise_w: preset.noise_w,
        sentence_silence: preset.sentence_silence,
      })
      setActivePreset(presetName)
    }
  }

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
      setCurrentPreviewId(response.preview_id)
      
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

      // Notify parent component with settings
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

  const deleteCurrentPreview = async () => {
    if (!currentPreviewId) return
    
    try {
      await api.deletePreview(currentPreviewId)
      setCurrentAudioUrl(null)
      setCurrentPreviewId(null)
      setIsPlaying(false)
    } catch (err) {
      console.error("Failed to delete preview:", err)
    }
  }

  const handleParameterChange = (param: keyof VoiceSettings, value: number) => {
    setSettings(prev => ({ ...prev, [param]: value }))
    setActivePreset(null) // Clear active preset when manually adjusting
  }

  const resetToDefaults = () => {
    if (!defaultParams) return
    
    setSettings({
      length_scale: defaultParams.parameters.length_scale.default,
      noise_scale: defaultParams.parameters.noise_scale.default,
      noise_w: defaultParams.parameters.noise_w.default,
      sentence_silence: defaultParams.parameters.sentence_silence.default,
    })
    setActivePreset(null)
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Voice Selection */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          🎭 Sélection de la voix
        </h3>
        <VoiceSelector
          onVoiceSelect={(voice) => {
            setSelectedVoice(voice)
            // Immediately notify parent with current settings
            if (onVoiceTest) {
              onVoiceTest(voice, settings)
            }
          }}
          selectedVoice={selectedVoice}
        />
      </div>

      {/* Preview Text */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          📝 Texte d'aperçu
        </h3>
        <div className="space-y-3">
          <textarea
            value={previewText}
            onChange={(e) => setPreviewText(e.target.value)}
            placeholder="Entrez le texte à synthétiser..."
            rows={4}
            maxLength={500}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 resize-none"
          />
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-500">{previewText.length}/500 caractères</span>
            <button
              onClick={() => setPreviewText("Bonjour ! Ceci est un aperçu de la voix française pour la conversion de vos livres audio. Vous pouvez ajuster la vitesse, l'expressivité et d'autres paramètres selon vos préférences.")}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              Texte par défaut
            </button>
          </div>
        </div>
      </div>

      {/* Voice Settings */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            ⚙️ Paramètres de la voix
          </h3>
          <button
            onClick={resetToDefaults}
            className="text-sm text-gray-600 hover:text-gray-800 font-medium"
          >
            Réinitialiser
          </button>
        </div>

        {/* Presets */}
        {defaultParams?.presets && (
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Préréglages rapides :</h4>
            <div className="flex flex-wrap gap-2">
              {Object.entries(defaultParams.presets).map(([key, preset]) => (
                <button
                  key={key}
                  onClick={() => applyPreset(key)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activePreset === key
                      ? 'bg-blue-100 text-blue-800 border border-blue-300'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300'
                  }`}
                  title={preset.description}
                >
                  {key === 'audiobook_natural' && '📚 Livre audio naturel'}
                  {key === 'news_fast' && '📰 Actualités rapide'}
                  {key === 'storytelling' && '🎭 Conte expressif'}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Parameter Controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Vitesse de lecture: {settings.length_scale}
            </label>
            <input
              type="range"
              min={defaultParams?.parameters.length_scale.range[0] || 0.5}
              max={defaultParams?.parameters.length_scale.range[1] || 2.0}
              step={defaultParams?.parameters.length_scale.step || 0.1}
              value={settings.length_scale}
              onChange={(e) => handleParameterChange('length_scale', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Rapide (0.5)</span>
              <span>Normal (1.0)</span>
              <span>Lent (2.0)</span>
            </div>
            {defaultParams?.parameters.length_scale && (
              <p className="text-xs text-gray-600 mt-1">
                {defaultParams.parameters.length_scale.description}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Expressivité: {settings.noise_scale}
            </label>
            <input
              type="range"
              min={defaultParams?.parameters.noise_scale.range[0] || 0.0}
              max={defaultParams?.parameters.noise_scale.range[1] || 1.0}
              step={defaultParams?.parameters.noise_scale.step || 0.1}
              value={settings.noise_scale}
              onChange={(e) => handleParameterChange('noise_scale', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Monotone (0.0)</span>
              <span>Naturel (0.7)</span>
              <span>Expressif (1.0)</span>
            </div>
            {defaultParams?.parameters.noise_scale && (
              <p className="text-xs text-gray-600 mt-1">
                {defaultParams.parameters.noise_scale.description}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Variation phonétique: {settings.noise_w}
            </label>
            <input
              type="range"
              min={defaultParams?.parameters.noise_w.range[0] || 0.0}
              max={defaultParams?.parameters.noise_w.range[1] || 1.0}
              step={defaultParams?.parameters.noise_w.step || 0.1}
              value={settings.noise_w}
              onChange={(e) => handleParameterChange('noise_w', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            {defaultParams?.parameters.noise_w && (
              <p className="text-xs text-gray-600 mt-1">
                {defaultParams.parameters.noise_w.description}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pause entre phrases: {settings.sentence_silence}s
            </label>
            <input
              type="range"
              min={defaultParams?.parameters.sentence_silence.range[0] || 0.0}
              max={defaultParams?.parameters.sentence_silence.range[1] || 2.0}
              step={defaultParams?.parameters.sentence_silence.step || 0.05}
              value={settings.sentence_silence}
              onChange={(e) => handleParameterChange('sentence_silence', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            {defaultParams?.parameters.sentence_silence && (
              <p className="text-xs text-gray-600 mt-1">
                {defaultParams.parameters.sentence_silence.description}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Generate and Play */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          🎵 Génération et écoute
        </h3>
        
        <div className="space-y-4">
          <button
            onClick={generatePreview}
            disabled={isGenerating || !selectedVoice || !previewText.trim()}
            className="w-full inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed disabled:from-gray-400 disabled:to-gray-400 transition-all duration-200"
          >
            {isGenerating ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                Génération en cours...
              </>
            ) : (
              <>
                🎤 Générer aperçu vocal
              </>
            )}
          </button>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <div className="text-red-600 text-xl">⚠️</div>
                <div>
                  <h4 className="text-sm font-medium text-red-800 mb-1">Erreur de génération</h4>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {currentAudioUrl && (
            <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h4 className="text-sm font-semibold text-gray-900">Aperçu généré ✨</h4>
                  <p className="text-sm text-gray-600">
                    Voix : {selectedVoice.split('/').pop()?.replace('.onnx', '') || 'Inconnue'}
                  </p>
                </div>
                <button
                  onClick={deleteCurrentPreview}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                  title="Supprimer cet aperçu"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
              
              <div className="flex items-center space-x-4 mb-4">
                <button
                  onClick={togglePlayback}
                  className="inline-flex items-center px-4 py-2 bg-white border border-gray-300 text-sm font-medium rounded-lg text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
                >
                  {isPlaying ? "⏸️ Pause" : "▶️ Écouter"}
                </button>
                
                <span className="text-sm text-gray-600">
                  Paramètres appliqués : Vitesse {settings.length_scale}x, Expressivité {settings.noise_scale}
                </span>
              </div>
              
              <audio
                ref={audioRef}
                className="w-full"
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