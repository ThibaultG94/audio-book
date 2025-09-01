'use client'

import { useState } from 'react'
import { PreviewVoiceInfo } from '@/lib/types'

interface VoiceCardProps {
  voice: PreviewVoiceInfo
  isSelected: boolean
  isRecommended?: string | null
  onSelect: () => void
  onPreview: () => void
}

export default function VoiceCard({
  voice,
  isSelected,
  isRecommended,
  onSelect,
  onPreview
}: VoiceCardProps) {
  const [isHovered, setIsHovered] = useState(false)
  
  // Extract voice metadata
  const getVoiceGender = () => {
    if (voice.dataset?.includes('siwis') || voice.dataset?.includes('mls')) return 'female'
    if (voice.dataset?.includes('tom') || voice.dataset?.includes('gilles')) return 'male'
    return 'neutral'
  }
  
  const gender = getVoiceGender()
  const genderIcon = gender === 'female' ? '👩' : gender === 'male' ? '👨' : '🎭'
  const qualityColor = {
    'low': 'bg-yellow-100 text-yellow-800',
    'medium': 'bg-blue-100 text-blue-800',
    'high': 'bg-green-100 text-green-800'
  }[voice.quality || 'medium']
  
  return (
    <div
      className={`
        relative p-6 rounded-xl transition-all duration-300 cursor-pointer
        ${isSelected 
          ? 'bg-gradient-to-br from-purple-500 to-blue-500 text-white shadow-xl scale-105' 
          : 'bg-white hover:shadow-lg border-2 border-gray-200 hover:border-purple-300'
        }
      `}
      onClick={onSelect}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Recommendation Badge */}
      {isRecommended && (
        <div className="absolute -top-3 -right-3 bg-gradient-to-r from-yellow-400 to-orange-400 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg animate-pulse">
          ⭐ {isRecommended}
        </div>
      )}
      
      {/* Voice Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-3xl">{genderIcon}</span>
          <div>
            <h3 className={`font-bold text-lg ${isSelected ? 'text-white' : 'text-gray-800'}`}>
              {voice.name}
            </h3>
            <p className={`text-sm ${isSelected ? 'text-blue-100' : 'text-gray-500'}`}>
              {voice.dataset}
            </p>
          </div>
        </div>
        
        {/* Quality Badge */}
        <span className={`
          px-3 py-1 rounded-full text-xs font-semibold
          ${isSelected ? 'bg-white/20 text-white' : qualityColor}
        `}>
          {voice.quality?.toUpperCase() || 'MEDIUM'}
        </span>
      </div>
      
      {/* Voice Stats */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className={`text-sm ${isSelected ? 'text-blue-100' : 'text-gray-600'}`}>
          <span className="font-medium">Fréquence:</span> {voice.sample_rate}Hz
        </div>
        <div className={`text-sm ${isSelected ? 'text-blue-100' : 'text-gray-600'}`}>
          <span className="font-medium">Taille:</span> {voice.file_size_mb}MB
        </div>
      </div>
      
      {/* Usage Tags */}
      <div className="flex flex-wrap gap-2 mb-4">
        {voice.recommended_usage?.map((usage) => (
          <span
            key={usage}
            className={`
              px-2 py-1 rounded-md text-xs font-medium
              ${isSelected ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-700'}
            `}
          >
            {usage === 'audiobook' && '📚'} 
            {usage === 'news' && '📰'} 
            {usage === 'storytelling' && '🎭'} 
            {usage}
          </span>
        ))}
      </div>
      
      {/* Preview Button */}
      <button
        onClick={(e) => {
          e.stopPropagation()
          onPreview()
        }}
        className={`
          w-full py-2 px-4 rounded-lg font-medium transition-all duration-200
          ${isSelected 
            ? 'bg-white text-purple-600 hover:bg-blue-50' 
            : 'bg-gradient-to-r from-purple-500 to-blue-500 text-white hover:from-purple-600 hover:to-blue-600'
          }
        `}
      >
        🔊 Tester cette voix
      </button>
      
      {/* Selection Indicator */}
      {isSelected && (
        <div className="absolute top-3 right-3">
          <div className="bg-white rounded-full p-1">
            <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
        </div>
      )}
    </div>
  )
}