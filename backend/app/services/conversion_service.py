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
