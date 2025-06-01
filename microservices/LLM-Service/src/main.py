import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .config.settings import get_settings
from .middleware import (authenticate_request, rate_limit_middleware,
                         security_headers_middleware)
from .models.llm_models import (BehavioralAnalysis, EmotionalAnalysis,
                                GameSessionData, LLMAnalysisRequest,
                                LLMAnalysisResponse, LLMHealthResponse,
                                ProgressAnalysis, Recommendations,
                                SessionInsights)
from .monitoring import metrics, metrics_middleware, setup_logging
from .services.llm_service import LLMService

# Initialize settings and services
settings = get_settings()

# Configure logging
setup_logging(log_level=settings.LOG_LEVEL, log_file="logs/llm-service.log")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LLM Service",
    description="AI-powered analysis service for ASD game sessions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security, rate limiting, and metrics middleware
app.middleware("http")(metrics_middleware)
app.middleware("http")(security_headers_middleware)
app.middleware("http")(rate_limit_middleware)

# Initialize LLM service
llm_service = LLMService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting LLM Service...")
    await llm_service.initialize()
    logger.info("LLM Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down LLM Service...")
    await llm_service.cleanup()
    logger.info("LLM Service shut down successfully")

@app.get("/health", response_model=LLMHealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check OpenAI API connectivity
        openai_status = await llm_service.check_openai_connectivity()
        
        return LLMHealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            openai_status=openai_status,
            service_version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return LLMHealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            openai_status="disconnected",
            service_version="1.0.0",
            error=str(e)
        )

@app.post("/analyze-session", response_model=LLMAnalysisResponse)
async def analyze_session(
    request: LLMAnalysisRequest,
    auth: dict = Depends(authenticate_request)
):
    """
    Analyze a game session using OpenAI GPT models
    
    This endpoint processes game session data and provides:
    - Emotional analysis and patterns
    - Behavioral insights and recommendations
    - Progress assessment
    - Personalized intervention suggestions
    """
    try:
        logger.info(f"Analyzing session {request.session_data.session_id} for child {request.session_data.child_id}")
        
        # Perform comprehensive session analysis
        analysis_result = await llm_service.analyze_game_session(
            session_data=request.session_data,
            analysis_type=request.analysis_type,
            include_recommendations=request.include_recommendations,
            child_context=request.child_context
        )
        
        logger.info(f"Analysis completed for session {request.session_data.session_id}")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error analyzing session {request.session_data.session_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze session: {str(e)}"
        )

@app.post("/analyze-emotional-patterns", response_model=EmotionalAnalysis)
async def analyze_emotional_patterns(
    session_data: GameSessionData,
    auth: dict = Depends(authenticate_request)
):
    """Analyze emotional patterns in game session data"""
    try:
        logger.info(f"Analyzing emotional patterns for session {session_data.session_id}")
        
        emotional_analysis = await llm_service.analyze_emotional_patterns(session_data)
        
        return emotional_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing emotional patterns: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze emotional patterns: {str(e)}"
        )

@app.post("/analyze-behavioral-patterns", response_model=BehavioralAnalysis)
async def analyze_behavioral_patterns(session_data: GameSessionData):
    """Analyze behavioral patterns and provide insights"""
    try:
        logger.info(f"Analyzing behavioral patterns for session {session_data.session_id}")
        
        behavioral_analysis = await llm_service.analyze_behavioral_patterns(session_data)
        
        return behavioral_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing behavioral patterns: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze behavioral patterns: {str(e)}"
        )

@app.post("/generate-recommendations", response_model=Recommendations)
async def generate_recommendations(
    session_data: GameSessionData,
    analysis_context: Optional[Dict[str, Any]] = None
):
    """Generate personalized recommendations based on session analysis"""
    try:
        logger.info(f"Generating recommendations for session {session_data.session_id}")
        
        recommendations = await llm_service.generate_recommendations(
            session_data=session_data,
            context=analysis_context
        )
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

@app.post("/analyze-progress", response_model=ProgressAnalysis)
async def analyze_progress(
    session_history: List[GameSessionData],
    child_id: int,
    analysis_timeframe_days: Optional[int] = 30
):
    """Analyze progress trends across multiple sessions"""
    try:
        logger.info(f"Analyzing progress for child {child_id} over {len(session_history)} sessions")
        
        progress_analysis = await llm_service.analyze_progress_trends(
            session_history=session_history,
            child_id=child_id,
            timeframe_days=analysis_timeframe_days
        )
        
        return progress_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing progress: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze progress: {str(e)}"
        )

@app.get("/models/available")
async def get_available_models():
    """Get list of available AI models"""
    try:
        models = await llm_service.get_available_models()
        return {"available_models": models}
    except Exception as e:
        logger.error(f"Error fetching available models: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch available models: {str(e)}"
        )

@app.post("/test-openai-connection")
async def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        result = await llm_service.test_openai_connection()
        return {"status": "success", "details": result}
    except Exception as e:
        logger.error(f"OpenAI connection test failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"OpenAI connection failed: {str(e)}"
        )

@app.get("/metrics")
async def get_metrics(auth: dict = Depends(authenticate_request)):
    """Get service metrics"""
    try:
        service_metrics = metrics.get_metrics()
        return service_metrics
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )
