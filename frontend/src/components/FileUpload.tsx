'use client'

import { useState, useRef } from 'react'
import { api, FileUploadResponse } from '@/lib/api'

interface FileUploadProps {
  onFileUploaded: (response: FileUploadResponse) => void
  onError?: (error: string) => void
  className?: string
}

export default function FileUpload({ onFileUploaded, onError, className = "" }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const allowedTypes = ['application/pdf', 'application/epub+zip']
  const maxSize = 50 * 1024 * 1024 // 50MB

  const validateFile = (file: File): string | null => {
    if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.epub')) {
      return 'Format non supporté. Utilisez PDF ou EPUB.'
    }
    if (file.size > maxSize) {
      return 'Fichier trop volumineux. Maximum 50MB.'
    }
    return null
  }

  const uploadFile = async (file: File) => {
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      onError?.(validationError)
      return
    }

    setIsUploading(true)
    setError(null)
    setUploadProgress(0)

    try {
      // Simulation de progression
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90))
      }, 150)

      const response = await api.uploadFile(file)
      
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      setTimeout(() => {
        onFileUploaded(response)
        setIsUploading(false)
        setUploadProgress(0)
      }, 500)

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur d\'upload'
      setError(errorMessage)
      onError?.(errorMessage)
      setIsUploading(false)
      setUploadProgress(0)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      uploadFile(files[0])
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      uploadFile(files[0])
    }
  }

  const openFileDialog = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className={`${className}`}>
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={openFileDialog}
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all
          ${isDragging 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${isUploading ? 'pointer-events-none opacity-50' : ''}
        `}
      >
        {isUploading ? (
          <div className="space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <div>
              <p className="text-lg font-medium text-gray-900">Upload en cours...</p>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600 mt-1">{uploadProgress}%</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-6xl">📚</div>
            <div>
              <h3 className="text-xl font-semibold text-gray-900">
                Téléchargez votre document
              </h3>
              <p className="text-gray-600 mt-1">
                Glissez-déposez ou cliquez pour sélectionner
              </p>
            </div>
            
            <div className="flex items-center justify-center space-x-4 text-sm">
              <span className="flex items-center">
                <span className="w-3 h-3 bg-red-500 rounded-full mr-1"></span>
                PDF
              </span>
              <span className="flex items-center">
                <span className="w-3 h-3 bg-blue-500 rounded-full mr-1"></span>
                EPUB
              </span>
              <span className="flex items-center">
                <span className="w-3 h-3 bg-gray-400 rounded-full mr-1"></span>
                Max 50MB
              </span>
            </div>
          </div>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.epub"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm flex items-center">
            ❌ {error}
          </p>
          <button
            onClick={() => setError(null)}
            className="mt-2 text-sm text-red-600 hover:text-red-800"
          >
            Fermer
          </button>
        </div>
      )}
    </div>
  )
}