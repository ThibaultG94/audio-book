/**
 * Conversion progress and status display
 */

"use client";

import { useEffect, useState } from "react";
import { CheckCircle, XCircle, Loader2, Download } from "lucide-react";
import { ConversionStatus, ConversionStatusResponse } from "@/lib/types";
import { api } from "@/lib/api";

interface ConversionStatusProps {
  jobId: string;
  onComplete?: (audioUrl: string) => void;
}

export function ConversionStatusDisplay({ jobId, onComplete }: ConversionStatusProps) {
  const [status, setStatus] = useState<ConversionStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await api.getConversionStatus(jobId);
        setStatus(response);

        if (response.status === ConversionStatus.COMPLETED && response.audio_file_url) {
          onComplete?.(response.audio_file_url);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to get status");
      }
    };

    pollStatus();
    
    // Poll every 2 seconds while processing
    const interval = setInterval(() => {
      if (status?.status === ConversionStatus.PROCESSING || status?.status === ConversionStatus.PENDING) {
        pollStatus();
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId, status?.status, onComplete]);

  if (error) {
    return (
      <div className="flex items-center space-x-3 p-4 bg-red-50 border border-red-200 rounded-lg">
        <XCircle className="h-6 w-6 text-red-500" />
        <div>
          <p className="font-medium text-red-800">Error</p>
          <p className="text-sm text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="flex items-center space-x-3 p-4">
        <Loader2 className="h-6 w-6 animate-spin" />
        <p>Loading status...</p>
      </div>
    );
  }

  const getStatusIcon = () => {
    switch (status.status) {
      case ConversionStatus.PENDING:
      case ConversionStatus.PROCESSING:
        return <Loader2 className="h-6 w-6 animate-spin text-blue-500" />;
      case ConversionStatus.COMPLETED:
        return <CheckCircle className="h-6 w-6 text-green-500" />;
      case ConversionStatus.FAILED:
        return <XCircle className="h-6 w-6 text-red-500" />;
    }
  };

  const getStatusMessage = () => {
    switch (status.status) {
      case ConversionStatus.PENDING:
        return "Conversion queued...";
      case ConversionStatus.PROCESSING:
        return `Converting to audio... ${status.progress_percent || 0}%`;
      case ConversionStatus.COMPLETED:
        return "Conversion completed!";
      case ConversionStatus.FAILED:
        return status.error_message || "Conversion failed";
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-3 p-4 bg-gray-50 border border-gray-200 rounded-lg">
        {getStatusIcon()}
        <div className="flex-1">
          <p className="font-medium">{getStatusMessage()}</p>
          {status.progress_percent && (
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${status.progress_percent}%` }}
              />
            </div>
          )}
        </div>
      </div>

      {status.status === ConversionStatus.COMPLETED && status.audio_file_url && (
        <div className="flex space-x-2">
          <a
            href={api.getAudioUrl(jobId)}
            download
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <Download className="h-4 w-4 mr-2" />
            Download Audio
          </a>
        </div>
      )}
    </div>
  );
}