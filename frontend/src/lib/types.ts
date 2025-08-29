// Voice-related types (matching backend models)
export interface VoiceTechnicalInfo {
  sample_rate: number;
  num_speakers: number;
  model_size: string;
  architecture?: string;
}

export interface VoiceMetadata {
  name: string;
  language_code: string;
  gender?: string;
  age?: string;
  dataset?: string;
  description?: string;
  recommended_usage: string[];
}

export interface Voice {
  id: string;
  model_path: string;
  config_path: string;
  metadata: VoiceMetadata;
  technical_info: VoiceTechnicalInfo;
  quality?: VoiceQuality;
  available: boolean;
}

export interface VoiceQuality {
  naturalness: number;
  clarity: number;
  expressiveness: number;
}

export interface VoicesListResponse {
  voices: Voice[];
  count: number;
  default_voice?: string;
}

// Preview-specific voice info (from preview endpoint)
export interface PreviewVoiceInfo {
  model_path: string;
  name: string;
  full_path: string;
  language?: {
    code: string;
    family: string;
    region: string;
    name_native: string;
    name_english: string;
    country_english: string;
  };
  dataset?: string;
  quality?: string;
  sample_rate?: number;
  file_size_mb?: number;
  recommended_usage: string[];
}

export interface PreviewVoicesListResponse {
  voices: PreviewVoiceInfo[];
  default_voice: string;
  count: number;
  recommendations: {
    fastest: string;
    highest_quality: string;
    most_natural: string;
    french_best: string;
  };
}

// TTS Preview types
export interface TTSPreviewRequest {
  text: string;
  voice_model?: string;
  length_scale?: number;
  noise_scale?: number;
  noise_w?: number;
  sentence_silence?: number;
}

export interface TTSPreviewResponse {
  preview_id: string;
  text: string;
  audio_url: string;
  duration_estimate: number;
  voice_model: string;
  parameters: {
    length_scale: number;
    noise_scale: number;
    noise_w: number;
    sentence_silence: number;
  };
  voice_info?: PreviewVoiceInfo;
}

// File upload types
export interface FileUploadResponse {
  file_id: string;
  filename: string;
  file_size: number;
  content_type: string;
  upload_path: string;
}

// Conversion types
export interface ConversionRequest {
  file_id: string;
  voice_model?: string;
  length_scale?: number;
  noise_scale?: number;
  noise_w?: number;
  sentence_silence?: number;
}

export interface ConversionResponse {
  job_id: string;
  status: ConversionStatus;
  created_at: string;
}

export enum ConversionStatus {
  PENDING = "pending",
  PROCESSING = "processing", 
  COMPLETED = "completed",
  FAILED = "failed"
}

export interface ConversionStatusResponse {
  job_id: string;
  status: ConversionStatus;
  progress_percent: number;
  created_at: string;
  completed_at?: string;
  audio_file_url?: string;
  error_message?: string;
}

// Default TTS parameters
export interface TTSParameters {
  length_scale: {
    default: number;
    range: [number, number];
    step: number;
    description: string;
    explanation: string;
  };
  noise_scale: {
    default: number;
    range: [number, number];
    step: number;
    description: string;
    explanation: string;
  };
  noise_w: {
    default: number;
    range: [number, number];
    step: number;
    description: string;
    explanation: string;
  };
  sentence_silence: {
    default: number;
    range: [number, number];
    step: number;
    description: string;
    explanation: string;
  };
}

export interface TTSPresets {
  audiobook_natural: {
    length_scale: number;
    noise_scale: number;
    noise_w: number;
    sentence_silence: number;
    description: string;
  };
  news_fast: {
    length_scale: number;
    noise_scale: number;
    noise_w: number;
    sentence_silence: number;
    description: string;
  };
  storytelling: {
    length_scale: number;
    noise_scale: number;
    noise_w: number;
    sentence_silence: number;
    description: string;
  };
}

export interface DefaultParametersResponse {
  parameters: TTSParameters;
  presets: TTSPresets;
}