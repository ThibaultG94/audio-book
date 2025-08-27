import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { VoiceSelector } from '@/components/VoiceSelector';
import { VoiceMetadata } from '@/lib/voice-types';

// Mock fetch
global.fetch = jest.fn();

const mockVoiceWithUsage: VoiceMetadata = {
  name: "Test Voice",
  display_name: "Test Voice (Medium)",
  language: {
    code: "fr_FR",
    name_english: "French",
    name_native: "Français"
  },
  speaker: {
    gender: "female",
    age_range: "adult",
    voice_style: "neutral",
    accent: "standard"
  },
  technical: {
    quality: "medium",
    sample_rate: 22050,
    dataset: "test",
    file_size_mb: 50,
    processing_speed: "medium"
  },
  recommended_usage: ["audiobook", "news"],
  description: "Test voice with usage",
  best_for: "Testing",
  avatar: "🎤",
  color: "#3B82F6",
  model_path: "voices/test/test-voice.onnx"
};

const mockVoiceWithoutUsage: VoiceMetadata = {
  ...mockVoiceWithUsage,
  name: "Voice Without Usage",
  recommended_usage: undefined, // This is the problematic case
  description: "Test voice without usage"
};

const mockVoiceWithEmptyUsage: VoiceMetadata = {
  ...mockVoiceWithUsage,
  name: "Voice With Empty Usage",
  recommended_usage: [], // Empty array case
  description: "Test voice with empty usage"
};

describe('VoiceSelector', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  it('handles voices with undefined recommended_usage', async () => {
    const mockResponse = {
      voices: [mockVoiceWithUsage, mockVoiceWithoutUsage],
      count: 2,
      default_voice: "test-voice"
    };

    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockResponse
    });

    const onVoiceSelect = jest.fn();

    render(
      <VoiceSelector
        onVoiceSelect={onVoiceSelect}
        selectedVoice=""
      />
    );

    // Wait for voices to load
    await waitFor(() => {
      expect(screen.getByText('2 voix disponibles')).toBeInTheDocument();
    });

    // Both voices should be rendered without errors
    expect(screen.getByText('Test Voice (Medium)')).toBeInTheDocument();
    expect(screen.getByText('Voice Without Usage')).toBeInTheDocument();
  });

  it('handles voices with empty recommended_usage array', async () => {
    const mockResponse = {
      voices: [mockVoiceWithEmptyUsage],
      count: 1,
      default_voice: "test-voice"
    };

    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockResponse
    });

    const onVoiceSelect = jest.fn();

    render(
      <VoiceSelector
        onVoiceSelect={onVoiceSelect}
        selectedVoice=""
      />
    );

    await waitFor(() => {
      expect(screen.getByText('1 voix disponibles')).toBeInTheDocument();
    });

    // Voice should render without usage tags
    expect(screen.getByText('Voice With Empty Usage')).toBeInTheDocument();
  });

  it('filters voices by usage without errors', async () => {
    const mockResponse = {
      voices: [mockVoiceWithUsage, mockVoiceWithoutUsage, mockVoiceWithEmptyUsage],
      count: 3,
      default_voice: "test-voice"
    };

    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockResponse
    });

    const onVoiceSelect = jest.fn();

    render(
      <VoiceSelector
        onVoiceSelect={onVoiceSelect}
        selectedVoice=""
      />
    );

    await waitFor(() => {
      expect(screen.getByText('3 voix disponibles')).toBeInTheDocument();
    });

    // Filter by audiobook usage
    const usageFilter = screen.getByDisplayValue('Tous usages');
    fireEvent.change(usageFilter, { target: { value: 'audiobook' } });

    await waitFor(() => {
      // Only the voice with audiobook usage should remain
      expect(screen.getByText('1 voix disponibles')).toBeInTheDocument();
      expect(screen.getByText('Test Voice (Medium)')).toBeInTheDocument();
      expect(screen.queryByText('Voice Without Usage')).not.toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    (fetch as jest.Mock).mockRejectedValue(new Error('API Error'));

    const onVoiceSelect = jest.fn();

    render(
      <VoiceSelector
        onVoiceSelect={onVoiceSelect}
        selectedVoice=""
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Erreur de chargement des voix')).toBeInTheDocument();
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });

    // Should show retry button
    expect(screen.getByText('Réessayer')).toBeInTheDocument();
  });

  it('handles malformed API responses', async () => {
    const malformedResponse = {
      voices: null, // This could cause issues
      count: 0
    };

    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => malformedResponse
    });

    const onVoiceSelect = jest.fn();

    render(
      <VoiceSelector
        onVoiceSelect={onVoiceSelect}
        selectedVoice=""
      />
    );

    await waitFor(() => {
      // Should handle gracefully and show empty state
      expect(screen.getByText('0 voix disponibles')).toBeInTheDocument();
    });
  });

  it('renders usage tags only when available', async () => {
    const mockResponse = {
      voices: [mockVoiceWithUsage, mockVoiceWithoutUsage],
      count: 2,
      default_voice: "test-voice"
    };

    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockResponse
    });

    const onVoiceSelect = jest.fn();

    render(
      <VoiceSelector
        onVoiceSelect={onVoiceSelect}
        selectedVoice=""
      />
    );

    await waitFor(() => {
      expect(screen.getByText('2 voix disponibles')).toBeInTheDocument();
    });

    // Voice with usage should show tags
    const voiceWithUsage = screen.getByText('Test Voice (Medium)').closest('[class*="cursor-pointer"]');
    expect(voiceWithUsage).toContainHTML('audiobook');
    expect(voiceWithUsage).toContainHTML('news');

    // Voice without usage should not have usage tags section
    const voiceWithoutUsage = screen.getByText('Voice Without Usage').closest('[class*="cursor-pointer"]');
    expect(voiceWithoutUsage).not.toContainHTML('audiobook');
  });

  it('calls onVoiceSelect with correct parameters', async () => {
    const mockResponse = {
      voices: [mockVoiceWithUsage],
      count: 1,
      default_voice: "test-voice"
    };

    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockResponse
    });

    const onVoiceSelect = jest.fn();

    render(
      <VoiceSelector
        onVoiceSelect={onVoiceSelect}
        selectedVoice=""
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Test Voice (Medium)')).toBeInTheDocument();
    });

    // Click on voice card
    fireEvent.click(screen.getByText('Test Voice (Medium)'));

    expect(onVoiceSelect).toHaveBeenCalledWith(
      mockVoiceWithUsage.model_path,
      expect.objectContaining({
        name: mockVoiceWithUsage.name,
        model_path: mockVoiceWithUsage.model_path,
        recommended_usage: mockVoiceWithUsage.recommended_usage
      })
    );
  });
});

// Type guard tests
describe('Voice Type Guards', () => {
  it('safely accesses recommended_usage', () => {
    const { safeVoiceAccess } = require('@/lib/voice-types');

    // Test with valid array
    expect(safeVoiceAccess.getRecommendedUsage(mockVoiceWithUsage))
      .toEqual(['audiobook', 'news']);

    // Test with undefined
    expect(safeVoiceAccess.getRecommendedUsage(mockVoiceWithoutUsage))
      .toEqual([]);

    // Test with empty array
    expect(safeVoiceAccess.getRecommendedUsage(mockVoiceWithEmptyUsage))
      .toEqual([]);
  });

  it('checks usage support safely', () => {
    const { safeVoiceAccess } = require('@/lib/voice-types');

    expect(safeVoiceAccess.supportsUsage(mockVoiceWithUsage, 'audiobook'))
      .toBe(true);

    expect(safeVoiceAccess.supportsUsage(mockVoiceWithoutUsage, 'audiobook'))
      .toBe(false);

    expect(safeVoiceAccess.supportsUsage(mockVoiceWithEmptyUsage, 'audiobook'))
      .toBe(false);
  });
});