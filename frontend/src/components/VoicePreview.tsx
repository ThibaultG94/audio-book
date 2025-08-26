"use client";

import { useState, useRef, useEffect } from "react";
import { Play, Pause, Volume2, Settings, Loader2, Download, AlertCircle, HelpCircle, RefreshCw, ChevronDown, ChevronUp } from "lucide-react";
import { VoiceSelector } from "./VoiceSelector";

interface VoicePreviewProps {
  onVoiceTest?: (voice: string, settings: VoiceSettings) => void;
  className?: string;
}

interface VoiceSettings {
  length_scale: number;
  noise_scale: number;
  noise_w: number;
  sentence_silence: number;
}

interface VoiceMetadata {
  name: string;
  display_name: string;
  speaker: {
    gender: string;
    age_range: string;
    voice_style: string;
  };
  technical: {
    quality: string;
    file_size_mb: number;
  };
  description: string;
  best_for: string;
  avatar: string;
  color: string;
  model_path: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const DEFAULT_PREVIEW_TEXT = "Bonjour ! Ceci est un aperçu de la voix française pour la conversion de vos livres audio. Vous pouvez ajuster la vitesse, l'expressivité et d'autres paramètres selon vos préférences.";

export function VoicePreview({ onVoiceTest, className = "" }: VoicePreviewProps) {
  const [previewText, setPreviewText] = useState(DEFAULT_PREVIEW_TEXT);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentAudioUrl, setCurrentAudioUrl] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [showVoiceSelector, setShowVoiceSelector] = useState(true);
  const [showHelp, setShowHelp] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedVoiceMetadata, setSelectedVoiceMetadata] = useState<VoiceMetadata | null>(null);
  
  const [settings, setSettings] = useState<VoiceSettings>({
    length_scale: 1.0,
    noise_scale: 0.667,
    noise_w: 0.8,
    sentence_silence: 0.35
  });
  
  const [selectedVoice, setSelectedVoice] = useState("");
  
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handleVoiceSelect = (voicePath: string, metadata: VoiceMetadata) => {
    setSelectedVoice(voicePath);
    setSelectedVoiceMetadata(metadata);
    setError(null);
    
    // Auto-adjust settings based on voice characteristics
    if (metadata.technical.quality === "high") {
      setSettings(prev => ({
        ...prev,
        noise_scale: 0.8,
        sentence_silence: 0.4
      }));
    } else if (metadata.technical.quality === "low") {
      setSettings(prev => ({
        ...prev,
        length_scale: 1.1,
        sentence_silence: 0.3
      }));
    }
  };

  const generatePreview = async () => {
    if (!previewText.trim()) {
      setError("Veuillez entrer du texte pour l'aperçu");
      return;
    }

    if (previewText.length > 500) {
      setError("Le texte est trop long (maximum 500 caractères)");
      return;
    }

    if (!selectedVoice) {
      setError("Veuillez sélectionner une voix");
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/preview/tts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          text: previewText,
          voice_model: selectedVoice,
          length_scale: settings.length_scale,
          noise_scale: settings.noise_scale,
          noise_w: settings.noise_w,
          sentence_silence: settings.sentence_silence
        })
      });

      if (!response.ok) {
        const contentType = response.headers.get("content-type");
        
        if (contentType && contentType.includes("text/html")) {
          throw new Error("Backend non accessible - vérifiez que FastAPI tourne sur le port 8000");
        }
        
        let errorMessage = `Erreur HTTP ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          errorMessage = await response.text() || errorMessage;
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      
      if (!data.audio_url) {
        throw new Error("Réponse invalide - pas d'URL audio");
      }
      
      const fullAudioUrl = `${API_BASE_URL}${data.audio_url}`;
      setCurrentAudioUrl(fullAudioUrl);
      
      // Auto-play the preview
      if (audioRef.current) {
        audioRef.current.src = fullAudioUrl;
        try {
          await audioRef.current.play();
          setIsPlaying(true);
        } catch (playError) {
          console.warn("Auto-play failed:", playError);
        }
      }

      // Notify parent component
      onVoiceTest?.(selectedVoice, settings);

    } catch (err) {
      console.error("Preview generation error:", err);
      
      let errorMessage = "Erreur inconnue";
      if (err instanceof Error) {
        errorMessage = err.message;
      }
      
      if (errorMessage.includes("fetch") || errorMessage.includes("NetworkError")) {
        errorMessage = `Backend non accessible. Vérifiez que FastAPI tourne sur ${API_BASE_URL}`;
      }
      
      setError(errorMessage);
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
    setError(null);
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
    <div className={`bg-white rounded-xl border border-gray-200 shadow-sm ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-100">
        <h3 className="text-xl font-semibold text-gray-900 flex items-center">
          <Volume2 className="h-6 w-6 mr-3 text-blue-600" />
          Test de voix interactif
        </h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowHelp(!showHelp)}
            className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            title="Aide sur les paramètres"
          >
            <HelpCircle className="h-4 w-4" />
          </button>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Paramètres avancés"
          >
            <Settings className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Help Panel */}
        {showHelp && (
          <div className="p-5 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl">
            <h4 className="font-semibold text-blue-900 mb-4 text-lg">🎓 Guide d'utilisation</h4>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-3">
                <div className="p-3 bg-white/60 rounded-lg">
                  <strong className="text-blue-900">1. Choisir une voix</strong>
                  <p className="text-blue-700 mt-1">Sélectionnez parmi les voix disponibles selon votre usage (livre audio, actualités, etc.)</p>
                </div>
                <div className="p-3 bg-white/60 rounded-lg">
                  <strong className="text-blue-900">2. Saisir le texte</strong>
                  <p className="text-blue-700 mt-1">Entrez jusqu'à 500 caractères pour tester la voix sur votre contenu</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="p-3 bg-white/60 rounded-lg">
                  <strong className="text-blue-900">3. Ajuster les paramètres</strong>
                  <p className="text-blue-700 mt-1">Modifiez vitesse, expressivité et pauses selon vos préférences</p>
                </div>
                <div className="p-3 bg-white/60 rounded-lg">
                  <strong className="text-blue-900">4. Valider et convertir</strong>
                  <p className="text-blue-700 mt-1">Une fois satisfait, utilisez ces paramètres pour votre livre audio</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Voice Selection */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-medium text-gray-900">
              1. Sélection de la voix
            </h4>
            <button
              onClick={() => setShowVoiceSelector(!showVoiceSelector)}
              className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-800"
            >
              {showVoiceSelector ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              <span>{showVoiceSelector ? "Masquer" : "Afficher"} les voix</span>
            </button>
          </div>

          {/* Selected Voice Summary */}
          {selectedVoiceMetadata && (
            <div className="flex items-center p-4 bg-green-50 border border-green-200 rounded-lg">
              <div 
                className="w-10 h-10 rounded-full flex items-center justify-center text-white font-medium mr-4"
                style={{ backgroundColor: selectedVoiceMetadata.color }}
              >
                {selectedVoiceMetadata.avatar}
              </div>
              <div className="flex-1">
                <div className="font-medium text-green-900">
                  {selectedVoiceMetadata.display_name}
                </div>
                <div className="text-sm text-green-700">
                  {selectedVoiceMetadata.description} • {selectedVoiceMetadata.technical.file_size_mb}MB
                </div>
              </div>
              <div className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded-full">
                {selectedVoiceMetadata.technical.quality.toUpperCase()}
              </div>
            </div>
          )}

          {/* Voice Selector */}
          {showVoiceSelector && (
            <VoiceSelector
              selectedVoice={selectedVoice}
              onVoiceSelect={handleVoiceSelect}
              usageFilter="audiobook"
            />
          )}
        </div>

        {/* Text Input */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-medium text-gray-900">
              2. Texte d'aperçu
            </h4>
            <button
              onClick={resetPreviewText}
              className="text-sm text-blue-600 hover:text-blue-800 underline"
            >
              Texte par défaut
            </button>
          </div>
          
          <textarea
            value={previewText}
            onChange={(e) => setPreviewText(e.target.value)}
            placeholder="Entrez le texte que vous souhaitez entendre..."
            maxLength={500}
            rows={4}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none bg-white leading-relaxed"
            style={{ 
              fontSize: '15px',
              lineHeight: '1.6',
              color: '#111827',
              fontWeight: '400'
            }}
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>{previewText.length}/500 caractères</span>
            <span>~{Math.ceil(previewText.split(' ').length / 2.5)} secondes d'audio</span>
          </div>
        </div>

        {/* Advanced Settings */}
        {showSettings && selectedVoiceMetadata && (
          <div className="space-y-4">
            <h4 className="text-lg font-medium text-gray-900">
              3. Paramètres avancés
            </h4>
            
            <div className="grid md:grid-cols-2 gap-6 p-4 bg-gray-50 rounded-lg">
              {/* Speed */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Vitesse de parole : {settings.length_scale}x
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
                  <span>0.5x (rapide)</span>
                  <span>1.0x (normale)</span>
                  <span>2.0x (lente)</span>
                </div>
              </div>
              
              {/* Expressivity */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Expressivité : {settings.noise_scale}
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
                  <span>0.0 (monotone)</span>
                  <span>0.5 (équilibrée)</span>
                  <span>1.0 (très expressive)</span>
                </div>
              </div>

              {/* Pitch Stability */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stabilité du pitch : {settings.noise_w}
                </label>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.1"
                  value={settings.noise_w}
                  onChange={(e) => setSettings({
                    ...settings,
                    noise_w: parseFloat(e.target.value)
                  })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0.0 (très stable)</span>
                  <span>0.5 (équilibrée)</span>
                  <span>1.0 (très variable)</span>
                </div>
              </div>

              {/* Sentence Pause */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Pause entre phrases : {settings.sentence_silence}s
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.05"
                  value={settings.sentence_silence}
                  onChange={(e) => setSettings({
                    ...settings,
                    sentence_silence: parseFloat(e.target.value)
                  })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0.1s (rapide)</span>
                  <span>0.35s (naturelle)</span>
                  <span>1.0s (posée)</span>
                </div>
              </div>
            </div>

            {/* Reset to defaults */}
            <button
              onClick={() => setSettings({
                length_scale: 1.0,
                noise_scale: 0.667,
                noise_w: 0.8,
                sentence_silence: 0.35
              })}
              className="text-sm text-gray-600 hover:text-gray-800 underline"
            >
              Réinitialiser aux valeurs par défaut
            </button>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start">
              <AlertCircle className="h-5 w-5 text-red-400 mr-3 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm text-red-800 font-medium">Erreur de génération</p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="space-y-4">
          <h4 className="text-lg font-medium text-gray-900">
            4. Génération et écoute
          </h4>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={generatePreview}
                disabled={isGenerating || !previewText.trim() || !selectedVoice}
                className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium text-sm"
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
                    className="flex items-center px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
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
                    className="flex items-center px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                    title="Télécharger l'aperçu"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                </>
              )}
            </div>
            
            {selectedVoiceMetadata && (
              <div className="text-right">
                <div className="text-sm text-gray-600">
                  Voix sélectionnée : <strong>{selectedVoiceMetadata.name}</strong>
                </div>
                <div className="text-xs text-gray-500">
                  {selectedVoiceMetadata.technical.quality} quality • {selectedVoiceMetadata.technical.file_size_mb}MB
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Settings Summary */}
        {!showSettings && (settings.length_scale !== 1.0 || settings.noise_scale !== 0.667) && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center mb-1">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              <span className="text-sm font-medium text-green-800">Paramètres personnalisés</span>
            </div>
            <div className="text-xs text-green-700 space-y-1">
              <p>Vitesse: {settings.length_scale}x • Expressivité: {settings.noise_scale} • Pitch: {settings.noise_w} • Pause: {settings.sentence_silence}s</p>
            </div>
          </div>
        )}
      </div>

      {/* Hidden Audio Element */}
      <audio
        ref={audioRef}
        onEnded={handleAudioEnd}
        onError={() => setError("Erreur lors du chargement de l'audio")}
        className="hidden"
      />

      {/* Footer */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 rounded-b-xl">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-4">
            <span>💡 Testez plusieurs voix pour trouver celle qui convient le mieux</span>
            {currentAudioUrl && (
              <span>🎵 Audio généré avec Piper TTS</span>
            )}
          </div>
          <span>API: {API_BASE_URL}</span>
        </div>
      </div>
    </div>
  );
}