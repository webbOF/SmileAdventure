"""
Progress Tracking API Routes for ASD Children
Provides comprehensive behavioral pattern recognition, emotional state progression analysis,
and clinical milestone tracking endpoints.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel

from ..models.asd_models import (BehavioralDataPoint, BehavioralPattern,
                                 BehavioralPatternAnalysis, ChildProfile,
                                 ClinicalMilestone, ClinicalMilestoneEvent,
                                 CognitiveProgressMetrics,
                                 EmotionalProgressProfile, EmotionalState,
                                 EmotionalStateTransition,
                                 LongTermProgressReport, ProgressDashboardData,
                                 ProgressGoal, ProgressTrackingConfig,
                                 ProgressTrend, RealTimeProgressMetrics,
                                 SensoryProgressProfile, SessionMetrics,
                                 SkillAssessment, SocialCommunicationProgress)
from ..services.progress_tracking_service import ProgressTrackingService

router = APIRouter(prefix="/progress", tags=["Progress Tracking"])

# Initialize Progress Tracking Service
progress_service = ProgressTrackingService()


class ProgressInitRequest(BaseModel):
    """Request model for initializing progress tracking"""
    child_profile: ChildProfile
    config: Optional[ProgressTrackingConfig] = None


class BehavioralDataRequest(BaseModel):
    """Request model for recording behavioral data"""
    child_id: int
    session_id: str
    behavioral_data: List[BehavioralDataPoint]


class EmotionalTransitionRequest(BaseModel):
    """Request model for recording emotional transitions"""
    child_id: int
    session_id: str
    transitions: List[EmotionalStateTransition]


class SkillAssessmentRequest(BaseModel):
    """Request model for skill assessments"""
    child_id: int
    assessments: List[SkillAssessment]


class ProgressGoalRequest(BaseModel):
    """Request model for setting progress goals"""
    child_id: int
    goals: List[ProgressGoal]


class ProgressReportRequest(BaseModel):
    """Request model for generating progress reports"""
    child_id: int
    start_date: datetime
    end_date: datetime
    report_type: str = "comprehensive"  # "behavioral", "emotional", "clinical", "comprehensive"


# ===========================
# INITIALIZATION ENDPOINTS
# ===========================

@router.post("/initialize", tags=["Progress Tracking"])
async def initialize_child_progress_tracking(request: ProgressInitRequest):
    """Initialize comprehensive progress tracking for a child"""
    try:
        config = await progress_service.initialize_child_tracking(
            request.child_profile, 
            request.config
        )
        return {
            "success": True,
            "message": "Progress tracking initialized successfully",
            "data": {
                "child_id": request.child_profile.child_id,
                "config": config.dict(),
                "focus_areas": [area.value for area in config.focus_areas],
                "milestone_targets": [milestone.value for milestone in config.milestone_targets]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize progress tracking: {str(e)}")


@router.get("/config/{child_id}", tags=["Progress Tracking"])
async def get_tracking_config(child_id: int):
    """Get progress tracking configuration for a child"""
    try:
        if child_id in progress_service.tracking_configs:
            config = progress_service.tracking_configs[child_id]
            return {
                "success": True,
                "data": config.dict()
            }
        else:
            raise HTTPException(status_code=404, detail="Tracking configuration not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tracking config: {str(e)}")


# ===========================
# DATA RECORDING ENDPOINTS
# ===========================

@router.post("/behavioral-data", tags=["Progress Tracking"])
async def record_behavioral_data(request: BehavioralDataRequest):
    """Record behavioral observation data"""
    try:
        await progress_service.record_behavioral_data(
            request.child_id,
            request.session_id,
            request.behavioral_data
        )
        return {
            "success": True,
            "message": f"Recorded {len(request.behavioral_data)} behavioral observations",
            "data": {
                "child_id": request.child_id,
                "session_id": request.session_id,
                "observations_count": len(request.behavioral_data)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record behavioral data: {str(e)}")


@router.post("/emotional-transitions", tags=["Progress Tracking"])
async def record_emotional_transitions(request: EmotionalTransitionRequest):
    """Record emotional state transitions during sessions"""
    try:
        await progress_service.record_emotional_transitions(
            request.child_id,
            request.session_id,
            request.transitions
        )
        return {
            "success": True,
            "message": f"Recorded {len(request.transitions)} emotional transitions",
            "data": {
                "child_id": request.child_id,
                "session_id": request.session_id,
                "transitions_count": len(request.transitions)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record emotional transitions: {str(e)}")


@router.post("/skill-assessments", tags=["Progress Tracking"])
async def record_skill_assessments(request: SkillAssessmentRequest):
    """Record skill assessments for progress tracking"""
    try:
        await progress_service.record_skill_assessments(
            request.child_id,
            request.assessments
        )
        return {
            "success": True,
            "message": f"Recorded {len(request.assessments)} skill assessments",
            "data": {
                "child_id": request.child_id,
                "assessments_count": len(request.assessments)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record skill assessments: {str(e)}")


@router.post("/session-analysis", tags=["Progress Tracking"])
async def analyze_session_for_progress(
    child_id: int,
    session_id: str,
    session_metrics: SessionMetrics
):
    """Analyze a game session for progress indicators"""
    try:
        # Generate real-time metrics from session
        real_time_metrics = await progress_service.generate_real_time_metrics(
            child_id, session_id, session_metrics
        )
        
        # Check for milestone achievements
        milestones = await progress_service.detect_milestone_achievements(
            child_id, session_id, session_metrics
        )
        
        return {
            "success": True,
            "message": "Session analyzed for progress indicators",
            "data": {
                "child_id": child_id,
                "session_id": session_id,
                "real_time_metrics": real_time_metrics.dict(),
                "milestones_detected": [m.dict() for m in milestones],
                "analysis_timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze session for progress: {str(e)}")


# ===========================
# BEHAVIORAL PATTERN ANALYSIS
# ===========================

@router.get("/behavioral-patterns/{child_id}", tags=["Progress Tracking"])
async def get_behavioral_pattern_analysis(
    child_id: int,
    pattern_type: Optional[BehavioralPattern] = None,
    days: int = Query(14, description="Number of days to analyze")
):
    """Get behavioral pattern analysis for a child"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        if pattern_type:
            analysis = await progress_service.analyze_behavioral_pattern(
                child_id, pattern_type, start_date, end_date
            )
            return {
                "success": True,
                "data": {
                    "pattern_type": pattern_type.value,
                    "analysis": analysis.dict()
                }
            }
        else:
            # Get analysis for all patterns
            all_patterns = list(BehavioralPattern)
            analyses = {}
            for pattern in all_patterns:
                try:
                    analysis = await progress_service.analyze_behavioral_pattern(
                        child_id, pattern, start_date, end_date
                    )
                    analyses[pattern.value] = analysis.dict()
                except Exception:
                    # Skip patterns with insufficient data
                    continue
            
            return {
                "success": True,
                "data": {
                    "child_id": child_id,
                    "analysis_period": f"{days} days",
                    "patterns": analyses
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get behavioral pattern analysis: {str(e)}")


@router.get("/emotional-progression/{child_id}", tags=["Progress Tracking"])
async def get_emotional_progression_analysis(
    child_id: int,
    days: int = Query(14, description="Number of days to analyze")
):
    """Get emotional state progression analysis for a child"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        progression = await progress_service.analyze_emotional_progression(
            child_id, start_date, end_date
        )
        
        return {
            "success": True,
            "data": {
                "child_id": child_id,
                "analysis_period": f"{days} days",
                "emotional_progression": progression.dict()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get emotional progression analysis: {str(e)}")


# ===========================
# MILESTONE TRACKING
# ===========================

@router.get("/milestones/{child_id}", tags=["Progress Tracking"])
async def get_milestone_achievements(
    child_id: int,
    milestone_type: Optional[ClinicalMilestone] = None
):
    """Get milestone achievements for a child"""
    try:
        milestones = progress_service.milestones.get(child_id, [])
        
        if milestone_type:
            filtered_milestones = [m for m in milestones if m.milestone == milestone_type]
            return {
                "success": True,
                "data": {
                    "child_id": child_id,
                    "milestone_type": milestone_type.value,
                    "achievements": [m.dict() for m in filtered_milestones]
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "child_id": child_id,
                    "all_achievements": [m.dict() for m in milestones],
                    "achievement_count": len(milestones)
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get milestone achievements: {str(e)}")


@router.post("/milestones/detect", tags=["Progress Tracking"])
async def detect_milestones_from_session(
    child_id: int,
    session_id: str,
    session_metrics: SessionMetrics
):
    """Detect milestone achievements from session data"""
    try:
        detected_milestones = await progress_service.detect_milestone_achievements(
            child_id, session_id, session_metrics
        )
        
        return {
            "success": True,
            "message": f"Detected {len(detected_milestones)} milestone achievements",
            "data": {
                "child_id": child_id,
                "session_id": session_id,
                "milestones": [m.dict() for m in detected_milestones]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect milestones: {str(e)}")


# ===========================
# GOALS AND TARGETS
# ===========================

@router.post("/goals", tags=["Progress Tracking"])
async def set_progress_goals(request: ProgressGoalRequest):
    """Set progress goals for a child"""
    try:
        await progress_service.set_progress_goals(request.child_id, request.goals)
        return {
            "success": True,
            "message": f"Set {len(request.goals)} progress goals",
            "data": {
                "child_id": request.child_id,
                "goals": [g.dict() for g in request.goals]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set progress goals: {str(e)}")


@router.get("/goals/{child_id}", tags=["Progress Tracking"])
async def get_progress_goals(child_id: int):
    """Get progress goals for a child"""
    try:
        goals = progress_service.progress_goals.get(child_id, [])
        return {
            "success": True,
            "data": {
                "child_id": child_id,
                "goals": [g.dict() for g in goals],
                "goal_count": len(goals)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress goals: {str(e)}")


@router.get("/goals/{child_id}/progress", tags=["Progress Tracking"])
async def evaluate_goal_progress(child_id: int):
    """Evaluate progress toward goals for a child"""
    try:
        progress_evaluation = await progress_service.evaluate_goal_progress(child_id)
        return {
            "success": True,
            "data": {
                "child_id": child_id,
                "goal_progress": progress_evaluation,
                "evaluation_timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate goal progress: {str(e)}")


# ===========================
# REAL-TIME MONITORING
# ===========================

@router.get("/real-time/{session_id}", tags=["Progress Tracking"])
async def get_real_time_progress_metrics(session_id: str):
    """Get real-time progress metrics for an active session"""
    try:
        if session_id in progress_service.real_time_metrics:
            metrics = progress_service.real_time_metrics[session_id]
            return {
                "success": True,
                "data": metrics.dict()
            }
        else:
            raise HTTPException(status_code=404, detail="Real-time metrics not found for session")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get real-time metrics: {str(e)}")


@router.get("/dashboard/{child_id}", tags=["Progress Tracking"])
async def get_progress_dashboard_data(
    child_id: int,
    days: int = Query(30, description="Number of days for dashboard data")
):
    """Get comprehensive dashboard data for progress visualization"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        dashboard_data = await progress_service.generate_dashboard_data(
            child_id, start_date, end_date
        )
        
        return {
            "success": True,
            "data": dashboard_data.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")


# ===========================
# REPORTING ENDPOINTS
# ===========================

@router.post("/reports/generate", tags=["Progress Tracking"])
async def generate_progress_report(request: ProgressReportRequest):
    """Generate comprehensive progress report"""
    try:
        report = await progress_service.generate_long_term_report(
            request.child_id,
            request.start_date,
            request.end_date
        )
        
        return {
            "success": True,
            "message": "Progress report generated successfully",
            "data": report.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate progress report: {str(e)}")


@router.get("/reports/{child_id}/latest", tags=["Progress Tracking"])
async def get_latest_progress_report(child_id: int):
    """Get the latest progress report for a child"""
    try:
        # Generate report for last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        report = await progress_service.generate_long_term_report(
            child_id, start_date, end_date
        )
        
        return {
            "success": True,
            "data": report.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get latest progress report: {str(e)}")


@router.get("/analytics/{child_id}/trends", tags=["Progress Tracking"])
async def get_progress_trends(
    child_id: int,
    metric_type: str = Query(..., description="Type of metric (behavioral, emotional, cognitive, social)"),
    days: int = Query(90, description="Number of days for trend analysis")
):
    """Get detailed progress trends and analytics"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        trends = await progress_service.analyze_progress_trends(
            child_id, metric_type, start_date, end_date
        )
        
        return {
            "success": True,
            "data": {
                "child_id": child_id,
                "metric_type": metric_type,
                "analysis_period": f"{days} days",
                "trends": trends
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress trends: {str(e)}")


# ===========================
# CLINICAL INSIGHTS
# ===========================

@router.get("/insights/{child_id}", tags=["Progress Tracking"])
async def get_clinical_insights(
    child_id: int,
    insight_type: str = Query("all", description="Type of insights (behavioral, developmental, intervention)")
):
    """Get clinical insights and recommendations based on progress data"""
    try:
        insights = await progress_service.generate_clinical_insights(child_id, insight_type)
        
        return {
            "success": True,
            "data": {
                "child_id": child_id,
                "insight_type": insight_type,
                "insights": insights,
                "generated_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get clinical insights: {str(e)}")


@router.get("/alerts/{child_id}", tags=["Progress Tracking"])
async def get_progress_alerts(child_id: int):
    """Get progress alerts and warnings for a child"""
    try:
        alerts = await progress_service.check_progress_alerts(child_id)
        
        return {
            "success": True,
            "data": {
                "child_id": child_id,
                "alerts": alerts,
                "alert_count": len(alerts),
                "checked_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress alerts: {str(e)}")


# ===========================
# EXPORT AND INTEGRATION
# ===========================

@router.get("/export/{child_id}", tags=["Progress Tracking"])
async def export_progress_data(
    child_id: int,
    format: str = Query("json", description="Export format (json, csv, pdf)"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Export progress tracking data in various formats"""
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=90)
        if not end_date:
            end_date = datetime.now()
        
        exported_data = await progress_service.export_progress_data(
            child_id, format, start_date, end_date
        )
        
        return {
            "success": True,
            "message": f"Progress data exported in {format} format",
            "data": exported_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export progress data: {str(e)}")


@router.get("/summary/{child_id}", tags=["Progress Tracking"])
async def get_progress_summary(child_id: int):
    """Get a concise progress summary for quick overview"""
    try:
        summary = await progress_service.generate_progress_summary(child_id)
        
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress summary: {str(e)}")


# ===========================
# MISSING ENDPOINTS FOR TESTS
# ===========================

@router.post("/skill-assessment", tags=["Progress Tracking"])
async def update_skill_assessment(
    child_id: int = Body(...),
    skill_name: str = Body(...),
    new_score: float = Body(...),
    assessment_method: str = Body(...),
    notes: Optional[str] = Body(None)
):
    """Update skill assessment for a child"""
    try:        # Create a skill assessment object
        skill_assessment = SkillAssessment(
            skill_name=skill_name,
            skill_category="cognitive",  # Default category
            baseline_score=max(0.0, new_score - 0.1),  # Slightly lower baseline
            current_score=new_score,
            target_score=min(new_score + 0.1, 1.0),  # Slightly higher target
            assessment_date=datetime.now(),
            assessment_method=assessment_method,
            notes=notes or ""
        )
        
        # Record the skill assessment
        await progress_service.record_skill_assessments(child_id, [skill_assessment])
        
        return {
            "success": True,
            "message": f"Skill assessment updated for {skill_name}",
            "data": {
                "child_id": child_id,
                "skill_name": skill_name,
                "new_score": new_score,
                "assessment_method": assessment_method,
                "updated_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update skill assessment: {str(e)}")


@router.get("/metrics/{child_id}", tags=["Progress Tracking"])
async def get_real_time_metrics(child_id: int):
    """Get real-time progress metrics for a child"""
    try:
        # Generate real-time metrics
        metrics = await progress_service.get_child_metrics(child_id)
        
        return {
            "child_id": child_id,
            "timestamp": datetime.now().isoformat(),
            "behavioral_scores": metrics.get("behavioral_scores", {}),
            "emotional_state_distribution": metrics.get("emotional_state_distribution", {}),
            "skill_progression": metrics.get("skill_progression", {}),
            "recent_achievements": metrics.get("recent_achievements", []),
            "areas_for_improvement": metrics.get("areas_for_improvement", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get real-time metrics: {str(e)}")


@router.get("/analysis/behavioral-patterns/{child_id}", tags=["Progress Tracking"])
async def analyze_behavioral_patterns(
    child_id: int,
    pattern_type: Optional[str] = Query(None, description="Type of pattern to analyze")
):
    """Analyze behavioral patterns for a child"""
    try:
        # Get behavioral pattern analysis
        analysis = await progress_service.analyze_behavioral_patterns(child_id, pattern_type)
        
        return {
            "pattern_type": pattern_type or "comprehensive",
            "overall_score": analysis.get("overall_score", 0.0),
            "trend": analysis.get("trend", "stable"),
            "recommendations": analysis.get("recommendations", []),
            "pattern_details": analysis.get("pattern_details", {}),
            "analysis_date": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze behavioral patterns: {str(e)}")


@router.post("/reports/long-term", tags=["Progress Tracking"])
async def generate_long_term_report(
    child_id: int = Body(...),
    start_date: str = Body(...),
    end_date: str = Body(...),
    include_recommendations: bool = Body(True)
):
    """Generate long-term progress report for a child"""
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Generate comprehensive report
        report = await progress_service.generate_long_term_report(
            child_id, start_dt, end_dt, include_recommendations
        )
        
        return {
            "report_period": {
                "start_date": start_date,
                "end_date": end_date,
                "duration_days": (end_dt - start_dt).days
            },
            "behavioral_summary": report.get("behavioral_summary", {}),
            "emotional_summary": report.get("emotional_summary", {}),
            "skill_development": report.get("skill_development", {}),
            "milestone_achievements": report.get("milestone_achievements", []),
            "recommendations": report.get("recommendations", []) if include_recommendations else [],
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate long-term report: {str(e)}")
