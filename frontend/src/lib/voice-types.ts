/**
 * Enhanced TypeScript interfaces for voice management with proper nullability
 */

export interface VoiceLanguage {
  code: string;
  name_english: string;
  name_native: string;
}

export interface VoiceSpeaker {
  gender: "female" | "male" | "multi" | "neutral";
  age_range: string;
  voice_style: string;
  accent: string;
  available_speakers?: Record<
    string,
    {
      gender: string;
      style: string;
    }
  >;
}

export interface VoiceTechnical {
  quality: "low" | "medium" | "high";
  sample_rate: number;
  dataset: string;
  file_size_mb: number;
  processing_speed: "fast" | "medium" | "slow";
}

export interface VoiceMetadata {
  // Basic info
  name: string;
  display_name: string;
  language: VoiceLanguage;

  // Voice characteristics
  speaker: VoiceSpeaker;
  technical: VoiceTechnical;

  // Usage and recommendations - made optional and nullable
  recommended_usage?: string[] | null;
  description: string;
  best_for: string;

  // UI representation
  avatar: string;
  color: string;
  model_path: string;
}

export interface VoiceListResponse {
  voices: VoiceMetadata[];
  default_voice: string;
  count: number;
  recommendations?: Record<string, string>;
}

export interface VoiceSettings {
  length_scale: number;
  noise_scale: number;
  noise_w: number;
  sentence_silence: number;
}

export interface PreviewRequest {
  text: string;
  voice_model?: string;
  length_scale?: number;
  noise_scale?: number;
  noise_w?: number;
  sentence_silence?: number;
}

export interface PreviewResponse {
  preview_id: string;
  text: string;
  audio_url: string;
  duration_estimate: number;
  voice_model: string;
  parameters: VoiceSettings;
  voice_info?: VoiceMetadata;
}

// Helper functions for safe data access
export const safeVoiceAccess = {
  /**
   * Safely get recommended usage array, never returns null/undefined
   */
  getRecommendedUsage: (voice: VoiceMetadata): string[] => {
    if (!voice.recommended_usage) return [];
    if (!Array.isArray(voice.recommended_usage)) return [];
    return voice.recommended_usage;
  },

  /**
   * Check if voice supports specific usage
   */
  supportsUsage: (voice: VoiceMetadata, usage: string): boolean => {
    const usageArray = safeVoiceAccess.getRecommendedUsage(voice);
    return usageArray.includes(usage);
  },

  /**
   * Get display name with fallback
   */
  getDisplayName: (voice: VoiceMetadata): string => {
    return voice.display_name || voice.name || "Voice inconnue";
  },

  /**
   * Get avatar with fallback
   */
  getAvatar: (voice: VoiceMetadata): string => {
    return voice.avatar || "🎭";
  },

  /**
   * Get color with fallback
   */
  getColor: (voice: VoiceMetadata): string => {
    return voice.color || "#6B7280";
  },

  /**
   * Safe file size access
   */
  getFileSize: (voice: VoiceMetadata): number => {
    return voice.technical?.file_size_mb || 0;
  },
};

// Type guards for runtime safety
export const voiceTypeGuards = {
  /**
   * Check if object is valid VoiceMetadata
   */
  isVoiceMetadata: (obj: any): obj is VoiceMetadata => {
    return (
      obj &&
      typeof obj === "object" &&
      typeof obj.name === "string" &&
      typeof obj.model_path === "string" &&
      obj.speaker &&
      obj.technical
    );
  },

  /**
   * Check if voice has valid recommended usage
   */
  hasValidRecommendedUsage: (voice: any): boolean => {
    return (
      voice?.recommended_usage &&
      Array.isArray(voice.recommended_usage) &&
      voice.recommended_usage.length > 0
    );
  },
};
