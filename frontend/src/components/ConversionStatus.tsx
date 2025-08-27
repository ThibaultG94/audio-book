"use client";

import { useEffect, useState } from "react";
import { ConversionStatus as ConversionStatusEnum, ConversionStatusResponse } from "@/lib/types";
import { api } from "@/lib/api";

interface ConversionStatusProps {
  jobId: string;
  onComplete?: (audioUrl: string) => void;
}

export default function ConversionStatus({ jobId, onComplete }: ConversionStatusProps) {
  const [status, setStatus] = useState<ConversionStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(true);

  useEffect(() => {
    let pollInterval: NodeJS.Timeout;
    let mounted = true;

    const pollStatus = async () => {
      try {
        const response = await api.getConversionStatus(jobId);
        
        if (!mounted) return;
        
        setStatus(response);
        setError(null);

        if (response.status === ConversionStatusEnum.COMPLETED) {
          setIsPolling(false);
          if (response.audio_file_url) {
            onComplete?.(response.audio_file_url);
          }
        } else if (response.status === ConversionStatusEnum.FAILED) {
          setIsPolling(false);
        }
      } catch (err) {
        if (!mounted) return;
        
        setError(err instanceof Error ? err.message : "Failed to get status");
        setIsPolling(false);
      }
    };

    // Initial poll
    pollStatus();
    
    // Set up polling interval
    if (isPolling) {
      pollInterval = setInterval(pollStatus, 2000);
    }

    return () => {
      mounted = false;
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [jobId, onComplete, isPolling]);

  const getStatusStep = (currentStatus: ConversionStatusEnum): number => {
    switch (currentStatus) {
      case ConversionStatusEnum.PENDING: return 1;
      case ConversionStatusEnum.PROCESSING: return 2;
      case ConversionStatusEnum.COMPLETED: return 3;
      case ConversionStatusEnum.FAILED: return 0;
      default: return 0;
    }
  };

  const steps = [
    { id: 1, name: "File en attente", description: "Votre fichier est dans la file d'attente" },
    { id: 2, name: "Conversion en cours", description: "Transformation du texte en audio" },
    { id: 3, name: "Terminé", description: "Votre livre audio est prêt !" }
  ];

  if (error) {
    return (
      <div className="space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-2">Erreur de conversion</h3>
              <p className="text-red-700 mb-4">{error}</p>
              <button
                onClick={() => {
                  setError(null);
                  setIsPolling(true);
                }}
                className="inline-flex items-center px-4 py-2 bg-red-100 text-red-800 rounded-lg hover:bg-red-200 transition-colors"
              >
                Réessayer
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center p-8">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <span className="text-lg text-gray-600">Chargement du statut...</span>
          </div>
        </div>
      </div>
    );
  }

  const currentStep = getStatusStep(status.status);
  const isComplete = status.status === ConversionStatusEnum.COMPLETED;
  const isFailed = status.status === ConversionStatusEnum.FAILED;

  return (
    <div className="space-y-8">
      
      {/* Progress Steps */}
      <div className="relative">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const isCurrentStep = step.id === currentStep;
            const isCompletedStep = step.id < currentStep || (step.id === currentStep && isComplete);
            const isFailedStep = isFailed && step.id === currentStep;
            
            return (
              <div key={step.id} className="flex flex-col items-center relative z-10">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-300 ${
                  isFailedStep
                    ? 'bg-red-500 border-red-500 text-white'
                    : isCompletedStep
                    ? 'bg-green-500 border-green-500 text-white'
                    : isCurrentStep
                    ? 'bg-blue-500 border-blue-500 text-white'
                    : 'bg-gray-200 border-gray-300 text-gray-500'
                }`}>
                  {isFailedStep ? (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  ) : isCompletedStep ? (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <span className="font-semibold">{step.id}</span>
                  )}
                </div>
                <div className="mt-3 text-center">
                  <div className={`font-medium ${
                    isCurrentStep || isCompletedStep ? 'text-gray-900' : 'text-gray-500'
                  }`}>
                    {step.name}
                  </div>
                  <div className={`text-sm mt-1 ${
                    isCurrentStep || isCompletedStep ? 'text-gray-600' : 'text-gray-400'
                  }`}>
                    {step.description}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Progress Line */}
        <div className="absolute top-6 left-6 right-6 h-0.5 bg-gray-200 -z-0">
          <div 
            className="h-full bg-blue-500 transition-all duration-500 ease-in-out"
            style={{ 
              width: isFailed ? '0%' : `${Math.max(0, ((currentStep - 1) / (steps.length - 1)) * 100)}%` 
            }}
          ></div>
        </div>
      </div>

      {/* Current Status Details */}
      <div className="bg-gray-50 rounded-xl p-6">
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0 mt-1">
            {status.status === ConversionStatusEnum.PROCESSING ? (
              <div className="animate-spin rounded-full h-6 w-6 border-2 border-blue-500 border-t-transparent"></div>
            ) : status.status === ConversionStatusEnum.COMPLETED ? (
              <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : status.status === ConversionStatusEnum.FAILED ? (
              <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : (
              <svg className="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
          </div>
          
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-2">
              {status.status === ConversionStatusEnum.PENDING && "File en attente de traitement"}
              {status.status === ConversionStatusEnum.PROCESSING && `Conversion en cours... ${status.progress_percent || 0}%`}
              {status.status === ConversionStatusEnum.COMPLETED && "Conversion terminée avec succès !"}
              {status.status === ConversionStatusEnum.FAILED && "Échec de la conversion"}
            </h3>
            
            <p className="text-gray-600 mb-4">
              {status.status === ConversionStatusEnum.PENDING && "Votre document est dans la file d'attente et sera traité sous peu."}
              {status.status === ConversionStatusEnum.PROCESSING && "Votre document est en cours de transformation en livre audio. Cette opération peut prendre quelques minutes selon la longueur du texte."}
              {status.status === ConversionStatusEnum.COMPLETED && "Votre livre audio est prêt ! Vous pouvez maintenant l'écouter ou le télécharger."}
              {status.status === ConversionStatusEnum.FAILED && (status.error_message || "Une erreur est survenue pendant la conversion. Veuillez réessayer.")}
            </p>

            {/* Progress Bar */}
            {status.status === ConversionStatusEnum.PROCESSING && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Progression</span>
                  <span>{status.progress_percent || 0}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-blue-500 h-3 rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${status.progress_percent || 0}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Additional Info */}
        {status.created_at && (
          <div className="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-500">
            <div className="flex justify-between">
              <span>Démarré le : {new Date(status.created_at).toLocaleString('fr-FR')}</span>
              {status.completed_at && (
                <span>Terminé le : {new Date(status.completed_at).toLocaleString('fr-FR')}</span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      {status.status === ConversionStatusEnum.COMPLETED && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-green-900 mb-1">🎉 Votre livre audio est prêt !</h4>
              <p className="text-green-700 text-sm">Cliquez sur les boutons ci-dessous pour écouter ou télécharger votre fichier.</p>
            </div>
          </div>
          
          <div className="flex space-x-3 mt-4">
            <audio
              controls
              className="flex-1 max-w-md"
              preload="metadata"
            >
              <source src={api.getAudioUrl(jobId)} type="audio/wav" />
              Votre navigateur ne supporte pas l'élément audio.
            </audio>
            
            <a
              href={api.downloadAudio(jobId)}
              download
              className="inline-flex items-center px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-4-4m4 4l4-4m3 5a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Télécharger
            </a>
          </div>
        </div>
      )}
    </div>
  );
}