"use client";

import { useState, useRef } from "react";
import { Play, Pause, Volume2, Settings, Loader2, Download } from "lucide-react";

interface Voice {
  model_path: string;
  name: string;
  language?: {
    name_english?: string;
    code?: string;
  };
  quality?: string;
  dataset?: string;
}

interface VoicePreviewProps {
  onVoiceTest?: (voice: string, settings: VoiceSettings) => void;
  className?: string;
}

interface VoiceSettings {
  length_scale: number;
  noise_scale: number;
}

const DEFAULT_PREVIEW_TEXT = "Bonjour ! Ceci est un aperçu de la voix française pour la conversion de vos livres audio.";

export function VoicePreview({ onVoiceTest, className = "" }: VoicePreviewProps) {
  const [previewText, setPreviewText] = useState(DEFAULT_PREVIEW_TEXT);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentAudioUrl, setCurrentAudioUrl] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Voice settings
  const [settings, setSettings] = useState<VoiceSettings>({
    length_scale: 1.0,
    noise_scale: 0.667
  });
  
  // Available voices (would be fetched from API)
  const [availableVoices] = useState<Voice[]>([
    {
      model_path: "fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx",
      name: "Siwis (French)",
      language: { name_english: "French", code: "fr_FR" },
      quality: "low",
      dataset: "siwis"
    }
  ]);
  
  const [selectedVoice, setSelectedVoice] = useState(availableVoices[0]?.model_path || "");
  
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const generatePreview = async () => {
    if (!previewText.trim()) {
      setError("Veuillez entrer du texte pour l'aperçu");
      return;
    }

    if (previewText.length > 500) {
      setError("Le texte est trop long (maximum 500 caractères)");
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch("/api/preview/tts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          text: previewText,
          voice_model: selectedVoice || undefined,
          length_scale: settings.length_scale,
          noise_scale: settings.noise_scale
        })
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(errorData || `HTTP ${response.status}`);
      }

      const data = await response.json();
      setCurrentAudioUrl(data.audio_url);
      
      // Automatically play the preview
      if (audioRef.current) {
        audioRef.current.src = data.audio_url;
        await audioRef.current.play();
        setIsPlaying(true);
      }

      // Notify parent component
      onVoiceTest?.(selectedVoice, settings);

    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec de la génération de l'aperçu");
    } finally {
      setIsGenerating(false);
    }
  };

  const togglePlayback = async () => {
    if (!audioRef.current || !currentAudioUrl) return;

    try {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        await audioRef.current.play();
        setIsPlaying(true);
      }
    } catch (err) {
      setError("Erreur lors de la lecture audio");
    }
  };

  const handleAudioEnd = () => {
    setIsPlaying(false);
  };

  const resetPreviewText = () => {
    setPreviewText(DEFAULT_PREVIEW_TEXT);
  };

  const downloadPreview = () => {
    if (currentAudioUrl) {
      const link = document.createElement('a');
      link.href = currentAudioUrl;
      link.download = 'voice-preview.wav';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className={`bg-white rounded-lg border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Volume2 className="h-5 w-5 mr-2" />
          Aperçu de la voix
        </h3>
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
          title="Paramètres de la voix"
        >
          <Settings className="h-4 w-4" />
        </button>
      </div>

      {/* Voice Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Voix disponibles
        </label>
        <select
          value={selectedVoice}
          onChange={(e) => setSelectedVoice(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {availableVoices.map((voice) => (
            <option key={voice.model_path} value={voice.model_path}>
              {voice.name} - {voice.quality} - {voice.language?.name_english}
            </option>
          ))}
        </select>
      </div>

      {/* Advanced Settings */}
      {showSettings && (
        <div className="mb-4 p-4 bg-gray-50 rounded-md space-y-4">
          <h4 className="text-sm font-medium text-gray-900">Paramètres avancés</h4>
          
          <div>
            <label className="block text-sm text-gray-700 mb-1">
              Vitesse de parole: {settings.length_scale}x
            </label>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={settings.length_scale}
              onChange={(e) => setSettings({
                ...settings,
                length_scale: parseFloat(e.target.value)
              })}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Plus lent</span>
              <span>Normal</span>
              <span>Plus rapide</span>
            </div>
          </div>
          
          <div>
            <label className="block text-sm text-gray-700 mb-1">
              Variation de voix: {settings.noise_scale}
            </label>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.1"
              value={settings.noise_scale}
              onChange={(e) => setSettings({
                ...settings,
                noise_scale: parseFloat(e.target.value)
              })}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Monotone</span>
              <span>Naturelle</span>
            </div>
          </div>
        </div>
      )}

      {/* Preview Text Input */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-700">
            Texte d'aperçu
          </label>
          <button
            onClick={resetPreviewText}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            Réinitialiser
          </button>
        </div>
        <textarea
          value={previewText}
          onChange={(e) => setPreviewText(e.target.value)}
          placeholder="Entrez le texte que vous souhaitez entendre..."
          maxLength={500}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
        <div className="flex justify-between mt-1">
          <span className="text-xs text-gray-500">
            {previewText.length}/500 caractères
          </span>
          {previewText.length > 400 && (
            <span className="text-xs text-amber-600">
              Texte long - génération plus lente
            </span>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Controls */}
      <div className="flex items-center space-x-3">
        <button
          onClick={generatePreview}
          disabled={isGenerating || !previewText.trim()}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isGenerating ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <Volume2 className="h-4 w-4 mr-2" />
          )}
          {isGenerating ? "Génération..." : "Générer aperçu"}
        </button>

        {currentAudioUrl && (
          <>
            <button
              onClick={togglePlayback}
              className="flex items-center px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
              title={isPlaying ? "Pause" : "Lecture"}
            >
              {isPlaying ? (
                <Pause className="h-4 w-4" />
              ) : (
                <Play className="h-4 w-4" />
              )}
            </button>

            <button
              onClick={downloadPreview}
              className="flex items-center px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
              title="Télécharger l'aperçu"
            >
              <Download className="h-4 w-4" />
            </button>
          </>
        )}
      </div>

      {/* Hidden Audio Element */}
      <audio
        ref={audioRef}
        onEnded={handleAudioEnd}
        onError={() => setError("Erreur lors du chargement de l'audio")}
        className="hidden"
      />

      {/* Info */}
      <div className="mt-4 text-xs text-gray-500">
        💡 Cet aperçu vous permet de tester la voix avant de convertir votre document complet.
        La qualité sera identique pour votre livre audio.
      </div>
    </div>
  );
}