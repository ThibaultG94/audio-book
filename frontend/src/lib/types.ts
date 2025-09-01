// Voice-related types
export interface VoiceMetadata {
  name: string;
  language_code: string;
  gender?: string;
  age?: string;
  recommended_usage?: string[];
}

export interface VoiceTechnicalInfo {
  sample_rate: number;
  num_speakers: number;
  model_size: string;
  quality?: string;
}

export interface Voice {
  id: string;
  model_path: string;
  config_path: string;
  metadata: VoiceMetadata;
  technical_info: VoiceTechnicalInfo;
  available: boolean;
}

export interface PreviewVoiceInfo {
  model_path: string;
  name: string;
  dataset?: string;
  quality?: string;
  file_size_mb?: number;
  sample_rate?: number;
  language?: string;
  gender?: string;
  recommended_usage?: string[];
}

export interface VoicesListResponse {
  voices: Voice[];
  count: number;
  default_voice: string;
}

export interface PreviewVoicesListResponse {
  voices: PreviewVoiceInfo[];
  count: number;
  default_voice: string;
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
  voice_model: string;
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
}

// File upload types - CORRECTED
export interface FileUploadResponse {
  file_id: string;
  filename: string;
  file_size?: number; // Made optional
  content_type?: string; // Made optional
  upload_path?: string; // Made optional
}

// Conversion types
export interface ConversionRequest {
  file_id: string;
  voice_model: string;
  length_scale: number;
  noise_scale: number;
  noise_w: number;
  sentence_silence: number;
  output_format: string;
}

export interface ConversionResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface ConversionStatusResponse {
  job_id: string;
  status: string;
  progress: number;
  started_at: string;
  completed_at?: string;
  error?: string;
  steps: {
    extraction: { status: string; progress: number };
    processing: { status: string; progress: number };
    synthesis: { status: string; progress: number };
    finalization: { status: string; progress: number };
  };
  output_file?: string;
  duration_estimate?: number;
  chapters: Array<{
    id: string;
    title: string;
    status: string;
    text_length?: number;
    audio_file?: string;
  }>;
}

// Default parameters
export interface DefaultParametersResponse {
  parameters: {
    length_scale: {
      default: number;
      range: [number, number];
      step: number;
      description: string;
    };
    noise_scale: {
      default: number;
      range: [number, number];
      step: number;
      description: string;
    };
    noise_w: {
      default: number;
      range: [number, number];
      step: number;
      description: string;
    };
    sentence_silence: {
      default: number;
      range: [number, number];
      step: number;
      description: string;
    };
  };
  presets: {
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
  };
}

// Component props
export interface VoiceSelectionPanelProps {
  onVoiceSelect: (voice: PreviewVoiceInfo) => void;
  onStartConversion: () => void;
}

export interface VoicePreviewProps {
  onVoiceTest?: (voiceModel: string, settings: VoiceSettings) => void;
  className?: string;
}

export interface VoiceSettings {
  length_scale: number;
  noise_scale: number;
  noise_w: number;
  sentence_silence: number;
}

export interface FileUploadProps {
  onFileUploaded: (response: FileUploadResponse) => void;
  isLoading: boolean;
}
