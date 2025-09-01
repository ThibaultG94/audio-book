"use client";

import { useState, useRef, DragEvent } from "react";
import { api } from "@/lib/api";
import { FileUploadResponse } from "@/lib/types";

interface FileUploadProps {
  onFileUploaded: (response: FileUploadResponse) => void;
  isLoading: boolean;
}

export default function FileUpload({ onFileUploaded, isLoading }: FileUploadProps) {
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    // Check file type
    const allowedTypes = [
      'application/pdf', 
      'application/epub+zip', 
      'text/plain',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/rtf'
    ];
    const allowedExtensions = ['.pdf', '.epub', '.txt', '.docx', '.rtf'];
    
    const hasValidType = allowedTypes.includes(file.type);
    const hasValidExtension = allowedExtensions.some(ext => 
      file.name.toLowerCase().endsWith(ext)
    );
    
    if (!hasValidType && !hasValidExtension) {
      return "Format de fichier non supporté. Formats acceptés : PDF, EPUB, TXT, DOCX, RTF.";
    }

    // Check file size (50MB max)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      return "Le fichier est trop volumineux. Taille maximum : 50MB.";
    }

    return null;
  };

  const handleFileUpload = async (file: File) => {
    if (isLoading) return;

    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setError(null);
    setUploadProgress(0);

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response = await api.uploadFile(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      setTimeout(() => {
        onFileUploaded(response);
        setUploadProgress(0);
      }, 500);
      
    } catch (err) {
      setUploadProgress(0);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Erreur lors du téléchargement du fichier");
      }
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (!isLoading && !isDragging) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    // Only set dragging to false if leaving the dropzone entirely
    if (!e.currentTarget.contains(e.relatedTarget as Node)) {
      setIsDragging(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    if (isLoading) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const openFileDialog = () => {
    if (!isLoading && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={openFileDialog}
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
          transition-all duration-300 ease-in-out
          ${isDragging 
            ? "border-blue-500 bg-blue-50 scale-105" 
            : "border-gray-300 hover:border-gray-400 hover:bg-gray-50"
          }
          ${isLoading ? "opacity-50 cursor-not-allowed pointer-events-none" : ""}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.epub,.txt,.docx,.rtf"
          onChange={handleFileInputChange}
          className="hidden"
          disabled={isLoading}
        />
        
        <div className="flex flex-col items-center space-y-6">
          {/* Icon */}
          <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-colors ${
            isDragging ? 'bg-blue-100' : 'bg-gray-100'
          }`}>
            {isLoading || uploadProgress > 0 ? (
              <div className="relative w-12 h-12">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-gray-200"></div>
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent absolute top-0 left-0"></div>
                {uploadProgress > 0 && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xs font-bold text-blue-600">{uploadProgress}%</span>
                  </div>
                )}
              </div>
            ) : (
              <svg 
                className={`w-8 h-8 ${isDragging ? 'text-blue-500' : 'text-gray-400'}`} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" 
                />
              </svg>
            )}
          </div>
          
          {/* Text */}
          <div className="space-y-2">
            <h3 className={`text-lg font-semibold ${
              isDragging ? 'text-blue-700' : 'text-gray-900'
            }`}>
              {isLoading ? (
                "Téléchargement en cours..."
              ) : isDragging ? (
                "Déposez votre fichier ici"
              ) : (
                "Téléchargez votre document"
              )}
            </h3>
            
            {!isLoading && (
              <>
                <p className="text-gray-600">
                  Glissez-déposez ou cliquez pour sélectionner
                </p>
                <div className="flex items-center justify-center space-x-3 text-sm text-gray-500">
                  <div className="flex items-center space-x-1">
                    <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                    <span>PDF</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                    <span>EPUB</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    <span>TXT</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                    <span>DOCX</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                    <span>RTF</span>
                  </div>
                  <span>•</span>
                  <span>Max 50MB</span>
                </div>
              </>
            )}
          </div>

          {/* Progress bar */}
          {uploadProgress > 0 && (
            <div className="w-full max-w-xs">
              <div className="bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start space-x-3">
            <div className="text-red-500 mt-0.5">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 className="text-sm font-medium text-red-800 mb-1">Erreur de téléchargement</h4>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
          <button
            onClick={() => setError(null)}
            className="mt-3 text-sm text-red-600 hover:text-red-800 font-medium"
          >
            Fermer
          </button>
        </div>
      )}

      {/* Help text */}
      <div className="mt-4 text-center">
        <details className="text-sm text-gray-500">
          <summary className="cursor-pointer hover:text-gray-700 font-medium">
            Formats supportés et conseils
          </summary>
          <div className="mt-2 text-left bg-gray-50 rounded-lg p-3 space-y-2">
            <div>
              <strong className="text-gray-700">📖 PDF :</strong> Assurez-vous que le texte est sélectionnable (pas une image scannée).
            </div>
            <div>
              <strong className="text-gray-700">📚 EPUB :</strong> Format idéal pour les livres électroniques.
            </div>
            <div>
              <strong className="text-gray-700">📝 TXT :</strong> Fichiers texte simple, encodage automatique détecté.
            </div>
            <div>
              <strong className="text-gray-700">📄 DOCX :</strong> Documents Microsoft Word modernes.
            </div>
            <div>
              <strong className="text-gray-700">📋 RTF :</strong> Rich Text Format, compatible multi-plateforme.
            </div>
            <div className="text-xs text-gray-400 pt-2 border-t">
              💡 Astuce : Les documents avec un texte bien structuré donnent de meilleurs résultats audio.
            </div>
          </div>
        </details>
      </div>
    </div>
  );
}