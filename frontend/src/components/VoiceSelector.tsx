"use client";

import { useState, useEffect } from "react";
import { Volume2, User, Users, Filter, Star, Zap, Crown, Info } from "lucide-react";

interface VoiceMetadata {
  name: string;
  display_name: string;
  language: {
    code: string;
    name_english: string;
    name_native: string;
  };
  speaker: {
    gender: "female" | "male" | "multi" | "neutral";
    age_range: string;
    voice_style: string;
    accent: string;
    available_speakers?: {
      [key: string]: {
        gender: string;
        style: string;
      };
    };
  };
  technical: {
    quality: "low" | "medium" | "high";
    sample_rate: number;
    dataset: string;
    file_size_mb: number;
    processing_speed: "fast" | "medium" | "slow";
  };
  recommended_usage?: string[]; // Make optional to handle undefined from API
  description: string;
  best_for: string;
  avatar: string;
  color: string;
  model_path: string;
}

interface VoiceSelectorProps {
  selectedVoice?: string;
  onVoiceSelect: (voicePath: string, metadata: VoiceMetadata) => void;
  usageFilter?: string;
  className?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function VoiceSelector({
  selectedVoice,
  onVoiceSelect,
  usageFilter,
  className = ""
}: VoiceSelectorProps) {
  const [voices, setVoices] = useState<VoiceMetadata[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilters, setActiveFilters] = useState({
    gender: "all",
    quality: "all",
    usage: usageFilter || "all"
  });
  const [viewMode, setViewMode] = useState<"cards" | "list">("cards");

  useEffect(() => {
    loadVoices();
  }, []);

  const loadVoices = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/preview/voices`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      const voicesData = data.voices || [];
      
      // Transform API data to match our interface and ensure recommended_usage is always array
      const transformedVoices: VoiceMetadata[] = voicesData.map((voice: any) => ({
        ...voice,
        model_path: voice.model_path,
        recommended_usage: Array.isArray(voice.recommended_usage) 
          ? voice.recommended_usage 
          : [], // Default to empty array if undefined or not array
      }));
      
      setVoices(transformedVoices);
    } catch (err) {
      console.error("Error loading voices:", err);
      setError(err instanceof Error ? err.message : "Failed to load voices");
    } finally {
      setIsLoading(false);
    }
  };

  const filteredVoices = voices.filter(voice => {
    // Gender filter
    if (activeFilters.gender !== "all" && voice.speaker.gender !== activeFilters.gender) {
      return false;
    }
    
    // Quality filter
    if (activeFilters.quality !== "all" && voice.technical.quality !== activeFilters.quality) {
      return false;
    }
    
    // Usage filter - now safely handles undefined/empty arrays
    if (activeFilters.usage !== "all") {
      const usageArray = voice.recommended_usage || [];
      if (!usageArray.includes(activeFilters.usage)) {
        return false;
      }
    }
    
    return true;
  });

  const getGenderIcon = (gender: string) => {
    switch (gender) {
      case "female": return "👩‍💼";
      case "male": return "👨‍💼";
      case "multi": return "👫";
      default: return "🎭";
    }
  };

  const getQualityBadge = (quality: string) => {
    const badges = {
      low: { color: "bg-yellow-100 text-yellow-800", icon: <Zap className="h-3 w-3" /> },
      medium: { color: "bg-blue-100 text-blue-800", icon: <Star className="h-3 w-3" /> },
      high: { color: "bg-purple-100 text-purple-800", icon: <Crown className="h-3 w-3" /> }
    };
    return badges[quality as keyof typeof badges] || badges.medium;
  };

  const getGenderLabel = (gender: string) => {
    const labels = {
      female: "Femme",
      male: "Homme", 
      multi: "Multiple",
      neutral: "Neutre"
    };
    return labels[gender as keyof typeof labels] || gender;
  };

  const VoiceCard = ({ voice }: { voice: VoiceMetadata }) => {
    const qualityBadge = getQualityBadge(voice.technical.quality);
    const isSelected = selectedVoice === voice.model_path;
    
    // Safe access to recommended_usage
    const recommendedUsage = voice.recommended_usage || [];
    
    return (
      <div
        onClick={() => onVoiceSelect(voice.model_path, voice)}
        className={`
          relative p-6 rounded-xl border-2 cursor-pointer transition-all duration-200 group
          ${isSelected 
            ? "border-blue-500 bg-blue-50 shadow-lg" 
            : "border-gray-200 hover:border-gray-300 hover:shadow-md bg-white"
          }
        `}
      >
        {/* Selection indicator */}
        {isSelected && (
          <div className="absolute top-3 right-3">
            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
              <div className="w-2 h-2 bg-white rounded-full"></div>
            </div>
          </div>
        )}
        
        {/* Voice Avatar & Basic Info */}
        <div className="flex items-start space-x-4 mb-4">
          <div 
            className="w-16 h-16 rounded-full flex items-center justify-center text-2xl font-medium text-white"
            style={{ backgroundColor: voice.color }}
          >
            {voice.avatar}
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-lg text-gray-900 truncate">
              {voice.display_name}
            </h3>
            <p className="text-sm text-gray-600 mb-2">
              {getGenderLabel(voice.speaker.gender)} • {voice.technical.dataset}
            </p>
            
            {/* Quality & Size */}
            <div className="flex items-center space-x-2">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${qualityBadge.color}`}>
                {qualityBadge.icon}
                <span className="ml-1">{voice.technical.quality.toUpperCase()}</span>
              </span>
              <span className="text-xs text-gray-500">
                {voice.technical.file_size_mb}MB
              </span>
            </div>
          </div>
        </div>

        {/* Description */}
        <p className="text-sm text-gray-700 mb-4 line-clamp-2">
          {voice.description}
        </p>

        {/* Usage Tags - Safe rendering */}
        {recommendedUsage.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-4">
            {recommendedUsage.slice(0, 3).map(usage => (
              <span
                key={usage}
                className="inline-block px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md"
              >
                {usage}
              </span>
            ))}
            {recommendedUsage.length > 3 && (
              <span className="inline-block px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-md">
                +{recommendedUsage.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Best For */}
        <div className="flex items-start space-x-2">
          <Info className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-gray-600 leading-relaxed">
            <strong>Idéal pour :</strong> {voice.best_for}
          </p>
        </div>

        {/* Multi-speaker info */}
        {voice.speaker.available_speakers && (
          <div className="mt-3 p-2 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-600 font-medium mb-1">Locuteurs disponibles :</p>
            <div className="flex space-x-2">
              {Object.entries(voice.speaker.available_speakers).map(([name, info]) => (
                <span
                  key={name}
                  className="text-xs bg-white px-2 py-1 rounded-md text-gray-700"
                >
                  {name} ({info.gender === 'female' ? '♀️' : '♂️'})
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const VoiceListItem = ({ voice }: { voice: VoiceMetadata }) => {
    const qualityBadge = getQualityBadge(voice.technical.quality);
    const isSelected = selectedVoice === voice.model_path;
    
    return (
      <div
        onClick={() => onVoiceSelect(voice.model_path, voice)}
        className={`
          flex items-center p-4 rounded-lg border cursor-pointer transition-all duration-200
          ${isSelected 
            ? "border-blue-500 bg-blue-50" 
            : "border-gray-200 hover:border-gray-300 bg-white"
          }
        `}
      >
        {/* Avatar */}
        <div 
          className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium text-white mr-4 flex-shrink-0"
          style={{ backgroundColor: voice.color }}
        >
          {voice.avatar}
        </div>
        
        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-3 mb-1">
            <h3 className="font-medium text-gray-900 truncate">
              {voice.display_name}
            </h3>
            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${qualityBadge.color}`}>
              {qualityBadge.icon}
              <span className="ml-1">{voice.technical.quality.toUpperCase()}</span>
            </span>
            <span className="text-xs text-gray-500">
              {voice.technical.file_size_mb}MB
            </span>
          </div>
          <p className="text-sm text-gray-600 truncate">
            {getGenderLabel(voice.speaker.gender)} • {voice.description}
          </p>
        </div>
        
        {/* Selection indicator */}
        {isSelected && (
          <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center ml-3">
            <div className="w-2 h-2 bg-white rounded-full"></div>
          </div>
        )}
      </div>
    );
  };

  if (error) {
    return (
      <div className={`p-6 bg-red-50 border border-red-200 rounded-xl ${className}`}>
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
            ❌
          </div>
          <div>
            <h3 className="font-medium text-red-900">Erreur de chargement des voix</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            <button
              onClick={loadVoices}
              className="text-sm text-red-600 hover:text-red-800 underline mt-2"
            >
              Réessayer
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Volume2 className="h-6 w-6 text-blue-600" />
          <div>
            <h3 className="text-xl font-semibold text-gray-900">
              Choisir une voix
            </h3>
            <p className="text-sm text-gray-600">
              {isLoading ? "Chargement..." : `${filteredVoices.length} voix disponibles`}
            </p>
          </div>
        </div>
        
        {/* View Mode Toggle */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode("cards")}
            className={`p-2 rounded-md transition-colors ${
              viewMode === "cards" 
                ? "bg-blue-100 text-blue-700" 
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            <svg className="h-4 w-4" viewBox="0 0 16 16" fill="currentColor">
              <path d="M2 2h4v4H2V2zm6 0h4v4H8V2zM2 8h4v4H2V8zm6 0h4v4H8V8z"/>
            </svg>
          </button>
          <button
            onClick={() => setViewMode("list")}
            className={`p-2 rounded-md transition-colors ${
              viewMode === "list" 
                ? "bg-blue-100 text-blue-700" 
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            <svg className="h-4 w-4" viewBox="0 0 16 16" fill="currentColor">
              <path d="M1 2h14v2H1V2zm0 4h14v2H1V6zm0 4h14v2H1v-2z"/>
            </svg>
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">Filtres :</span>
        </div>
        
        {/* Gender Filter */}
        <select
          value={activeFilters.gender}
          onChange={(e) => setActiveFilters({...activeFilters, gender: e.target.value})}
          className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">Tous genres</option>
          <option value="female">👩 Femme</option>
          <option value="male">👨 Homme</option>
          <option value="multi">👫 Multiple</option>
        </select>

        {/* Quality Filter */}
        <select
          value={activeFilters.quality}
          onChange={(e) => setActiveFilters({...activeFilters, quality: e.target.value})}
          className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">Toutes qualités</option>
          <option value="low">⚡ Rapide (Low)</option>
          <option value="medium">⭐ Équilibrée (Medium)</option>
          <option value="high">👑 Premium (High)</option>
        </select>

        {/* Usage Filter */}
        <select
          value={activeFilters.usage}
          onChange={(e) => setActiveFilters({...activeFilters, usage: e.target.value})}
          className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">Tous usages</option>
          <option value="audiobook">📚 Livre audio</option>
          <option value="news">📰 Actualités</option>
          <option value="storytelling">🎭 Narration</option>
          <option value="educational">🎓 Éducatif</option>
          <option value="documentary">🎬 Documentaire</option>
          <option value="professional">💼 Professionnel</option>
        </select>

        {/* Reset Filters */}
        {(activeFilters.gender !== "all" || activeFilters.quality !== "all" || activeFilters.usage !== (usageFilter || "all")) && (
          <button
            onClick={() => setActiveFilters({
              gender: "all",
              quality: "all", 
              usage: usageFilter || "all"
            })}
            className="text-sm text-blue-600 hover:text-blue-800 underline"
          >
            Réinitialiser
          </button>
        )}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="p-6 bg-gray-100 rounded-xl animate-pulse">
              <div className="flex items-start space-x-4 mb-4">
                <div className="w-16 h-16 bg-gray-300 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-300 rounded mb-2"></div>
                  <div className="h-3 bg-gray-300 rounded w-3/4"></div>
                </div>
              </div>
              <div className="h-3 bg-gray-300 rounded mb-2"></div>
              <div className="h-3 bg-gray-300 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && filteredVoices.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Users className="h-8 w-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Aucune voix trouvée
          </h3>
          <p className="text-gray-600 mb-4">
            Aucune voix ne correspond aux filtres sélectionnés.
          </p>
          <button
            onClick={() => setActiveFilters({
              gender: "all",
              quality: "all",
              usage: "all"
            })}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Afficher toutes les voix
          </button>
        </div>
      )}

      {/* Voice Grid/List */}
      {!isLoading && filteredVoices.length > 0 && (
        <div className={
          viewMode === "cards" 
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            : "space-y-3"
        }>
          {filteredVoices.map((voice) => (
            <div key={voice.model_path}>
              {viewMode === "cards" ? (
                <VoiceCard voice={voice} />
              ) : (
                <VoiceListItem voice={voice} />
              )}
            </div>
          ))}
        </div>
      )}

      {/* Statistics */}
      {!isLoading && filteredVoices.length > 0 && (
        <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="text-center">
              <div className="font-semibold text-blue-900">
                {filteredVoices.filter(v => v.speaker.gender === "female").length}
              </div>
              <div className="text-blue-700">Voix féminines</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-blue-900">
                {filteredVoices.filter(v => v.speaker.gender === "male").length}
              </div>
              <div className="text-blue-700">Voix masculines</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-blue-900">
                {filteredVoices.filter(v => v.technical.quality === "high").length}
              </div>
              <div className="text-blue-700">Haute qualité</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-blue-900">
                {Math.round(filteredVoices.reduce((sum, v) => sum + v.technical.file_size_mb, 0))}MB
              </div>
              <div className="text-blue-700">Taille totale</div>
            </div>
          </div>
        </div>
      )}

      {/* Installation Guide */}
      {!isLoading && voices.length <= 2 && (
        <div className="mt-8 p-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl border border-purple-200">
          <div className="flex items-start space-x-4">
            <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
              <Crown className="h-5 w-5 text-purple-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-purple-900 mb-2">
                🚀 Enrichissez votre collection de voix
              </h3>
              <p className="text-purple-800 mb-4">
                Vous n'avez que {voices.length} voix installées. Ajoutez des voix masculines, 
                féminines et de haute qualité pour une meilleure expérience utilisateur.
              </p>
              
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div className="p-3 bg-white/60 rounded-lg">
                  <h4 className="font-medium text-purple-900 mb-1">🎯 Installation recommandée</h4>
                  <p className="text-sm text-purple-700 mb-2">
                    Pack équilibré avec voix homme/femme
                  </p>
                  <code className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                    ./scripts/install-voices.sh default
                  </code>
                </div>
                
                <div className="p-3 bg-white/60 rounded-lg">
                  <h4 className="font-medium text-purple-900 mb-1">👑 Installation premium</h4>
                  <p className="text-sm text-purple-700 mb-2">
                    Voix haute qualité pour un rendu professionnel
                  </p>
                  <code className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                    ./scripts/install-voices.sh premium
                  </code>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="text-sm text-purple-700">
                  💡 <strong>Voix recommandées :</strong> Tom (♂️), Bernard (♂️), Siwis Medium (♀️)
                </div>
                <button
                  onClick={() => window.open(`${API_BASE_URL}/api/preview/voices/install-guide`, '_blank')}
                  className="px-4 py-2 bg-purple-600 text-white text-sm rounded-md hover:bg-purple-700 transition-colors"
                >
                  Guide d'installation
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}