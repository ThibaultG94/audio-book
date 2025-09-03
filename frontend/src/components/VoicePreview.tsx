'use client'

import { useState, useRef } from 'react'
import VoiceSelectionPanel from './VoiceSelectionPanel'
import type { PreviewVoiceInfo } from '@/lib/api'

interface VoicePreviewProps {
  onVoiceTest?: (voiceModel: string, settings: any) => void
  className?: string
}

export default function VoicePreview({ onVoiceTest, className = "" }: VoicePreviewProps) {
  const [selectedVoiceInfo, setSelectedVoiceInfo] = useState<PreviewVoiceInfo | null>(null)
  const [previewText, setPreviewText] = useState(
    "Bonjour ! Ceci est un aperçu de la voix française pour la conversion de vos livres audio."
  )
  const [settings, setSettings] = useState({
    length_scale: 1.0,
    noise_scale: 0.667,
    noise_w: 0.8,
    sentence_silence: 0.35
  })
  const [isGenerating, setIsGenerating] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const audioRef = useRef<HTMLAudioElement>(null)

  const handleVoiceSelect = (voice: PreviewVoiceInfo) => {
    setSelectedVoiceInfo(voice)
    if (onVoiceTest) {
      onVoiceTest(voice.model_path, settings)
    }
  }

  const handlePreview = async () => {
    if (!selectedVoiceInfo || !previewText.trim()) {
      setError('Sélectionnez une voix et entrez du texte')
      return
    }

    setIsGenerating(true)
    setError(null)

    try {
      // Simulation d'un appel API
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Pour l'instant, on simule juste la génération
      setError('Preview simulé - backend pas encore connecté')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de génération')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSettingChange = (key: string, value: number) => {
    const newSettings = { ...settings, [key]: value }
    setSettings(newSettings)
    
    if (selectedVoiceInfo && onVoiceTest) {
      onVoiceTest(selectedVoiceInfo.model_path, newSettings)
    }
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Voice Selection */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Sélection de la voix
        </h3>
        <VoiceSelectionPanel
          onVoiceSelect={handleVoiceSelect}
        />
      </div>

      {/* Preview Text */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Texte d'aperçu
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
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Paramètres de la voix
        </h3>
        
        <div className="space-y-4">
          {/* Speed */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Vitesse de parole: {settings.length_scale.toFixed(2)}
            </label>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={settings.length_scale}
              onChange={(e) => handleSettingChange('length_scale', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Lent</span>
              <span>Rapide</span>
            </div>
          </div>

          {/* Expressiveness */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Expressivité: {settings.noise_scale.toFixed(3)}
            </label>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={settings.noise_scale}
              onChange={(e) => handleSettingChange('noise_scale', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Monotone</span>
              <span>Expressif</span>
            </div>
          </div>

          {/* Phonetic Variation */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Variation phonétique: {settings.noise_w.toFixed(2)}
            </label>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.1"
              value={settings.noise_w}
              onChange={(e) => handleSettingChange('noise_w', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Stable</span>
              <span>Varié</span>
            </div>
          </div>

          {/* Sentence Silence */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pause entre phrases: {settings.sentence_silence.toFixed(2)}s
            </label>
            <input
              type="range"
              min="0.0"
              max="2.0"
              step="0.05"
              value={settings.sentence_silence}
              onChange={(e) => handleSettingChange('sentence_silence', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Aucune</span>
              <span>Longue</span>
            </div>
          </div>
        </div>

        {/* Reset Button */}
        <button
          onClick={() => {
            const defaultSettings = {
              length_scale: 1.0,
              noise_scale: 0.667,
              noise_w: 0.8,
              sentence_silence: 0.35
            }
            setSettings(defaultSettings)
            if (selectedVoiceInfo && onVoiceTest) {
              onVoiceTest(selectedVoiceInfo.model_path, defaultSettings)
            }
          }}
          className="mt-4 text-sm text-gray-600 hover:text-gray-800 font-medium"
        >
          Réinitialiser aux valeurs par défaut
        </button>
      </div>

      {/* Preview Button */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Aperçu de la voix
        </h3>
        
        {selectedVoiceInfo && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
            <p className="text-sm">
              Voix sélectionnée: <strong>{selectedVoiceInfo.name}</strong>
            </p>
            <p className="text-xs text-gray-600">{selectedVoiceInfo.description}</p>
          </div>
        )}
        
        <button
          onClick={handlePreview}
          disabled={isGenerating || !selectedVoiceInfo || !previewText.trim()}
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? 'Génération en cours...' : 'Générer l\'aperçu vocal'}
        </button>

        {error && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-yellow-800 text-sm">{error}</p>
          </div>
        )}

        {/* Audio Player (hidden for now) */}
        <audio ref={audioRef} className="hidden" />
      </div>
    </div>
  )
}