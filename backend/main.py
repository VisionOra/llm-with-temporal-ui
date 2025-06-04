import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
from typing import Dict, Any

from temporal_client import TemporalClient
from llm_service import LLMService

load_dotenv()

app = FastAPI(title="Temporal LLM Web App", version="1.0.0")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Initialize services
temporal_client = TemporalClient()
llm_service = LLMService()

class ReverseRequest(BaseModel):
    text: str

class LLMRequest(BaseModel):
    text: str
    operation: str = "summarize"  # summarize, rephrase, etc.

class ResponseModel(BaseModel):
    success: bool
    result: str
    workflow_id: str = None
    error: str = None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    try:
        with open("../frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Frontend not found</h1>")

@app.post("/api/reverse", response_model=ResponseModel)
async def reverse_string(request: ReverseRequest):
    """Trigger Temporal workflow to reverse a string"""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        result = await temporal_client.execute_reverse_workflow(request.text)
        
        return ResponseModel(
            success=True,
            result=result["reversed_text"],
            workflow_id=result["workflow_id"]
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            result="",
            error=str(e)
        )

@app.post("/api/llm", response_model=ResponseModel)
async def llm_operation(request: LLMRequest):
    """Perform LLM operation (summarize, rephrase, etc.)"""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        result = await llm_service.process_text(request.text, request.operation)
        
        return ResponseModel(
            success=True,
            result=result
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            result="",
            error=str(e)
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    temporal_healthy = await temporal_client.health_check()
    llm_healthy = await llm_service.health_check()
    
    return {
        "status": "healthy" if temporal_healthy and llm_healthy else "unhealthy",
        "services": {
            "temporal": "healthy" if temporal_healthy else "unhealthy",
            "llm": "healthy" if llm_healthy else "unhealthy"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 