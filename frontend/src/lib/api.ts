// API Client complet avec fonction d'upload

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

// Types complets
export interface ConversionRequest {
  file_id: string;
  voice_model?: string;
}

export interface ConversionResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface ConversionStatusResponse {
  job_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress: number;
  started_at: string;
  completed_at?: string;
  error?: string;
}

export interface FileUploadResponse {
  file_id: string;
  filename: string;
  message: string;
  file_size: number;
}

export interface PreviewVoiceInfo {
  id: string;
  name: string;
  model_path: string;
  language: string;
  gender: "male" | "female";
  quality: "low" | "medium" | "high";
  description: string;
}

export interface PreviewVoicesListResponse {
  voices: PreviewVoiceInfo[];
  total: number;
  recommendations: {
    fastest: string;
    best_quality: string;
    french_best: string;
  };
}

export interface TTSPreviewRequest {
  text: string;
  voice_model: string;
  length_scale?: number;
  noise_scale?: number;
  noise_w?: number;
  sentence_silence?: number;
}

export interface TTSPreviewResponse {
  audio_url: string;
  preview_id: string;
}

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
    this.name = "ApiError";
  }
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          // N'ajouter Content-Type que si ce n'est pas FormData
          ...(!(options.body instanceof FormData) && {
            "Content-Type": "application/json",
          }),
          ...options.headers,
        },
      });

      if (!response.ok) {
        let errorMessage = `HTTP Error ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          errorMessage = response.statusText || errorMessage;
        }
        throw new ApiError(errorMessage, response.status);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) throw error;
      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new ApiError("Backend non accessible - port 8001", 0);
      }
      throw new ApiError("Erreur inconnue", 0);
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>("/health");
  }

  // File upload
  async uploadFile(file: File): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    // Pour l'instant, on simule l'upload
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          file_id: "file-" + Math.random().toString(36).substr(2, 9),
          filename: file.name,
          message: "File uploaded successfully (simulated)",
          file_size: file.size,
        });
      }, 1500); // Simule un délai d'upload
    });

    // Quand le backend sera prêt, décommenter cette ligne :
    // return this.request<FileUploadResponse>("/api/upload/file", {
    //   method: "POST",
    //   body: formData,
    // })
  }

  // Conversion endpoints
  async startConversion(
    request: ConversionRequest
  ): Promise<ConversionResponse> {
    return this.request<ConversionResponse>("/api/convert/start", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async getConversionStatus(jobId: string): Promise<ConversionStatusResponse> {
    return this.request<ConversionStatusResponse>(
      `/api/convert/status/${jobId}`
    );
  }

  // Mock voice endpoints
  async getPreviewVoices(): Promise<PreviewVoicesListResponse> {
    const mockVoices: PreviewVoiceInfo[] = [
      {
        id: "fr-1",
        name: "Marie",
        model_path: "fr_FR-marie-medium",
        language: "French",
        gender: "female",
        quality: "medium",
        description: "Voix féminine française naturelle",
      },
      {
        id: "fr-2",
        name: "Pierre",
        model_path: "fr_FR-pierre-medium",
        language: "French",
        gender: "male",
        quality: "medium",
        description: "Voix masculine française claire",
      },
      {
        id: "fr-3",
        name: "Sophie",
        model_path: "fr_FR-sophie-high",
        language: "French",
        gender: "female",
        quality: "high",
        description: "Voix féminine française haute qualité",
      },
    ];

    return {
      voices: mockVoices,
      total: mockVoices.length,
      recommendations: {
        fastest: "fr_FR-marie-medium",
        best_quality: "fr_FR-sophie-high",
        french_best: "fr_FR-marie-medium",
      },
    };
  }

  async generateTTSPreview(
    request: TTSPreviewRequest
  ): Promise<TTSPreviewResponse> {
    // Mock preview - simule la génération
    await new Promise((resolve) => setTimeout(resolve, 2000));

    return {
      audio_url: `${this.baseUrl}/mock-audio.mp3`,
      preview_id: "preview-" + Math.random().toString(36).substr(2, 9),
    };
  }

  // Test connection
  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch {
      return false;
    }
  }
}

export const api = new ApiClient();
