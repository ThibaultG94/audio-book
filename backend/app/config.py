# --- Config Module ---

class Settings(BaseModel):
    """Application settings"""
    # Directories
    PROCESSING_DIR: str = Field(default="/tmp/tts_processing")
    
    # TTS Settings
    PIPER_MODEL_PATH: str = Field(default="/models/piper/en_US-amy-medium.onnx")
    PIPER_CONFIG_PATH: str = Field(default="/models/piper/en_US-amy-medium.onnx.json")
    OUTPUT_FORMAT: str = Field(default="mp3")
    MAX_CHAPTER_DURATION_MINUTES: int = Field(default=30)
    MAX_TTS_WORKERS: int = Field(default=2)
    
    # API Settings
    ALLOWED_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:8000"])
    MAX_UPLOAD_SIZE_MB: int = Field(default=500)
    
    class Config:
        env_file = ".env"

