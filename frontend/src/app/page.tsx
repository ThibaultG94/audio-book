'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import FileUpload from '@/components/FileUpload'
import VoiceSelectionPanel from '@/components/VoiceSelectionPanel'
import VoicePreview from '@/components/VoicePreview'
import { api } from '@/lib/api'
import type { PreviewVoiceInfo, FileUploadResponse } from '@/lib/types'

export default function HomePage() {
  const router = useRouter()
  const [selectedVoice, setSelectedVoice] = useState<PreviewVoiceInfo | null>(null)
  const [uploadedFileId, setUploadedFileId] = useState<string | null>(null)
  const [isConverting, setIsConverting] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  
  const handleFileUploaded = (response: FileUploadResponse) => {
    setUploadedFileId(response.file_id)
    setIsLoading(false)
  }
  
  const handleVoiceSelect = (voice: PreviewVoiceInfo) => {
    setSelectedVoice(voice)
  }
  
  const handleStartConversion = async () => {
    if (!selectedVoice || !uploadedFileId) return
    
    setIsConverting(true)
    try {
      const response = await api.startConversion({
        file_id: uploadedFileId,
        voice_model: selectedVoice.model_path,
        length_scale: 1.0,
        noise_scale: 0.667,
        noise_w: 0.8,
        sentence_silence: 0.35,
        output_format: 'wav'
      })
      
      router.push(`/convert/${response.job_id}`)
    } catch (error) {
      console.error('Conversion failed:', error)
      setIsConverting(false)
    }
  }
  
  const handleVoiceTest = (voiceModel: string, settings: any) => {
    console.log('Voice test:', voiceModel, settings)
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-3">
            <span className="text-3xl">📚</span>
            <h1 className="text-3xl font-bold text-gray-900">
              Book to Audiobook Converter
            </h1>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Step 1: Prominent Voice Selection */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">
            🎤 Choose Your AI Voice
          </h2>
          
          {/* Enhanced Voice Selector - more prominent */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <VoiceSelectionPanel
              onVoiceSelect={handleVoiceSelect}
              onStartConversion={handleStartConversion}
            />
            
            {/* Voice Preview integrated */}
            {selectedVoice && (
              <div className="mt-6 pt-6 border-t">
                <VoicePreview
                  onVoiceTest={handleVoiceTest}
                  className="mt-4"
                />
              </div>
            )}
          </div>
        </div>
        
        {/* Step 2: File Upload */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">
            📚 Upload Your Book
          </h2>
          <FileUpload 
            onFileUploaded={handleFileUploaded}
            isLoading={isLoading}
          />
        </div>
        
        {/* Step 3: Start Conversion */}
        {selectedVoice && uploadedFileId && (
          <div className="text-center">
            <button
              onClick={handleStartConversion}
              disabled={isConverting}
              className="px-8 py-4 bg-gradient-to-r from-purple-500 to-blue-500 text-white font-bold rounded-lg hover:from-purple-600 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isConverting ? 'Starting...' : '🚀 Start Conversion'}
            </button>
          </div>
        )}
      </main>
    </div>
  )
}