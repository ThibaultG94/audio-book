"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FileUpload } from "@/components/FileUpload";
import VoicePreview from "@/components/VoicePreview";
import { api } from "@/lib/api";
import { FileUploadResponse, ConversionRequest } from "@/lib/types";

interface VoiceSettings { 
  length_scale: number;
  noise_scale: number;
  noise_w: number;
  sentence_silence: number;
}

export default function HomePage() {
  const [isUploading, setIsUploading] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const [selectedVoiceSettings, setSelectedVoiceSettings] = useState<{
    voice: string;
    settings: VoiceSettings;
  } | null>(null);
  
  const router = useRouter();

  const handleFileUploaded = async (uploadResponse: FileUploadResponse) => {
    setIsConverting(true);

    try {
      const conversionRequest: ConversionRequest = {
        file_id: uploadResponse.file_id,
        // Use voice settings from preview if available
        ...(selectedVoiceSettings && {
          voice_model: selectedVoiceSettings.voice,
          length_scale: selectedVoiceSettings.settings.length_scale,
          noise_scale: selectedVoiceSettings.settings.noise_scale,
          noise_w: selectedVoiceSettings.settings.noise_w,
          sentence_silence: selectedVoiceSettings.settings.sentence_silence,
        })
      };

      const conversionResponse = await api.startConversion(conversionRequest);

      // Redirect to conversion status page
      router.push(`/convert/${conversionResponse.job_id}`);
    } catch (error) {
      console.error("Failed to start conversion:", error);
      setIsConverting(false);
    }
  };

  const handleVoiceTest = (voice: string, settings: VoiceSettings) => {
    setSelectedVoiceSettings({ voice, settings });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <div className="container mx-auto px-4 py-16">
        
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Audio Book Converter
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Convertissez vos PDF et EPUB en livres audio de haute qualité 
            grâce à l'intelligence artificielle.
          </p>
        </div>

        <div className="max-w-4xl mx-auto grid lg:grid-cols-2 gap-8">
          
          {/* Voice Preview Section */}
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-3">
                🎤 Testez la voix
              </h2>
              <p className="text-gray-600 mb-4">
                Écoutez un aperçu de la voix qui lira votre livre audio 
                et ajustez les paramètres selon vos préférences.
              </p>
            </div>
            
            <VoicePreview 
              onVoiceTest={handleVoiceTest}
              className="h-fit"
            />

            {selectedVoiceSettings && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center mb-2">
                  <div className="w-3 h-3 bg-green-400 rounded-full mr-2"></div>
                  <span className="text-sm font-medium text-green-800">
                    Paramètres de voix configurés
                  </span>
                </div>
                <div className="text-sm text-green-700">
                  <p>Vitesse: {selectedVoiceSettings.settings.length_scale}x</p>
                  <p>Expressivité: {selectedVoiceSettings.settings.noise_scale}</p>
                  <p>Variation phonétique: {selectedVoiceSettings.settings.noise_w}</p>
                  <p>Pause entre phrases: {selectedVoiceSettings.settings.sentence_silence}s</p>
                  <p className="text-xs mt-1">
                    Ces paramètres seront utilisés pour votre conversion
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* File Upload Section */}
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-3">
                📚 Téléchargez votre document
              </h2>
              <p className="text-gray-600 mb-4">
                Glissez-déposez ou sélectionnez votre fichier PDF ou EPUB 
                pour commencer la conversion.
              </p>
            </div>
            
            <FileUpload 
              onFileUploaded={handleFileUploaded} 
              isLoading={isUploading || isConverting}
            />

            {isConverting && (
              <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-center mb-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500 mr-2"></div>
                  <span className="text-blue-800 font-medium">Démarrage de la conversion...</span>
                </div>
                <p className="text-sm text-blue-600">
                  {selectedVoiceSettings 
                    ? "Utilisation de vos paramètres de voix personnalisés" 
                    : "Utilisation des paramètres par défaut"
                  }
                </p>
              </div>
            )}

            {/* File Format Support */}
            <div className="text-center space-y-2">
              <p className="text-sm text-gray-500">Formats supportés :</p>
              <div className="flex justify-center space-x-4">
                <span className="px-3 py-1 bg-red-100 text-red-800 text-xs rounded-full font-medium">
                  PDF
                </span>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium">
                  EPUB
                </span>
              </div>
              <p className="text-xs text-gray-400">
                Taille maximum : 50 MB
              </p>
            </div>
          </div>
        </div>

        {/* How it works */}
        <div className="mt-20 max-w-5xl mx-auto">
          <h2 className="text-3xl font-semibold text-gray-900 mb-8 text-center">
            Comment ça marche
          </h2>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">1</span>
              </div>
              <h3 className="font-semibold mb-2 text-lg">Testez la voix</h3>
              <p className="text-gray-600 text-sm">
                Écoutez un aperçu et ajustez les paramètres selon vos préférences
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">2</span>
              </div>
              <h3 className="font-semibold mb-2 text-lg">Téléchargez le document</h3>
              <p className="text-gray-600 text-sm">
                Uploadez votre fichier PDF ou EPUB
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">3</span>
              </div>
              <h3 className="font-semibold mb-2 text-lg">IA en traitement</h3>
              <p className="text-gray-600 text-sm">
                Notre IA convertit le texte en parole naturelle
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">4</span>
              </div>
              <h3 className="font-semibold mb-2 text-lg">Téléchargez l'audio</h3>
              <p className="text-gray-600 text-sm">
                Récupérez votre livre audio de haute qualité
              </p>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="mt-20 bg-white rounded-2xl shadow-sm border p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
            Pourquoi choisir notre convertisseur ?
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl mb-3">🧠</div>
              <h3 className="font-semibold mb-2">Intelligence artificielle avancée</h3>
              <p className="text-gray-600 text-sm">
                Voix naturelle grâce aux réseaux de neurones Piper TTS
              </p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-3">🎛️</div>
              <h3 className="font-semibold mb-2">Paramètres personnalisables</h3>
              <p className="text-gray-600 text-sm">
                Ajustez la vitesse et les variations de voix selon vos goûts
              </p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-3">🔒</div>
              <h3 className="font-semibold mb-2">Traitement sécurisé</h3>
              <p className="text-gray-600 text-sm">
                Vos documents sont traités localement et supprimés après conversion
              </p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-3">⚡</div>
              <h3 className="font-semibold mb-2">Rapidité</h3>
              <p className="text-gray-600 text-sm">
                Conversion optimisée par blocs pour un traitement efficace
              </p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-3">🎧</div>
              <h3 className="font-semibold mb-2">Qualité audio</h3>
              <p className="text-gray-600 text-sm">
                Format WAV haute définition pour une écoute optimale
              </p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-3">🌍</div>
              <h3 className="font-semibold mb-2">Gratuit et open source</h3>
              <p className="text-gray-600 text-sm">
                Traitement local sans envoi de données vers des serveurs tiers
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-20 text-center text-gray-500">
          <div className="max-w-4xl mx-auto border-t pt-8">
            <p className="text-sm">
              Propulsé par{" "}
              <a
                href="https://github.com/rhasspy/piper"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline"
              >
                Piper TTS
              </a>{" "}
              • Intelligence artificielle pour une voix naturelle
            </p>
            <p className="text-xs mt-2 text-gray-400">
              Convertissez vos documents en toute sécurité • Traitement local • Open Source
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}