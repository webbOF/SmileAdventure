"""
Enhanced Game Service that integrates standard game functionality with ASD-specific features
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..models.asd_models import (AdaptiveSessionConfig, ASDRecommendation,
                                 ChildProfile, OverstimulationIndicator,
                                 SessionMetrics)
from ..models.game_models import (EndGameRequest, GameActionData, GameResponse,
                                  GameState, StartGameRequest)
from .asd_game_service import ASDGameService
from .game_service import GameService


class EnhancedGameService:
    """Enhanced Game Service with integrated ASD support"""
    
    def __init__(self):
        self.game_service = GameService()
        self.asd_service = ASDGameService()
        
        # Track ASD-enabled sessions
        self.asd_enabled_sessions: Dict[str, bool] = {}
        self.session_start_times: Dict[str, datetime] = {}
    
    async def start_adaptive_game_session(
        self, 
        request: StartGameRequest, 
        child_profile: Optional[ChildProfile] = None
    ) -> GameResponse:
        """
        Start a game session with optional ASD adaptive features
        
        Args:
            request: Standard game start request
            child_profile: Optional ASD child profile for adaptive features
            
        Returns:
            GameResponse with session details and adaptive configuration
        """
        try:
            # Start regular game session
            game_response = await self.game_service.start_game_session(request)
            
            if not game_response.success:
                return game_response
            
            session_id = game_response.session_id
            self.session_start_times[session_id] = datetime.now()
            
            # If child profile provided, enable ASD features
            if child_profile:
                try:
                    adaptive_config = await self.asd_service.create_adaptive_session(
                        child_profile, session_id
                    )
                    self.asd_enabled_sessions[session_id] = True
                    
                    # Enhance response with adaptive configuration
                    game_response.data["adaptive_config"] = adaptive_config.dict()
                    game_response.data["asd_enabled"] = True
                    game_response.message += " (ASD adaptive features enabled)"
                    
                except Exception as e:
                    # ASD features failed, but continue with regular game
                    print(f"ASD features failed for session {session_id}: {str(e)}")
                    self.asd_enabled_sessions[session_id] = False
                    game_response.data["asd_enabled"] = False
                    game_response.data["asd_error"] = str(e)
            else:
                self.asd_enabled_sessions[session_id] = False
                game_response.data["asd_enabled"] = False
            
            return game_response
            
        except Exception as e:
            return GameResponse(
                success=False,
                message=f"Failed to start enhanced game session: {str(e)}"
            )
    
    async def process_enhanced_game_action(self, action_data: GameActionData) -> GameResponse:
        """
        Process game action with real-time ASD monitoring and adaptation
        
        Args:
            action_data: Game action data
            
        Returns:
            GameResponse with action result and any ASD interventions
        """
        try:
            session_id = action_data.session_id
            
            # Process regular game action
            game_response = await self.game_service.process_game_action(action_data)
            
            if not game_response.success:
                return game_response
              # If ASD features are enabled for this session, perform monitoring
            if self.asd_enabled_sessions.get(session_id, False):
                asd_response = await self._monitor_and_adapt(session_id)
                
                # Merge ASD response data
                if asd_response:
                    game_response.data["asd_monitoring"] = asd_response
            
            return game_response
            
        except Exception as e:
            return GameResponse(
                success=False,
                message=f"Failed to process enhanced game action: {str(e)}"
            )
    
    async def _monitor_and_adapt(self, session_id: str) -> Dict[str, Any]:
        """Monitor session for overstimulation and adapt as needed"""
        try:            # Calculate current session metrics
            session_metrics = await self._calculate_session_metrics(session_id)
            
            # Detect overstimulation
            is_overstimulated, indicators, intervention = await self.asd_service.detect_overstimulation(session_metrics)
            
            response_data = {
                "overstimulation_detected": is_overstimulated,
                "indicators": indicators,
                "session_metrics": session_metrics.dict()
            }
            
            # If overstimulation detected, provide intervention guidance
            if is_overstimulated and intervention:
                calming_intervention = await self.asd_service.trigger_calming_intervention(
                    session_id, intervention
                )
                response_data["recommended_intervention"] = calming_intervention.dict()
                
                # Adjust environmental settings
                adjustments = await self.asd_service.adjust_environmental_settings(
                    session_id, session_metrics.overstimulation_score
                )
                response_data["environmental_adjustments"] = adjustments
            
            return response_data
            
        except Exception as e:
            print(f"Error in ASD monitoring for session {session_id}: {str(e)}")
            return {"error": str(e)}
    
    async def _calculate_session_metrics(self, session_id: str) -> SessionMetrics:
        """Calculate real-time session metrics for overstimulation detection"""
        try:
            # Get session start time
            start_time = self.session_start_times.get(session_id, datetime.now())
            session_duration = (datetime.now() - start_time).total_seconds()
            
            # Get game state for analysis
            game_state = self.game_service.active_sessions.get(session_id)
            
            if not game_state:
                # Return default metrics if no game state
                return SessionMetrics(
                    session_id=session_id,
                    timestamp=datetime.now(),
                    actions_per_minute=0.0,
                    error_rate=0.0,
                    pause_frequency=0.0,
                    average_response_time=1.0,
                    progress_rate=0.0,
                    overstimulation_score=0.0
                )
            
            # Get existing metrics for trend analysis
            existing_metrics = self.asd_service.session_metrics.get(session_id, [])
            
            # Calculate actions per minute
            if session_duration > 0:
                # Estimate based on game state and time
                actions_per_minute = min(60.0, max(0.0, (len(existing_metrics) + 1) * 60 / session_duration))
            else:
                actions_per_minute = 1.0
            
            # Calculate error rate (simplified - based on score vs expected progress)
            expected_score = max(1, int(session_duration / 30))  # Expected 1 point per 30 seconds
            actual_score = game_state.score
            error_rate = max(0.0, min(1.0, 1.0 - (actual_score / expected_score)))
            
            # Calculate pause frequency (time between actions)
            if len(existing_metrics) >= 2:
                recent_metrics = existing_metrics[-2:]
                time_diff = (recent_metrics[-1].timestamp - recent_metrics[0].timestamp).total_seconds()
                pause_frequency = max(0.0, min(1.0, time_diff / 60.0))  # Normalize to 0-1
            else:
                pause_frequency = 0.1  # Default low pause frequency
            
            # Calculate average response time (simplified)
            average_response_time = max(0.5, min(10.0, pause_frequency * 10))
            
            # Calculate progress rate
            total_objectives = len(game_state.completed_objectives) + 1  # +1 for current
            completed_objectives = len(game_state.completed_objectives)
            progress_rate = completed_objectives / total_objectives if total_objectives > 0 else 0.0
            
            # Calculate overstimulation score based on multiple factors
            overstimulation_score = 0.0
            
            # High error rate contributes to overstimulation
            overstimulation_score += error_rate * 0.3
            
            # High action frequency might indicate agitation
            if actions_per_minute > 60:  # More than 1 per second
                overstimulation_score += 0.3
            
            # High pause frequency might indicate confusion/overwhelm
            if pause_frequency > 0.5:
                overstimulation_score += 0.2
            
            # Low progress rate with high activity might indicate frustration
            if progress_rate < 0.3 and actions_per_minute > 30:
                overstimulation_score += 0.2
            
            overstimulation_score = min(1.0, overstimulation_score)
            
            return SessionMetrics(
                session_id=session_id,
                timestamp=datetime.now(),
                actions_per_minute=actions_per_minute,
                error_rate=error_rate,
                pause_frequency=pause_frequency,
                average_response_time=average_response_time,
                progress_rate=progress_rate,
                overstimulation_score=overstimulation_score
            )
            
        except Exception as e:
            print(f"Error calculating session metrics: {str(e)}")
            # Return safe default metrics
            return SessionMetrics(
                session_id=session_id,
                timestamp=datetime.now(),
                actions_per_minute=10.0,
                error_rate=0.1,
                pause_frequency=0.1,
                average_response_time=2.0,
                progress_rate=0.5,
                overstimulation_score=0.1
            )
    
    async def generate_session_report(self, session_id: str, user_id: int) -> Dict[str, Any]:
        """Generate comprehensive session report with ASD insights"""
        try:
            # Get basic game session data
            game_state = self.game_service.active_sessions.get(session_id)
            session_data = self.game_service.session_history.get(session_id)
            
            if not game_state or not session_data:
                return {"error": "Session not found"}
            
            # Verify user owns session
            if game_state.user_id != user_id:
                return {"error": "Unauthorized access"}
            
            # Basic session report
            report = {
                "session_id": session_id,
                "user_id": user_id,
                "scenario": game_state.current_scenario,
                "final_score": game_state.score,
                "completed_objectives": game_state.completed_objectives,
                "session_duration": (datetime.now() - session_data.start_time).total_seconds(),
                "asd_enabled": self.asd_enabled_sessions.get(session_id, False)
            }
            
            # Add ASD-specific insights if enabled
            if self.asd_enabled_sessions.get(session_id, False):
                # Generate ASD recommendations
                progress_data = {
                    "session_id": session_id,
                    "child_id": session_data.child_id,
                    "game_state": game_state.dict(),
                    "session_data": session_data.dict()
                }
                
                recommendations = await self.asd_service.generate_asd_recommendations(progress_data)
                
                # Get session metrics summary
                metrics = self.asd_service.session_metrics.get(session_id, [])
                
                if metrics:
                    avg_overstimulation = sum(m.overstimulation_score for m in metrics) / len(metrics)
                    overstimulation_events = len([m for m in metrics if m.overstimulation_score > 0.6])
                else:
                    avg_overstimulation = 0.0
                    overstimulation_events = 0
                
                report["asd_insights"] = {
                    "recommendations": [rec.dict() for rec in recommendations],
                    "average_overstimulation_score": avg_overstimulation,
                    "overstimulation_events": overstimulation_events,
                    "total_metrics_collected": len(metrics),
                    "adaptive_config": self.asd_service.adaptive_sessions.get(session_id, {})
                }
            
            return report
            
        except Exception as e:
            return {"error": f"Failed to generate session report: {str(e)}"}
    
    async def end_enhanced_game_session(self, request: EndGameRequest) -> GameResponse:
        """End game session with ASD session report generation"""
        try:
            # End regular game session
            game_response = await self.game_service.end_game_session(request)
            
            if game_response.success:
                session_id = request.session_id
                
                # Generate comprehensive report
                report = await self.generate_session_report(session_id, request.user_id)
                game_response.data["session_report"] = report
                
                # Clean up session tracking
                self.asd_enabled_sessions.pop(session_id, None)
                self.session_start_times.pop(session_id, None)
            
            return game_response
            
        except Exception as e:
            return GameResponse(
                success=False,
                message=f"Failed to end enhanced game session: {str(e)}"
            )
    
    # Delegate other methods to base game service
    async def get_game_state(self, session_id: str, user_id: int) -> GameResponse:
        """Get game state (delegates to base service)"""
        return await self.game_service.get_game_state(session_id, user_id)
    
    async def get_available_scenarios(self) -> Dict[str, Any]:
        """Get available scenarios (delegates to base service)"""
        return await self.game_service.get_available_scenarios()


# Create global instance
enhanced_game_service = EnhancedGameService()
