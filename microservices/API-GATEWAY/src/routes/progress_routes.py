# API Gateway Progress Tracking Routes
import os
from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException

from ..auth.jwt_auth import get_current_user

router = APIRouter()

GAME_SERVICE_URL = os.getenv("GAME_SERVICE_URL", "http://game:8005/api/v1")
SERVICE_UNAVAILABLE_MSG = "Game service unavailable"

@router.get("/health", tags=["Progress Tracking"])
async def progress_health():
    """Health check endpoint for progress tracking service."""
    try:
        async with httpx.AsyncClient() as client:
            progress_status_url = f"{GAME_SERVICE_URL}/game/progress/summary/1"  # Test endpoint
            response = await client.get(progress_status_url, timeout=5.0)
            if response.status_code in [200, 404]:  # 404 is ok for test child_id
                return {"status": "online", "service": "progress_tracking"}
            else:
                return {"status": "degraded", "service": "progress_tracking", "code": response.status_code}
    except Exception as e:
        return {"status": "offline", "service": "progress_tracking", "error": str(e)}


@router.post("/initialize", tags=["Progress Tracking"])
async def initialize_progress_tracking(
    request_body: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Initialize progress tracking for a child."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/initialize"
            response = await client.post(target_url, json=request_body, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to initialize progress tracking"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.get("/config/{child_id}", tags=["Progress Tracking"])
async def get_tracking_config(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get progress tracking configuration for a child."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/config/{child_id}"
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get tracking config"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.post("/behavioral-data", tags=["Progress Tracking"])
async def record_behavioral_data(
    request_body: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Record behavioral observation data."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/behavioral-data"
            response = await client.post(target_url, json=request_body, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to record behavioral data"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.post("/emotional-transitions", tags=["Progress Tracking"])
async def record_emotional_transitions(
    request_body: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Record emotional state transitions during sessions."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/emotional-transitions"
            response = await client.post(target_url, json=request_body, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to record emotional transitions"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.post("/skill-assessments", tags=["Progress Tracking"])
async def record_skill_assessments(
    request_body: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Record skill assessments for progress tracking."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/skill-assessments"
            response = await client.post(target_url, json=request_body, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to record skill assessments"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.post("/session-analysis", tags=["Progress Tracking"])
async def analyze_session_for_progress(
    request_body: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze a game session for progress indicators."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/session-analysis"
            response = await client.post(target_url, json=request_body, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to analyze session for progress"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.get("/behavioral-patterns/{child_id}", tags=["Progress Tracking"])
async def get_behavioral_pattern_analysis(
    child_id: int,
    pattern_type: str = None,
    days: int = 14,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get behavioral pattern analysis for a child."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/behavioral-patterns/{child_id}"
            params = {"days": days}
            if pattern_type:
                params["pattern_type"] = pattern_type
            
            response = await client.get(target_url, params=params, timeout=15.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get behavioral pattern analysis"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.get("/emotional-progression/{child_id}", tags=["Progress Tracking"])
async def get_emotional_progression_analysis(
    child_id: int,
    days: int = 14,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get emotional state progression analysis for a child."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/emotional-progression/{child_id}"
            params = {"days": days}
            response = await client.get(target_url, params=params, timeout=15.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get emotional progression analysis"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.get("/milestones/{child_id}", tags=["Progress Tracking"])
async def get_milestone_achievements(
    child_id: int,
    milestone_type: str = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get milestone achievements for a child."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/milestones/{child_id}"
            params = {}
            if milestone_type:
                params["milestone_type"] = milestone_type
            
            response = await client.get(target_url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get milestone achievements"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.post("/milestones/detect", tags=["Progress Tracking"])
async def detect_milestones_from_session(
    request_body: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Detect milestone achievements from session data."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/milestones/detect"
            response = await client.post(target_url, json=request_body, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to detect milestones"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.post("/goals", tags=["Progress Tracking"])
async def set_progress_goals(
    request_body: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Set progress goals for a child."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/goals"
            response = await client.post(target_url, json=request_body, timeout=20.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to set progress goals"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.get("/goals/{child_id}", tags=["Progress Tracking"])
async def get_progress_goals(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get progress goals for a child."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/goals/{child_id}"
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get progress goals"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.get("/goals/{child_id}/progress", tags=["Progress Tracking"])
async def evaluate_goal_progress(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Evaluate progress toward goals for a child."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/goals/{child_id}/progress"
            response = await client.get(target_url, timeout=15.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to evaluate goal progress"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.get("/real-time/{session_id}", tags=["Progress Tracking"])
async def get_real_time_progress_metrics(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get real-time progress metrics for an active session."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/real-time/{session_id}"
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get real-time metrics"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.get("/dashboard/{child_id}", tags=["Progress Tracking"])
async def get_progress_dashboard_data(
    child_id: int,
    days: int = 30,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get comprehensive dashboard data for progress visualization."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/dashboard/{child_id}"
            params = {"days": days}
            response = await client.get(target_url, params=params, timeout=20.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get dashboard data"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.post("/reports/generate", tags=["Progress Tracking"])
async def generate_progress_report(
    request_body: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate comprehensive progress report."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/reports/generate"
            response = await client.post(target_url, json=request_body, timeout=60.0)  # Longer timeout for report generation
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to generate progress report"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.get("/reports/{child_id}/latest", tags=["Progress Tracking"])
async def get_latest_progress_report(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get the latest progress report for a child."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/reports/{child_id}/latest"
            response = await client.get(target_url, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get latest progress report"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.get("/analytics/{child_id}/trends", tags=["Progress Tracking"])
async def get_progress_trends(
    child_id: int,
    metric_type: str,
    days: int = 90,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get detailed progress trends and analytics."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/analytics/{child_id}/trends"
            params = {"metric_type": metric_type, "days": days}
            response = await client.get(target_url, params=params, timeout=20.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get progress trends"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.get("/insights/{child_id}", tags=["Progress Tracking"])
async def get_clinical_insights(
    child_id: int,
    insight_type: str = "all",
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get clinical insights and recommendations based on progress data."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/insights/{child_id}"
            params = {"insight_type": insight_type}
            response = await client.get(target_url, params=params, timeout=15.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get clinical insights"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.get("/alerts/{child_id}", tags=["Progress Tracking"])
async def get_progress_alerts(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get progress alerts and warnings for a child."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/alerts/{child_id}"
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get progress alerts"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.get("/export/{child_id}", tags=["Progress Tracking"])
async def export_progress_data(
    child_id: int,
    format: str = "json",
    start_date: str = None,
    end_date: str = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Export progress tracking data in various formats."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/export/{child_id}"
            params = {"format": format}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            
            response = await client.get(target_url, params=params, timeout=60.0)  # Longer timeout for export
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to export progress data"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)


@router.get("/summary/{child_id}", tags=["Progress Tracking"])
async def get_progress_summary(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a concise progress summary for quick overview."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/progress/summary/{child_id}"
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get progress summary"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)
