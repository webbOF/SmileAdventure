from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query

from ..models.asd_models import (AdaptiveSessionConfig, ASDRecommendation,
                                 ChildProfile, SessionMetrics)
from ..services.asd_game_service import ASDGameService

router = APIRouter(prefix="/asd", tags=["ASD Support"])

# Initialize ASD Game Service
asd_service = ASDGameService()

@router.post("/session/create-adaptive", tags=["ASD Support"])
async def create_adaptive_session(
    child_profile: ChildProfile,
    session_id: str = Query(..., description="Game session ID")
):
    """Create an adaptive game session for a child with ASD"""
    try:
        config = await asd_service.create_adaptive_session(child_profile, session_id)
        return {
            "success": True,
            "message": "Adaptive session created successfully",
            "data": config.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create adaptive session: {str(e)}")

@router.post("/overstimulation/detect", tags=["ASD Support"])
async def detect_overstimulation(session_metrics: SessionMetrics):
    """Detect overstimulation based on session metrics"""
    try:
        is_overstimulated, indicators, intervention = await asd_service.detect_overstimulation(session_metrics)
        
        return {
            "success": True,
            "data": {
                "is_overstimulated": is_overstimulated,
                "indicators": indicators,
                "recommended_intervention": intervention,
                "overstimulation_score": session_metrics.overstimulation_score
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect overstimulation: {str(e)}")

@router.post("/intervention/trigger", tags=["ASD Support"])
async def trigger_calming_intervention(
    session_id: str = Query(..., description="Game session ID"),
    intervention_type: str = Query(..., description="Type of intervention to trigger")
):
    """Trigger a calming intervention for overstimulation"""
    try:
        intervention = await asd_service.trigger_calming_intervention(session_id, intervention_type)
        return {
            "success": True,
            "message": "Calming intervention triggered",
            "data": intervention.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger intervention: {str(e)}")

@router.post("/environment/adjust", tags=["ASD Support"])
async def adjust_environmental_settings(
    session_id: str = Query(..., description="Game session ID"),
    overstimulation_level: float = Query(..., ge=0.0, le=1.0, description="Current overstimulation level")
):
    """Dynamically adjust environmental settings based on overstimulation"""
    try:
        adjustments = await asd_service.adjust_environmental_settings(session_id, overstimulation_level)
        return {
            "success": True,
            "message": "Environmental settings adjusted",
            "data": adjustments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to adjust environment: {str(e)}")

@router.post("/recommendations/generate", tags=["ASD Support"])
async def generate_asd_recommendations(progress_data: Dict[str, Any]):
    """Generate ASD-specific recommendations based on progress data"""
    try:
        recommendations = await asd_service.generate_asd_recommendations(progress_data)
        return {
            "success": True,
            "message": f"Generated {len(recommendations)} recommendations",
            "data": [rec.dict() for rec in recommendations]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.get("/child-profile/{child_id}", tags=["ASD Support"])
async def get_child_profile(child_id: int):
    """Get stored child profile"""
    try:
        if child_id in asd_service.child_profiles:
            profile = asd_service.child_profiles[child_id]
            return {
                "success": True,
                "data": profile.dict()
            }
        else:
            raise HTTPException(status_code=404, detail="Child profile not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get child profile: {str(e)}")

@router.get("/session/{session_id}/metrics", tags=["ASD Support"])
async def get_session_metrics(session_id: str):
    """Get session metrics for analysis"""
    try:
        if session_id in asd_service.session_metrics:
            metrics = asd_service.session_metrics[session_id]
            return {
                "success": True,
                "data": [metric.dict() for metric in metrics]
            }
        else:
            return {
                "success": True,
                "data": [],
                "message": "No metrics found for session"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session metrics: {str(e)}")

@router.get("/session/{session_id}/config", tags=["ASD Support"])
async def get_adaptive_config(session_id: str):
    """Get adaptive configuration for a session"""
    try:
        if session_id in asd_service.adaptive_sessions:
            config = asd_service.adaptive_sessions[session_id]
            return {
                "success": True,
                "data": config.dict()
            }
        else:
            raise HTTPException(status_code=404, detail="Adaptive session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get adaptive config: {str(e)}")

@router.get("/interventions/available", tags=["ASD Support"])
async def get_available_interventions():
    """Get list of available calming interventions"""
    try:
        interventions = {}
        for key, intervention in asd_service.calming_interventions.items():
            interventions[key] = intervention.dict()
        
        return {
            "success": True,
            "data": interventions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get interventions: {str(e)}")

@router.post("/session/{session_id}/report", tags=["ASD Support"])
async def generate_session_report(
    session_id: str,
    include_recommendations: bool = Query(True, description="Include recommendations in report")
):
    """Generate comprehensive ASD session report"""
    try:
        # Get session data
        config = asd_service.adaptive_sessions.get(session_id)
        metrics = asd_service.session_metrics.get(session_id, [])
        
        if not config:
            raise HTTPException(status_code=404, detail="Adaptive session not found")
        
        # Generate recommendations if requested
        recommendations = []
        if include_recommendations and metrics:
            progress_data = {
                "session_id": session_id,
                "child_id": config.child_profile.child_id,
                "metrics": [m.dict() for m in metrics]
            }
            recommendations = await asd_service.generate_asd_recommendations(progress_data)
        
        # Calculate session statistics
        if metrics:
            session_duration = int((metrics[-1].timestamp - metrics[0].timestamp).total_seconds())
            total_interactions = sum(m.actions_per_minute for m in metrics)
            overstimulation_events = [m for m in metrics if m.overstimulation_score > 0.6]
        else:
            session_duration = 0
            total_interactions = 0
            overstimulation_events = []
        
        report = {
            "session_id": session_id,
            "child_profile": config.child_profile.dict(),
            "session_duration": session_duration,
            "total_interactions": int(total_interactions),
            "adaptations_made": [config.sensory_adjustments, config.pacing_adjustments],
            "overstimulation_events": [{"timestamp": e.timestamp, "score": e.overstimulation_score} for e in overstimulation_events],
            "recommendations": [rec.dict() for rec in recommendations],
            "created_at": datetime.now()
        }
        
        return {
            "success": True,
            "message": "Session report generated successfully",
            "data": report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate session report: {str(e)}")
