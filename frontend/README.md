# 🎨 Audio Book Converter - Frontend

Modern React frontend for the Audio Book Converter application. Built with Next.js 15, TypeScript, and Tailwind CSS for a responsive and intuitive user experience.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ with npm
- Backend API running on port 8001

### Development Setup

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > .env.local
npm run dev
```

### Access Points
- **Main Application**: http://localhost:3001
- **Development Server**: Hot reload enabled

## 🏗️ Architecture

### Project Structure

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── globals.css           # Global styles and Tailwind imports
│   │   ├── layout.tsx            # Root layout component
│   │   ├── page.tsx              # Main application page
│   │   └── convert/
│   │       └── [id]/
│   │           └── page.tsx      # Conversion status page
│   ├── components/               # React components
│   │   ├── VoiceSelector.tsx     # Advanced voice selection interface
│   │   ├── VoicePreview.tsx      # Voice preview and parameter tuning
│   │   ├── FileUpload.tsx        # Drag & drop file upload
│   │   └── ConversionStatus.tsx  # Real-time progress tracking
│   └── lib/                      # Utilities and API client
│       ├── api.ts                # HTTP client with error handling
│       ├── types.ts              # TypeScript type definitions
│       └── voice-types.ts        # Legacy voice types (deprecated)
├── public/                       # Static assets
├── package.json                  # Node.js dependencies and scripts
├── tailwind.config.ts            # Tailwind CSS configuration
├── tsconfig.json                 # TypeScript configuration
├── next.config.ts                # Next.js configuration
└── README.md                     # This file
```

### Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript with strict mode
- **Styling**: Tailwind CSS with custom components
- **State Management**: React hooks (useState, useEffect)
- **HTTP Client**: Custom API client with error handling
- **Build Tool**: Next.js built-in bundler with Turbopack

## 🎨 Components

### VoiceSelector (`components/VoiceSelector.tsx`)

Advanced voice selection interface with filtering and recommendations.

**Features:**
- Lists 7 French TTS voices with metadata
- Filter by gender (male/female) and quality (low/medium/high)
- Sort by name, quality, or file size
- Voice recommendations (fastest, best quality, most natural)
- Visual voice cards with usage tags
- Real-time voice count display

### VoicePreview (`components/VoicePreview.tsx`)

Complete voice testing interface with parameter controls and audio preview.

**Features:**
- Real-time voice preview generation
- Advanced TTS parameter controls (speed, expressiveness, etc.)
- Smart presets (audiobook, news, storytelling)
- Integrated audio player with playback controls
- Parameter validation and error handling
- Auto-loads default parameters from API

### FileUpload (`components/FileUpload.tsx`)

Modern drag-and-drop file upload with validation and progress tracking.

**Features:**
- Drag & drop interface with visual feedback
- File validation (PDF/EPUB, 50MB max)
- Upload progress simulation for better UX
- Error handling with detailed messages
- File format indicators and help text
- Responsive design for mobile/desktop

### ConversionStatus (`components/ConversionStatus.tsx`)

Real-time conversion progress tracking with visual step indicators.

**Features:**
- Multi-step progress visualization
- Real-time status polling every 2 seconds
- Progress percentage with animated bar
- Conversion time tracking
- Integrated audio player for results
- Error handling with retry options
- Download functionality

## 📄 License

This frontend is part of the Audio Book Converter project, licensed under MIT License.

---

**Frontend ready! Start with: `npm run dev`**

*Access at: http://localhost:3001*
