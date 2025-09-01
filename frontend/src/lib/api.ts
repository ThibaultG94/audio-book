import {
  ConversionRequest,
  ConversionResponse,
  ConversionStatusResponse,
  FileUploadResponse,
  TTSPreviewRequest,
  TTSPreviewResponse,
  VoicesListResponse,
  PreviewVoicesListResponse,
  DefaultParametersResponse,
  Voice,
  VoiceMetadata,
  VoiceTechnicalInfo,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export class ApiError extends Error {
  constructor(message: string, public status: number, public response?: any) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * HTTP client with error handling and retries
 */
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/$/, ""); // Remove trailing slash
  }

  /**
   * Generic fetch wrapper with error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    // Build headers properly
    const headers: HeadersInit = {};

    // Copy existing headers if they're an object
    if (
      options.headers &&
      typeof options.headers === "object" &&
      !Array.isArray(options.headers)
    ) {
      Object.assign(headers, options.headers);
    }

    // Only add JSON Content-Type if we're not sending FormData
    if (!(options.body instanceof FormData) && options.body) {
      headers["Content-Type"] = "application/json";
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Check if response is ok
      if (!response.ok) {
        let errorMessage = `HTTP Error ${response.status}`;

        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          // If JSON parsing fails, use status text
          errorMessage = response.statusText || errorMessage;
        }

        throw new ApiError(errorMessage, response.status);
      }

      // Handle different response types
      const contentType = response.headers.get("content-type");

      if (contentType?.includes("application/json")) {
        return await response.json();
      } else {
        // For non-JSON responses, return response object
        return response as unknown as T;
      }
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }

      // Network or other errors
      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new ApiError(
          "Backend non accessible - vérifiez que FastAPI tourne sur le port 8001",
          0
        );
      }

      throw new ApiError(
        error instanceof Error ? error.message : "Erreur inconnue",
        0
      );
    }
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" });
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }

  // Health check
  async healthCheck(): Promise<{
    status: string;
    app: string;
    version: string;
  }> {
    return this.get<{ status: string; app: string; version: string }>(
      "/health"
    );
  }

  // Voice-related methods
  async getVoices(): Promise<VoicesListResponse> {
    return this.get<VoicesListResponse>("/api/voice/list");
  }

  async getPreviewVoices(): Promise<PreviewVoicesListResponse> {
    return this.get<PreviewVoicesListResponse>("/api/preview/voices");
  }

  async getVoiceDetails(voiceId: string): Promise<Voice> {
    return this.get<Voice>(`/api/voice/${voiceId}`);
  }

  async validateVoice(voiceId: string): Promise<{
    voice_id: string;
    valid: boolean;
    model_file: string;
    config_file: string;
    config_valid: boolean;
    issues: string[];
  }> {
    return this.get(`/api/voice/validate/${voiceId}`);
  }

  // TTS Preview methods
  async generateTTSPreview(
    request: TTSPreviewRequest
  ): Promise<TTSPreviewResponse> {
    return this.post<TTSPreviewResponse>("/api/preview/tts", request);
  }

  async getDefaultParameters(): Promise<DefaultParametersResponse> {
    return this.get<DefaultParametersResponse>(
      "/api/preview/parameters/defaults"
    );
  }

  async deletePreview(previewId: string): Promise<{ message: string }> {
    return this.delete<{ message: string }>(`/api/preview/audio/${previewId}`);
  }

  async cleanupOldPreviews(maxAgeHours: number = 24): Promise<{
    deleted: number;
    size_freed_mb: number;
    message: string;
  }> {
    return this.post(`/api/preview/cleanup?max_age_hours=${maxAgeHours}`);
  }

  // File upload methods
  async uploadFile(file: File): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${this.baseUrl}/api/upload/file`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let errorMessage = "Upload failed";
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        errorMessage = response.statusText || errorMessage;
      }
      throw new ApiError(errorMessage, response.status);
    }

    const data = await response.json();

    // Ensure the response conforms to FileUploadResponse
    return {
      file_id: data.file_id,
      filename: data.filename,
      file_size: data.file_size,
      content_type: data.content_type,
      upload_path: data.upload_path,
    } as FileUploadResponse;
  }

  // Conversion methods
  async startConversion(request: {
    file_id: string;
    voice_model: string;
    length_scale: number;
    noise_scale: number;
    noise_w: number;
    sentence_silence: number;
    output_format: string;
  }): Promise<ConversionResponse> {
    return this.post<ConversionResponse>("/api/convert/start", request);
  }

  async getConversionStatus(jobId: string): Promise<ConversionStatusResponse> {
    return this.get<ConversionStatusResponse>(`/api/convert/status/${jobId}`);
  }

  // Audio serving (these return direct URLs)
  getAudioUrl(jobId: string): string {
    return `${this.baseUrl}/api/audio/${jobId}`;
  }

  getPreviewAudioUrl(previewId: string): string {
    return `${this.baseUrl}/api/preview/audio/${previewId}`;
  }

  downloadAudio(jobId: string): string {
    return `${this.baseUrl}/api/audio/${jobId}/download`;
  }
}

// Export singleton instance
export const api = new ApiClient();

// Re-export types for convenience
export type {
  Voice,
  VoiceMetadata,
  VoiceTechnicalInfo,
  VoicesListResponse,
  PreviewVoicesListResponse,
  TTSPreviewRequest,
  TTSPreviewResponse,
  FileUploadResponse,
  ConversionRequest,
  ConversionResponse,
  ConversionStatusResponse,
  DefaultParametersResponse,
};
