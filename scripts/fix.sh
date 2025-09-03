#!/bin/bash
# 🎯 FINAL FIX - Solution qui fonctionne VRAIMENT

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🎯 FINAL FIX - Solution qui fonctionne VRAIMENT${NC}"

cd backend

# Clean start
rm -rf venv/ app/ 2>/dev/null || true
python3 -m venv venv
source venv/bin/activate
pip install -q fastapi uvicorn pydantic-settings

# Create structure
mkdir -p app/{api/routes,services,models,core}
find app -name "*.py" -delete 2>/dev/null || true

# __init__.py files
touch app/__init__.py app/api/__init__.py app/api/routes/__init__.py
touch app/services/__init__.py app/models/__init__.py app/core/__init__.py

# 1. Config (ultra-simple)
cat > app/core/config.py << 'EOF'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_TITLE: str = "Audio Book Converter"
    PORT: int = 8001

settings = Settings()
EOF

# 2. Models (sans async)
cat > app/models/conversion.py << 'EOF'
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class Status(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ConversionRequest(BaseModel):
    file_id: str
    voice_model: str = "default"

class ConversionResponse(BaseModel):
    job_id: str
    status: str
    message: str

class ConversionStatusResponse(BaseModel):
    job_id: str              # LE CHAMP CRITIQUE
    status: Status
    progress: int = 0
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
EOF

# 3. Service (SANS asyncio pour éviter les erreurs)
cat > app/services/conversion_service.py << 'EOF'
import threading
import time
from datetime import datetime
from typing import Dict, Any
from uuid import uuid4
from app.models.conversion import ConversionStatusResponse, Status

class ConversionService:
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
    
    def start_conversion(self, file_id: str, voice_model: str = "default") -> str:
        job_id = str(uuid4())
        
        job_data = {
            "job_id": job_id,
            "status": Status.PENDING,
            "progress": 0,
            "started_at": datetime.now(),
            "completed_at": None,
            "error": None
        }
        
        self.jobs[job_id] = job_data
        
        # Démarrer le traitement en arrière-plan (threading, pas asyncio)
        thread = threading.Thread(target=self._process_conversion, args=(job_id,))
        thread.daemon = True
        thread.start()
        
        return job_id
    
    def get_conversion_status(self, job_id: str) -> ConversionStatusResponse:
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job_data = self.jobs[job_id]
        return ConversionStatusResponse(**job_data)
    
    def _process_conversion(self, job_id: str):
        """Traitement en arrière-plan avec threading."""
        try:
            job_data = self.jobs[job_id]
            job_data["status"] = Status.PROCESSING
            
            # Simulation du traitement
            for i in range(1, 5):
                time.sleep(1)  # time.sleep au lieu d'asyncio.sleep
                job_data["progress"] = i * 25
            
            # Conversion terminée
            job_data["status"] = Status.COMPLETED
            job_data["progress"] = 100
            job_data["completed_at"] = datetime.now()
            
        except Exception as e:
            job_data["status"] = Status.FAILED
            job_data["error"] = str(e)
            job_data["completed_at"] = datetime.now()

# Instance globale
conversion_service = ConversionService()
EOF

# 4. Routes
cat > app/api/routes/convert.py << 'EOF'
from fastapi import APIRouter, HTTPException
from app.models.conversion import ConversionRequest, ConversionResponse, ConversionStatusResponse
from app.services.conversion_service import conversion_service

router = APIRouter(prefix="/api/convert", tags=["conversion"])

@router.post("/start", response_model=ConversionResponse)
async def start_conversion(request: ConversionRequest):
    try:
        job_id = conversion_service.start_conversion(
            file_id=request.file_id,
            voice_model=request.voice_model
        )
        return ConversionResponse(
            job_id=job_id,
            status="started",
            message="Conversion started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=ConversionStatusResponse)
async def get_status(job_id: str):
    try:
        return conversion_service.get_conversion_status(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
EOF

# 5. Main app
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes.convert import router

app = FastAPI(title=settings.API_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Audio Book Converter API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
EOF

echo -e "${GREEN}✅ Application créée !${NC}"

# Test SIMPLE (sans asyncio)
echo -e "${BLUE}🧪 Test simple...${NC}"
python -c "
from app.main import app
print('✅ App OK')

from app.models.conversion import ConversionStatusResponse, Status
from datetime import datetime
status = ConversionStatusResponse(job_id='test', status=Status.PROCESSING, started_at=datetime.now())
print(f'✅ Model OK - Job ID: {status.job_id}')

from app.services.conversion_service import conversion_service
print('✅ Service OK')
"

echo -e "\n${GREEN}🎉 SUCCÈS !${NC}"
echo -e "${YELLOW}Démarrer le serveur :${NC}"
echo -e "  ${GREEN}cd backend && source venv/bin/activate${NC}"
echo -e "  ${GREEN}uvicorn app.main:app --reload --port 8001${NC}"
echo -e ""
echo -e "${BLUE}Endpoints :${NC}"
echo -e "  • http://localhost:8001/docs"
echo -e "  • http://localhost:8001/health"