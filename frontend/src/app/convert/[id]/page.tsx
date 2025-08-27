"use client";

import { useParams, useRouter } from "next/navigation";
import ConversionStatus from "@/components/ConversionStatus";

export default function ConvertPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.id as string;

  const handleComplete = (audioUrl: string) => {
    // Could redirect to player page or show success message
    console.log("Conversion completed:", audioUrl);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          
          {/* Header */}
          <div className="flex items-center mb-8">
            <button
              onClick={() => router.push("/")}
              className="flex items-center text-gray-600 hover:text-gray-900 bg-white rounded-lg px-4 py-2 border border-gray-200 hover:border-gray-300 transition-colors"
            >
              <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Retour à l'accueil
            </button>
          </div>

          {/* Main content */}
          <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
            
            {/* Header section */}
            <div className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white p-8">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 016 0v6a3 3 0 01-3 3z" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-3xl font-bold mb-2">
                    Conversion en cours
                  </h1>
                  <p className="text-blue-100 text-lg">
                    Votre document est en cours de transformation en livre audio
                  </p>
                </div>
              </div>
            </div>

            {/* Status section */}
            <div className="p-8">
              <ConversionStatus
                jobId={jobId}
                onComplete={handleComplete}
              />
            </div>
          </div>

          {/* Help section */}
          <div className="mt-8 bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <span className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mr-3 text-blue-600">
                💡
              </span>
              Pendant que vous attendez...
            </h3>
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div className="space-y-2">
                <h4 className="font-medium text-gray-800">⏰ Temps de traitement</h4>
                <p className="text-gray-600">
                  Le temps de conversion dépend de la longueur du document et de la qualité de voix sélectionnée.
                </p>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium text-gray-800">🎯 Traitement par blocs</h4>
                <p className="text-gray-600">
                  Votre document est découpé en segments pour une synthèse vocale optimale et naturelle.
                </p>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium text-gray-800">🔊 Qualité audio</h4>
                <p className="text-gray-600">
                  Le fichier final sera au format WAV haute définition, parfait pour l'écoute.
                </p>
              </div>
            </div>
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>ID de conversion :</strong> <code className="bg-white px-2 py-1 rounded text-xs">{jobId}</code>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}