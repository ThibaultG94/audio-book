"use client";

import { useState, useRef, useEffect } from "react";
import { Play, Pause, Volume2, Settings, Loader2, Download, AlertCircle, HelpCircle, RefreshCw } from "lucide-react";

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

interface VoiceModel {
  model_path: string;
  name: string;
  full_path: string;
  language?: {
    name_english: string;
    name_native: string;
    code: string;
  };
  dataset?: string;
  quality?: string;
  sample_rate?: number;
  file_size_mb?: number;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const DEFAULT_PREVIEW_TEXT = "Bonjour ! Ceci est un aperçu de la voix française pour la conversion de vos livres audio. Vous pouvez ajuster la vitesse, l'expressivité et d'autres paramètres selon vos préférences.";

export function VoicePreview({ onVoiceTest, className = "" }: VoicePreviewProps) {
  const [previewText, setPreviewText] = useState(DEFAULT_PREVIEW_TEXT);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentAudioUrl, setCurrentAudioUrl] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [showPresets, setShowPresets] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableVoices, setAvailableVoices] = useState<VoiceModel[]>([]);
  const [isLoadingVoices, setIsLoadingVoices] = useState(false);
  const [voiceLoadError, setVoiceLoadError] = useState<string | null>(null);
  
  const [settings, setSettings] = useState<VoiceSettings>({
    length_scale: 1.0,
    noise_scale: 0.667,
    noise_w: 0.8,
    sentence_silence: 0.35
  });
  
  const [selectedVoice, setSelectedVoice] = useState("");
  
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Load presets and parameter info
  const [presets, setPresets] = useState<any>({});

  useEffect(() => {
    loadPresetsAndDefaults();
    loadAvailableVoices();
  }, []);

  const loadPresetsAndDefaults = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/preview/parameters/defaults`);
      if (response.ok) {
        const data = await response.json();
        setPresets(data.presets || {});
      }
    } catch (err) {
      console.warn("Could not load presets:", err);
    }
  };

  const loadAvailableVoices = async () => {
    setIsLoadingVoices(true);
    setVoiceLoadError(null);
    
    try {
      console.log("🔍 Loading voices from API...");
      const response = await fetch(`${API_BASE_URL}/api/preview/voices`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log("📊 API Response:", data);
      
      const voices = data.voices || [];
      setAvailableVoices(voices);
      
      // Set default voice intelligently
      if (voices.length > 0) {
        // Priority: medium quality > low quality > any available
        const mediumVoice = voices.find((v: VoiceModel) => v.quality === "medium");
        const lowVoice = voices.find((v: VoiceModel) => v.quality === "low");
        const defaultVoice = mediumVoice || lowVoice || voices[0];
        
        console.log("🎤 Setting default voice:", defaultVoice.model_path);
        setSelectedVoice(defaultVoice.model_path);
      } else if (data.default_voice) {
        console.log("🎤 Using backend default voice:", data.default_voice);
        setSelectedVoice(data.default_voice);
      } else {
        // Fallback to hardcoded default
        setSelectedVoice("voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx");
      }
      
    } catch (err) {
      console.error("❌ Voice loading error:", err);
      const errorMsg = err instanceof Error ? err.message : "Erreur inconnue";
      setVoiceLoadError(`Impossible de charger les voix: ${errorMsg}`);
      
      // Set fallback voice on error
      setSelectedVoice("voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx");
    } finally {
      setIsLoadingVoices(false);
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

    setIsGenerating(true);
    setError(null);

    try {
      console.log("🎤 Generating preview with voice:", selectedVoice);
      console.log("⚙️ Parameters:", settings);
      
      const previewUrl = `${API_BASE_URL}/api/preview/tts`;
      
      const response = await fetch(previewUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          text: previewText,
          voice_model: selectedVoice || undefined,
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
      console.log("✅ Preview generated:", data);
      
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

  const getVoiceDisplayName = (voice: VoiceModel) => {
    if (voice.language && voice.dataset) {
      const quality = voice.quality ? ` (${voice.quality})` : '';
      const size = voice.file_size_mb ? ` - ${Math.round(voice.file_size_mb)}MB` : '';
      return `${voice.language.name_native} - ${voice.dataset}${quality}${size}`;
    }
    return voice.name || voice.model_path;
  };

  const applyPreset = (presetName: string) => {
    const preset = presets[presetName];
    if (preset && preset.parameters) {
      setSettings({
        length_scale: preset.parameters.length_scale,
        noise_scale: preset.parameters.noise_scale,
        noise_w: preset.parameters.noise_w,
        sentence_silence: preset.parameters.sentence_silence
      });
      setError(null);
      console.log(`Applied preset: ${preset.name}`);
    }
  };

  const getPresetSamples = () => {
    return {
      "audiobook_natural": "Voici un extrait de roman lu de manière confortable pour une écoute prolongée.",
      "news_fast": "Voici un bulletin d'information lu de façon claire et efficace.",
      "storytelling": "Il était une fois, dans un royaume lointain, une princesse aux pouvoirs magiques...",
      "learning_careful": "Cette leçon explique les concepts fondamentaux de la physique quantique.",
      "meditation_calm": "Respirez profondément. Laissez vos pensées s'apaiser doucement."
    };
  };

  const applyPresetWithSample = (presetName: string) => {
    applyPreset(presetName);
    const samples = getPresetSamples();
    const sampleText = samples[presetName as keyof typeof samples];
    if (sampleText) {
      setPreviewText(sampleText);
    }
  };

  // Count total voices (including fallback)
  const totalVoices = availableVoices.length + (selectedVoice && !availableVoices.find(v => v.model_path === selectedVoice) ? 1 : 0);

  return (
    <div className={`bg-white rounded-xl border border-gray-200 shadow-sm p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900 flex items-center">
          <Volume2 className="h-6 w-6 mr-3 text-blue-600" />
          Aperçu de la voix
        </h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowPresets(!showPresets)}
            className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
            title="Configurations prédéfinies"
          >
            <span className="text-sm">🎨</span>
          </button>
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

      {/* Help Panel */}
      {showHelp && (
        <div className="mb-6 p-5 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl">
          <h4 className="font-semibold text-blue-900 mb-4 text-lg">🎓 Guide des paramètres vocaux</h4>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div className="space-y-3">
              <div className="p-3 bg-white/60 rounded-lg">
                <strong className="text-blue-900">Vitesse de parole</strong>
                <p className="text-blue-700 mt-1">Contrôle la rapidité d'élocution sans déformer la voix</p>
                <div className="text-blue-600 text-xs mt-2">
                  • 0.8x = lecture rapide (actualités)<br/>
                  • 1.0x = vitesse normale (conversation)<br/>
                  • 1.2x = lecture posée (apprentissage)
                </div>
              </div>
              <div className="p-3 bg-white/60 rounded-lg">
                <strong className="text-blue-900">Expressivité</strong>
                <p className="text-blue-700 mt-1">Variations naturelles qui rendent la voix vivante</p>
                <div className="text-blue-600 text-xs mt-2">
                  • 0.0 = voix robotique, monotone<br/>
                  • 0.667 = naturellement expressive<br/>
                  • 1.0 = très expressive (risque d'artéfacts)
                </div>
              </div>
            </div>
            <div className="space-y-3">
              <div className="p-3 bg-white/60 rounded-lg">
                <strong className="text-blue-900">Stabilité du pitch</strong>
                <p className="text-blue-700 mt-1">Contrôle les variations de hauteur de voix</p>
                <div className="text-blue-600 text-xs mt-2">
                  • 0.0 = pitch très stable (institutionnel)<br/>
                  • 0.8 = variations naturelles<br/>
                  • 1.0 = très variable (dramatique)
                </div>
              </div>
              <div className="p-3 bg-white/60 rounded-lg">
                <strong className="text-blue-900">Pause entre phrases</strong>
                <p className="text-blue-700 mt-1">Durée des silences pour le confort d'écoute</p>
                <div className="text-blue-600 text-xs mt-2">
                  • 0.1s = lecture très rapide<br/>
                  • 0.35s = pause naturelle<br/>
                  • 0.8s = lecture méditative
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Presets Panel */}
      {showPresets && Object.keys(presets).length > 0 && (
        <div className="mb-6 p-5 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl">
          <h4 className="font-semibold text-green-900 mb-4 text-lg">🎨 Configurations prédéfinies</h4>
          <div className="grid md:grid-cols-2 gap-3">
            {Object.entries(presets).map(([key, preset]: [string, any]) => (
              <button
                key={key}
                onClick={() => applyPresetWithSample(key)}
                className="p-4 bg-white/80 hover:bg-white border border-green-200 rounded-lg text-left transition-all hover:shadow-sm group"
              >
                <div className="font-medium text-green-900 group-hover:text-green-700 mb-1">
                  {preset.name}
                </div>
                <div className="text-sm text-green-700 mb-2">
                  {preset.description}
                </div>
                <div className="text-xs text-green-600">
                  {preset.best_for?.join(" • ") || "Usage général"}
                </div>
                <div className="text-xs text-gray-500 mt-2 font-mono">
                  Speed: {preset.parameters?.length_scale}x • Express: {preset.parameters?.noise_scale}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Voice Selection with Better Error Handling */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-700">
            Voix disponibles
          </label>
          <button
            onClick={loadAvailableVoices}
            disabled={isLoadingVoices}
            className="text-xs text-blue-600 hover:text-blue-800 flex items-center disabled:text-gray-400"
          >
            <RefreshCw className={`h-3 w-3 mr-1 ${isLoadingVoices ? 'animate-spin' : ''}`} />
            {isLoadingVoices ? "Chargement..." : "Actualiser"}
          </button>
        </div>
        
        <select
          value={selectedVoice}
          onChange={(e) => setSelectedVoice(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
        >
          {availableVoices.length > 0 ? (
            availableVoices.map((voice) => (
              <option key={voice.model_path} value={voice.model_path}>
                {getVoiceDisplayName(voice)}
              </option>
            ))
          ) : (
            <option value={selectedVoice}>
              Siwis (French) - Low Quality (défaut)
            </option>
          )}
        </select>
        
        {/* Voice Status */}
        <div className="mt-3 p-3 rounded-lg border-l-4 border-l-blue-500 bg-blue-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-sm">
                {voiceLoadError ? (
                  <div className="flex items-center text-red-700">
                    <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                    <strong>Erreur de chargement</strong>
                  </div>
                ) : totalVoices > 1 ? (
                  <div className="flex items-center text-green-700">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    <strong>{totalVoices} voix disponibles</strong>
                  </div>
                ) : (
                  <div className="flex items-center text-blue-700">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                    <strong>1 voix installée</strong> (défaut)
                  </div>
                )}
                
                <div className="text-xs text-gray-600 mt-1">
                  {voiceLoadError ? (
                    voiceLoadError
                  ) : totalVoices <= 1 ? (
                    "Installez plus de voix pour de meilleures options de qualité"
                  ) : (
                    "Sélectionnez la voix qui convient le mieux à votre usage"
                  )}
                </div>
              </div>
              
              {totalVoices <= 1 && (
                <div className="text-xs bg-gradient-to-r from-purple-100 to-blue-100 text-purple-800 px-3 py-1 rounded-full border border-purple-200">
                  Amélioration disponible
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-3">
              {totalVoices <= 1 && (
                <button
                  onClick={() => window.open(`${API_BASE_URL}/api/preview/voices/install-guide`, '_blank')}
                  className="text-xs bg-blue-600 text-white px-3 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Guide installation
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Advanced Settings */}
      {showSettings && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg space-y-4">
          <h4 className="text-sm font-semibold text-gray-900">Paramètres avancés</h4>
          
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

          {/* Reset to defaults */}
          <button
            onClick={() => setSettings({
              length_scale: 1.0,
              noise_scale: 0.667,
              noise_w: 0.8,
              sentence_silence: 0.35
            })}
            className="text-xs text-gray-600 hover:text-gray-800 underline"
          >
            Réinitialiser aux valeurs par défaut
          </button>
        </div>
      )}

      {/* Preview Text Input */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-700">
            Texte d'aperçu
          </label>
          <button
            onClick={resetPreviewText}
            className="text-xs text-blue-600 hover:text-blue-800 underline"
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
        <div className="flex justify-between mt-2">
          <span className="text-xs text-gray-500">
            {previewText.length}/500 caractères
          </span>
          <span className="text-xs text-gray-500">
            ~{Math.ceil(previewText.split(' ').length / 2.5)} secondes d'audio
          </span>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-red-400 mr-3 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-red-800 font-medium">Erreur de génération</p>
              <p className="text-sm text-red-700 mt-1">{error}</p>
              <div className="mt-3 text-xs text-red-600">
                <p className="font-medium">💡 Vérifications :</p>
                <ul className="list-disc list-inside mt-1 space-y-1">
                  <li>Backend FastAPI actif sur {API_BASE_URL}</li>
                  <li>Route preview configurée dans main.py</li>
                  <li>Modèle vocal présent dans backend/voices/</li>
                  <li>Test manuel : <a href={`${API_BASE_URL}/health`} className="underline" target="_blank" rel="noopener noreferrer">health check</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={generatePreview}
              disabled={isGenerating || !previewText.trim()}
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
        </div>
      </div>

      {/* Settings Summary */}
      {!showSettings && (settings.length_scale !== 1.0 || settings.noise_scale !== 0.667) && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center mb-1">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            <span className="text-sm font-medium text-green-800">Paramètres personnalisés</span>
          </div>
          <div className="text-xs text-green-700 space-y-1">
            <p>Vitesse: {settings.length_scale}x • Expressivité: {settings.noise_scale} • Pitch: {settings.noise_w}</p>
          </div>
        </div>
      )}

      {/* Hidden Audio Element */}
      <audio
        ref={audioRef}
        onEnded={handleAudioEnd}
        onError={() => setError("Erreur lors du chargement de l'audio")}
        className="hidden"
      />

      {/* Tech note */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>💡 Appel direct FastAPI {API_BASE_URL}</span>
          {currentAudioUrl && (
            <span>🎵 Audio généré avec Piper TTS</span>
          )}
        </div>
      </div>
    </div>
  );
}