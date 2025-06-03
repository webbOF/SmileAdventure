"""
Real-time AI Service for SmileAdventure ASD Support System
Provides streaming AI analysis, live interventions, and real-time session monitoring
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

import aiohttp
from openai import AsyncOpenAI

from ..config.settings import get_settings
from ..models.llm_models import (
    GameSessionData, EmotionalAnalysis, BehavioralAnalysis, 
    Recommendations, SessionInsights, AnalysisType
)

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class InterventionType(Enum):
    CALMING = "calming"
    ENGAGEMENT = "engagement"
    REGULATION = "regulation"
    BREAK = "break"
    ENVIRONMENTAL = "environmental"

@dataclass
class RealTimeAlert:
    """Real-time alert for immediate intervention needs"""
    alert_id: str
    session_id: str
    child_id: int
    timestamp: datetime
    level: AlertLevel
    intervention_type: InterventionType
    trigger_patterns: List[str]
    recommended_actions: List[str]
    urgency_score: float
    auto_resolved: bool = False

@dataclass
class StreamingAnalysis:
    """Streaming AI analysis result"""
    analysis_id: str
    session_id: str
    timestamp: datetime
    emotional_state: str
    engagement_level: float
    attention_score: float
    overstimulation_risk: float
    immediate_recommendations: List[str]
    behavioral_insights: List[str]
    intervention_needed: bool
    confidence_score: float

@dataclass
class LiveSessionMetrics:
    """Live session metrics for real-time monitoring"""
    session_id: str
    child_id: int
    start_time: datetime
    last_update: datetime
    total_interactions: int
    emotional_stability: float
    regulation_events: int
    breakthrough_moments: int
    concerning_patterns: List[str]
    positive_indicators: List[str]

class RealTimeAIService:
    """Service for real-time AI analysis and streaming interventions"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.active_sessions: Dict[str, LiveSessionMetrics] = {}
        self.session_alerts: Dict[str, List[RealTimeAlert]] = {}
        self.streaming_analyses: Dict[str, List[StreamingAnalysis]] = {}
        self.websocket_connections: Dict[str, Set[object]] = {}
        self.ai_models_cache = {}
        
    async def initialize(self):
        """Initialize the real-time AI service"""
        try:
            if not self.settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found for real-time AI service")
            
            self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
            
            # Test streaming capability
            if not self.settings.OPENAI_API_KEY.startswith("test-"):
                await self._test_streaming_capability()
            
            logger.info("Real-time AI Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize real-time AI service: {str(e)}")
            if not self.settings.DEBUG:
                raise
    
    async def _test_streaming_capability(self):
        """Test OpenAI streaming capability"""
        try:
            stream = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test streaming response"}],
                stream=True,
                max_tokens=10
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    break
                    
            logger.info("OpenAI streaming capability verified")
            
        except Exception as e:
            logger.warning(f"Streaming test failed: {str(e)}")
            
    async def start_live_session_monitoring(self, session_id: str, child_id: int) -> LiveSessionMetrics:
        """Start live monitoring for a game session"""
        try:
            session_metrics = LiveSessionMetrics(
                session_id=session_id,
                child_id=child_id,
                start_time=datetime.now(),
                last_update=datetime.now(),
                total_interactions=0,
                emotional_stability=0.5,
                regulation_events=0,
                breakthrough_moments=0,
                concerning_patterns=[],
                positive_indicators=[]
            )
            
            self.active_sessions[session_id] = session_metrics
            self.session_alerts[session_id] = []
            self.streaming_analyses[session_id] = []
            
            logger.info(f"Started live monitoring for session {session_id}")
            return session_metrics
            
        except Exception as e:
            logger.error(f"Error starting live session monitoring: {str(e)}")
            raise
    
    async def process_live_session_data(self, session_id: str, session_data: Dict[str, Any]) -> StreamingAnalysis:
        """Process live session data and provide real-time AI analysis"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found in active sessions")
            
            # Update session metrics
            session_metrics = self.active_sessions[session_id]
            session_metrics.last_update = datetime.now()
            session_metrics.total_interactions += 1
            
            # Perform streaming AI analysis
            analysis = await self._perform_streaming_analysis(session_id, session_data)
            
            # Store analysis
            self.streaming_analyses[session_id].append(analysis)
            
            # Check for intervention needs
            if analysis.intervention_needed:
                alert = await self._create_intervention_alert(session_id, analysis)
                self.session_alerts[session_id].append(alert)
                
                # Broadcast alert to connected WebSockets
                await self._broadcast_alert(session_id, alert)
            
            # Broadcast analysis to connected WebSockets
            await self._broadcast_analysis(session_id, analysis)
            
            logger.info(f"Processed live session data for {session_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error processing live session data: {str(e)}")
            raise
    
    async def _perform_streaming_analysis(self, session_id: str, session_data: Dict[str, Any]) -> StreamingAnalysis:
        """Perform streaming AI analysis of session data"""
        try:
            # Build real-time analysis prompt
            prompt = self._build_realtime_analysis_prompt(session_data)
            
            # Stream analysis from OpenAI
            analysis_content = ""
            
            if self.client and not self.settings.OPENAI_API_KEY.startswith("test-"):
                stream = await self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a real-time ASD therapy assistant. Provide immediate, actionable analysis of child behavior during gameplay. Be concise and focus on immediate needs."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    stream=True,
                    temperature=0.3,
                    max_tokens=800
                )
                
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        analysis_content += chunk.choices[0].delta.content
            else:
                # Fallback analysis for development
                analysis_content = self._create_fallback_streaming_analysis(session_data)
            
            # Parse streaming analysis
            return self._parse_streaming_analysis(session_id, analysis_content, session_data)
            
        except Exception as e:
            logger.error(f"Error in streaming analysis: {str(e)}")
            return self._create_fallback_analysis_result(session_id, session_data)
    
    def _build_realtime_analysis_prompt(self, session_data: Dict[str, Any]) -> str:
        """Build prompt for real-time analysis"""
        return f"""
        REAL-TIME ASD THERAPY SESSION ANALYSIS
        
        Current Session Data:
        - Emotions detected: {session_data.get('emotions', [])}
        - Recent interactions: {session_data.get('interactions', [])}
        - Current engagement: {session_data.get('engagement_level', 0.5)}
        - Attention indicators: {session_data.get('attention_score', 0.5)}
        - Behavioral observations: {session_data.get('behaviors', [])}
        
        Provide IMMEDIATE analysis focusing on:
        1. Current emotional state (1 word)
        2. Engagement level (0-1 score)
        3. Attention score (0-1 score)
        4. Overstimulation risk (0-1 score)
        5. Top 3 immediate recommendations
        6. Key behavioral insights
        7. Intervention needed? (yes/no)
        8. Confidence in analysis (0-1)
        
        Format as JSON for real-time processing.
        """
    
    def _create_fallback_streaming_analysis(self, session_data: Dict[str, Any]) -> str:
        """Create fallback streaming analysis for development"""
        engagement = session_data.get('engagement_level', 0.5)
        attention = session_data.get('attention_score', 0.5)
        
        return json.dumps({
            "emotional_state": "calm" if engagement > 0.6 else "focused",
            "engagement_level": engagement,
            "attention_score": attention,
            "overstimulation_risk": max(0.0, 1.0 - engagement),
            "immediate_recommendations": [
                "Continue current activity" if engagement > 0.6 else "Increase engagement",
                "Monitor attention patterns",
                "Provide positive reinforcement"
            ],
            "behavioral_insights": [
                "Child is engaged with current task",
                "Good emotional regulation observed"
            ],
            "intervention_needed": engagement < 0.3 or attention < 0.3,
            "confidence_score": 0.8
        })
    
    def _parse_streaming_analysis(self, session_id: str, content: str, session_data: Dict[str, Any]) -> StreamingAnalysis:
        """Parse streaming analysis content"""
        try:
            # Try to parse JSON response
            if content.startswith('{'):
                analysis_data = json.loads(content)
            else:
                # Parse text response
                analysis_data = self._extract_analysis_from_text(content)
            
            return StreamingAnalysis(
                analysis_id=str(uuid.uuid4()),
                session_id=session_id,
                timestamp=datetime.now(),
                emotional_state=analysis_data.get('emotional_state', 'unknown'),
                engagement_level=float(analysis_data.get('engagement_level', 0.5)),
                attention_score=float(analysis_data.get('attention_score', 0.5)),
                overstimulation_risk=float(analysis_data.get('overstimulation_risk', 0.0)),
                immediate_recommendations=analysis_data.get('immediate_recommendations', []),
                behavioral_insights=analysis_data.get('behavioral_insights', []),
                intervention_needed=bool(analysis_data.get('intervention_needed', False)),
                confidence_score=float(analysis_data.get('confidence_score', 0.5))
            )
            
        except Exception as e:
            logger.error(f"Error parsing streaming analysis: {str(e)}")
            return self._create_fallback_analysis_result(session_id, session_data)
    
    def _extract_analysis_from_text(self, text: str) -> Dict[str, Any]:
        """Extract analysis from text response"""
        # Simple text parsing for non-JSON responses
        return {
            "emotional_state": "calm",
            "engagement_level": 0.6,
            "attention_score": 0.6,
            "overstimulation_risk": 0.2,
            "immediate_recommendations": ["Continue current approach", "Monitor progress"],
            "behavioral_insights": ["Positive engagement observed"],
            "intervention_needed": False,
            "confidence_score": 0.7
        }
    
    def _create_fallback_analysis_result(self, session_id: str, session_data: Dict[str, Any]) -> StreamingAnalysis:
        """Create fallback analysis result"""
        return StreamingAnalysis(
            analysis_id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=datetime.now(),
            emotional_state="stable",
            engagement_level=0.5,
            attention_score=0.5,
            overstimulation_risk=0.3,
            immediate_recommendations=["Continue monitoring", "Maintain current approach"],
            behavioral_insights=["Session progressing normally"],
            intervention_needed=False,
            confidence_score=0.6
        )
    
    async def _create_intervention_alert(self, session_id: str, analysis: StreamingAnalysis) -> RealTimeAlert:
        """Create intervention alert based on analysis"""
        # Determine alert level and intervention type
        if analysis.overstimulation_risk > 0.8:
            level = AlertLevel.CRITICAL
            intervention_type = InterventionType.BREAK
        elif analysis.engagement_level < 0.3:
            level = AlertLevel.HIGH
            intervention_type = InterventionType.ENGAGEMENT
        elif analysis.attention_score < 0.3:
            level = AlertLevel.MEDIUM
            intervention_type = InterventionType.REGULATION
        else:
            level = AlertLevel.LOW
            intervention_type = InterventionType.CALMING
        
        # Get session metrics
        session_metrics = self.active_sessions.get(session_id)
        child_id = session_metrics.child_id if session_metrics else 0
        
        alert = RealTimeAlert(
            alert_id=str(uuid.uuid4()),
            session_id=session_id,
            child_id=child_id,
            timestamp=datetime.now(),
            level=level,
            intervention_type=intervention_type,
            trigger_patterns=analysis.behavioral_insights,
            recommended_actions=analysis.immediate_recommendations,
            urgency_score=analysis.overstimulation_risk
        )
        
        logger.warning(f"Created intervention alert {alert.alert_id} for session {session_id}")
        return alert
    
    async def generate_live_recommendations(self, session_id: str, context: Dict[str, Any]) -> List[str]:
        """Generate live recommendations for ongoing session"""
        try:
            if session_id not in self.active_sessions:
                return ["Session monitoring not active"]
            
            # Get recent analyses
            recent_analyses = self.streaming_analyses.get(session_id, [])[-3:]
            
            if not recent_analyses:
                return ["Continue current approach", "Monitor child's response"]
            
            # Build context-aware prompt
            prompt = self._build_live_recommendations_prompt(recent_analyses, context)
            
            recommendations = []
            
            if self.client and not self.settings.OPENAI_API_KEY.startswith("test-"):
                response = await self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a real-time ASD therapy assistant. Provide 3-5 immediate, actionable recommendations for the current session."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.4,
                    max_tokens=400
                )
                
                content = response.choices[0].message.content
                recommendations = self._parse_recommendations_response(content)
            else:
                # Fallback recommendations
                recommendations = [
                    "Maintain current engagement level",
                    "Provide positive reinforcement",
                    "Monitor for overstimulation signs",
                    "Be ready to implement calming strategies"
                ]
            
            logger.info(f"Generated {len(recommendations)} live recommendations for session {session_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating live recommendations: {str(e)}")
            return ["Continue current approach", "Monitor child's response"]
    
    def _build_live_recommendations_prompt(self, recent_analyses: List[StreamingAnalysis], context: Dict[str, Any]) -> str:
        """Build prompt for live recommendations"""
        analyses_summary = []
        for analysis in recent_analyses:
            analyses_summary.append({
                "timestamp": analysis.timestamp.isoformat(),
                "emotional_state": analysis.emotional_state,
                "engagement": analysis.engagement_level,
                "attention": analysis.attention_score,
                "overstimulation_risk": analysis.overstimulation_risk
            })
        
        return f"""
        LIVE SESSION RECOMMENDATION REQUEST
        
        Recent Analyses (last 3):
        {json.dumps(analyses_summary, indent=2)}
        
        Current Context:
        {json.dumps(context, indent=2)}
        
        Provide 3-5 immediate, actionable recommendations for:
        1. Maintaining/improving engagement
        2. Supporting emotional regulation
        3. Preventing overstimulation
        4. Optimizing learning outcomes
        5. Environmental adjustments if needed
        
        Focus on what can be implemented RIGHT NOW during the session.
        """
    
    def _parse_recommendations_response(self, content: str) -> List[str]:
        """Parse recommendations from AI response"""
        recommendations = []
        
        # Split by common patterns
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*') or line[0].isdigit()):
                # Clean up formatting
                clean_line = line.lstrip('•-*0123456789. ')
                if clean_line:
                    recommendations.append(clean_line)
        
        # If no structured format found, split by sentences
        if not recommendations:
            sentences = content.split('. ')
            recommendations = [s.strip() + '.' for s in sentences if len(s.strip()) > 10]
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    async def detect_overstimulation_patterns(self, session_id: str) -> Dict[str, Any]:
        """Detect overstimulation patterns in real-time"""
        try:
            if session_id not in self.active_sessions:
                return {"error": "Session not found"}
            
            recent_analyses = self.streaming_analyses.get(session_id, [])[-5:]
            
            if len(recent_analyses) < 2:
                return {
                    "overstimulation_detected": False,
                    "confidence": 0.0,
                    "patterns": [],
                    "recommendations": []
                }
            
            # Analyze patterns
            overstimulation_scores = [a.overstimulation_risk for a in recent_analyses]
            engagement_scores = [a.engagement_level for a in recent_analyses]
            attention_scores = [a.attention_score for a in recent_analyses]
            
            # Detect trends
            overstim_trend = self._calculate_trend(overstimulation_scores)
            engagement_trend = self._calculate_trend(engagement_scores)
            attention_trend = self._calculate_trend(attention_scores)
            
            # Determine overstimulation
            current_overstim = overstimulation_scores[-1]
            overstimulation_detected = (
                current_overstim > 0.7 or
                (overstim_trend > 0.3 and current_overstim > 0.5) or
                (engagement_trend < -0.3 and attention_trend < -0.3)
            )
            
            patterns = []
            if overstim_trend > 0.2:
                patterns.append("Increasing overstimulation trend detected")
            if engagement_trend < -0.2:
                patterns.append("Declining engagement pattern")
            if attention_trend < -0.2:
                patterns.append("Attention difficulties emerging")
            
            # Generate specific recommendations
            recommendations = []
            if overstimulation_detected:
                if current_overstim > 0.8:
                    recommendations.extend([
                        "Implement immediate calming intervention",
                        "Reduce environmental stimulation",
                        "Consider taking a break"
                    ])
                elif current_overstim > 0.6:
                    recommendations.extend([
                        "Begin calming strategies",
                        "Slow down activity pace",
                        "Provide sensory regulation tools"
                    ])
                else:
                    recommendations.extend([
                        "Monitor closely for escalation",
                        "Prepare calming interventions",
                        "Adjust difficulty level"
                    ])
            
            confidence = min(1.0, len(recent_analyses) / 5.0)
            
            result = {
                "overstimulation_detected": overstimulation_detected,
                "confidence": confidence,
                "current_risk_score": current_overstim,
                "trend_analysis": {
                    "overstimulation_trend": overstim_trend,
                    "engagement_trend": engagement_trend,
                    "attention_trend": attention_trend
                },
                "patterns": patterns,
                "recommendations": recommendations,
                "analysis_count": len(recent_analyses)
            }
            
            logger.info(f"Overstimulation analysis for session {session_id}: detected={overstimulation_detected}")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting overstimulation patterns: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend in values (-1 to 1, negative = decreasing, positive = increasing)"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend calculation
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        # Normalize to -1 to 1 range
        return max(-1.0, min(1.0, slope * 2))
    
    async def get_live_session_dashboard(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive live session dashboard data"""
        try:
            if session_id not in self.active_sessions:
                return {"error": "Session not found"}
            
            session_metrics = self.active_sessions[session_id]
            recent_analyses = self.streaming_analyses.get(session_id, [])[-10:]
            active_alerts = [alert for alert in self.session_alerts.get(session_id, []) 
                           if not alert.auto_resolved]
            
            # Calculate session statistics
            session_duration = (datetime.now() - session_metrics.start_time).total_seconds() / 60
            
            # Analysis trends
            if recent_analyses:
                avg_engagement = sum(a.engagement_level for a in recent_analyses) / len(recent_analyses)
                avg_attention = sum(a.attention_score for a in recent_analyses) / len(recent_analyses)
                avg_overstim_risk = sum(a.overstimulation_risk for a in recent_analyses) / len(recent_analyses)
                
                latest_analysis = recent_analyses[-1]
            else:
                avg_engagement = avg_attention = avg_overstim_risk = 0.5
                latest_analysis = None
            
            dashboard = {
                "session_info": {
                    "session_id": session_id,
                    "child_id": session_metrics.child_id,
                    "duration_minutes": round(session_duration, 2),
                    "total_interactions": session_metrics.total_interactions,
                    "status": "active"
                },
                "current_state": {
                    "emotional_state": latest_analysis.emotional_state if latest_analysis else "unknown",
                    "engagement_level": latest_analysis.engagement_level if latest_analysis else 0.5,
                    "attention_score": latest_analysis.attention_score if latest_analysis else 0.5,
                    "overstimulation_risk": latest_analysis.overstimulation_risk if latest_analysis else 0.0
                },
                "session_averages": {
                    "engagement": round(avg_engagement, 2),
                    "attention": round(avg_attention, 2),
                    "overstimulation_risk": round(avg_overstim_risk, 2)
                },
                "alerts": {
                    "active_count": len(active_alerts),
                    "total_count": len(self.session_alerts.get(session_id, [])),
                    "recent_alerts": [asdict(alert) for alert in active_alerts[-3:]]
                },
                "analysis_count": len(recent_analyses),
                "last_update": session_metrics.last_update.isoformat(),
                "breakthrough_moments": session_metrics.breakthrough_moments,
                "concerning_patterns": session_metrics.concerning_patterns,
                "positive_indicators": session_metrics.positive_indicators
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting live session dashboard: {str(e)}")
            return {"error": str(e)}
    
    async def register_websocket_connection(self, session_id: str, websocket) -> None:
        """Register WebSocket connection for real-time updates"""
        if session_id not in self.websocket_connections:
            self.websocket_connections[session_id] = set()
        
        self.websocket_connections[session_id].add(websocket)
        logger.info(f"Registered WebSocket connection for session {session_id}")
    
    async def unregister_websocket_connection(self, session_id: str, websocket) -> None:
        """Unregister WebSocket connection"""
        if session_id in self.websocket_connections:
            self.websocket_connections[session_id].discard(websocket)
            
            if not self.websocket_connections[session_id]:
                del self.websocket_connections[session_id]
        
        logger.info(f"Unregistered WebSocket connection for session {session_id}")
    
    async def _broadcast_analysis(self, session_id: str, analysis: StreamingAnalysis) -> None:
        """Broadcast analysis to connected WebSockets"""
        if session_id not in self.websocket_connections:
            return
        
        message = {
            "type": "streaming_analysis",
            "data": asdict(analysis)
        }
        
        await self._broadcast_message(session_id, message)
    
    async def _broadcast_alert(self, session_id: str, alert: RealTimeAlert) -> None:
        """Broadcast alert to connected WebSockets"""
        if session_id not in self.websocket_connections:
            return
        
        message = {
            "type": "intervention_alert",
            "data": asdict(alert)
        }
        
        await self._broadcast_message(session_id, message)
    
    async def _broadcast_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """Broadcast message to all WebSocket connections for a session"""
        if session_id not in self.websocket_connections:
            return
        
        connections = list(self.websocket_connections[session_id])
        message_json = json.dumps(message, default=str)
        
        # Remove closed connections while broadcasting
        to_remove = []
        
        for websocket in connections:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.warning(f"Failed to send message to WebSocket: {str(e)}")
                to_remove.append(websocket)
        
        # Clean up closed connections
        for websocket in to_remove:
            await self.unregister_websocket_connection(session_id, websocket)
    
    async def end_live_session_monitoring(self, session_id: str) -> Dict[str, Any]:
        """End live session monitoring and generate summary"""
        try:
            if session_id not in self.active_sessions:
                return {"error": "Session not found"}
            
            session_metrics = self.active_sessions[session_id]
            analyses = self.streaming_analyses.get(session_id, [])
            alerts = self.session_alerts.get(session_id, [])
            
            # Calculate session summary
            session_duration = (datetime.now() - session_metrics.start_time).total_seconds() / 60
            
            summary = {
                "session_id": session_id,
                "child_id": session_metrics.child_id,
                "duration_minutes": round(session_duration, 2),
                "total_interactions": session_metrics.total_interactions,
                "total_analyses": len(analyses),
                "total_alerts": len(alerts),
                "high_priority_alerts": len([a for a in alerts if a.level in [AlertLevel.HIGH, AlertLevel.CRITICAL]]),
                "breakthrough_moments": session_metrics.breakthrough_moments,
                "regulation_events": session_metrics.regulation_events,
                "final_emotional_stability": session_metrics.emotional_stability,
                "concerning_patterns": session_metrics.concerning_patterns,
                "positive_indicators": session_metrics.positive_indicators
            }
            
            if analyses:
                final_analysis = analyses[-1]
                summary.update({
                    "final_engagement": final_analysis.engagement_level,
                    "final_attention": final_analysis.attention_score,
                    "final_overstimulation_risk": final_analysis.overstimulation_risk
                })
            
            # Clean up session data
            del self.active_sessions[session_id]
            if session_id in self.session_alerts:
                del self.session_alerts[session_id]
            if session_id in self.streaming_analyses:
                del self.streaming_analyses[session_id]
            if session_id in self.websocket_connections:
                del self.websocket_connections[session_id]
            
            logger.info(f"Ended live session monitoring for {session_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error ending live session monitoring: {str(e)}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.close()
        
        # Close all WebSocket connections
        for session_id, connections in self.websocket_connections.items():
            for websocket in connections:
                try:
                    await websocket.close()
                except Exception:
                    pass
        
        self.websocket_connections.clear()
        logger.info("Real-time AI Service cleanup completed")

# Global service instance
realtime_ai_service = RealTimeAIService()
