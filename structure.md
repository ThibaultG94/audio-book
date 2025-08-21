audio-book-app/
├── backend/ # Python FastAPI backend
│ ├── app/
│ │ ├── **init**.py
│ │ ├── main.py # FastAPI app entry point
│ │ ├── api/
│ │ │ ├── **init**.py
│ │ │ ├── routes/
│ │ │ │ ├── **init**.py
│ │ │ │ ├── upload.py # File upload endpoints
│ │ │ │ ├── convert.py # TTS conversion endpoints
│ │ │ │ └── audio.py # Audio file serving
│ │ │ └── dependencies.py # FastAPI dependencies
│ │ ├── services/
│ │ │ ├── **init**.py
│ │ │ ├── text_extractor.py # PDF/EPUB text extraction
│ │ │ ├── text_processor.py # Text cleaning & chunking
│ │ │ ├── tts_engine.py # Piper TTS integration
│ │ │ └── audio_processor.py # WAV concatenation & processing
│ │ ├── models/
│ │ │ ├── **init**.py
│ │ │ ├── schemas.py # Pydantic models
│ │ │ └── enums.py # Status enums, etc.
│ │ ├── core/
│ │ │ ├── **init**.py
│ │ │ ├── config.py # Settings & environment
│ │ │ ├── exceptions.py # Custom exceptions
│ │ │ └── logger.py # Structured logging
│ │ └── utils/
│ │ ├── **init**.py
│ │ ├── file_utils.py # File operations
│ │ └── validation.py # Input validation
│ ├── tests/
│ │ ├── **init**.py
│ │ ├── conftest.py # Pytest fixtures
│ │ ├── unit/
│ │ │ ├── test_text_extractor.py
│ │ │ ├── test_text_processor.py
│ │ │ └── test_tts_engine.py
│ │ └── integration/
│ │ └── test_api.py
│ ├── voices/ # TTS voice models
│ │ └── fr/fr_FR/siwis/low/
│ │ ├── fr_FR-siwis-low.onnx
│ │ └── fr_FR-siwis-low.onnx.json
│ ├── storage/ # Generated audio files
│ │ ├── uploads/ # Uploaded PDF/EPUB
│ │ └── outputs/ # Generated WAV/MP3
│ ├── requirements.txt
│ ├── requirements-dev.txt # Dev dependencies
│ └── pyproject.toml # Project config & tools
│
├── frontend/ # Next.js frontend
│ ├── src/
│ │ ├── app/ # App Router (Next.js 13+)
│ │ │ ├── layout.tsx # Root layout
│ │ │ ├── page.tsx # Home page
│ │ │ ├── upload/
│ │ │ │ └── page.tsx # File upload page
│ │ │ ├── convert/
│ │ │ │ └── [id]/
│ │ │ │ └── page.tsx # Conversion status page
│ │ │ └── player/
│ │ │ └── [id]/
│ │ │ └── page.tsx # Audio player page
│ │ ├── components/
│ │ │ ├── ui/ # shadcn/ui components
│ │ │ ├── FileUpload.tsx # File upload component
│ │ │ ├── ConversionStatus.tsx # Progress tracking
│ │ │ ├── AudioPlayer.tsx # Audio playback
│ │ │ └── Layout.tsx # App layout wrapper
│ │ ├── lib/
│ │ │ ├── api.ts # API client functions
│ │ │ ├── types.ts # TypeScript interfaces
│ │ │ ├── utils.ts # Utility functions
│ │ │ └── validations.ts # Form validation schemas
│ │ └── hooks/
│ │ ├── useFileUpload.ts # File upload hook
│ │ ├── useConversionStatus.ts# Status polling hook
│ │ └── useAudioPlayer.ts # Audio player hook
│ ├── public/
│ │ ├── icons/
│ │ └── favicon.ico
│ ├── tests/
│ │ ├── **tests**/
│ │ │ ├── components/
│ │ │ └── pages/
│ │ └── setup.ts # Test setup
│ ├── package.json
│ ├── package-lock.json
│ ├── next.config.js
│ ├── tailwind.config.js
│ ├── tsconfig.json
│ └── eslint.config.js
│
├── docker/ # Docker configuration
│ ├── Dockerfile # Multi-stage build
│ ├── Dockerfile.dev # Development image
│ └── docker-compose.dev.yml # Local development
│
├── scripts/ # Build & deployment scripts
│ ├── build.sh # Production build
│ ├── dev.sh # Development startup
│ └── deploy.sh # CapRover deployment
│
├── docs/ # Documentation
│ ├── README.md # Main documentation
│ ├── API.md # API documentation
│ └── DEPLOYMENT.md # CapRover deployment guide
│
├── captain-definition # CapRover configuration
├── .gitignore # Global gitignore
├── .env.example # Environment variables template
├── Makefile # Development commands
└── README.md # Project overview
