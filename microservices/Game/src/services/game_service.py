import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..models.game_models import (EmotionType, EndGameRequest, GameAction,
                                  GameActionData, GameResponse,
                                  GameSessionData, GameState, StartGameRequest)


class GameService:
    """Service for handling game logic and state management"""
    
    def __init__(self):
        # In-memory storage for demo purposes
        # In production, this would use a database
        self.active_sessions: Dict[str, GameState] = {}
        self.session_history: Dict[str, GameSessionData] = {}
        self.scenarios = {
            "basic_adventure": {
                "name": "Basic Adventure",
                "description": "A simple adventure to get started",
                "objectives": ["find_treasure", "help_friend", "solve_puzzle"],
                "max_score": 100
            },
            "emotion_garden": {
                "name": "Emotion Garden",
                "description": "Learn about emotions while gardening",
                "objectives": ["plant_seeds", "water_plants", "identify_emotions"],
                "max_score": 150
            },
            "friendship_quest": {
                "name": "Friendship Quest",
                "description": "Build friendships and social skills",
                "objectives": ["make_friend", "resolve_conflict", "share_feelings"],
                "max_score": 120
            }
        }
    
    async def start_game_session(self, request: StartGameRequest) -> GameResponse:
        """Start a new game session"""
        try:
            session_id = str(uuid.uuid4())
            scenario = self.scenarios.get(request.scenario_id, self.scenarios["basic_adventure"])
            
            # Create initial game state
            game_state = GameState(
                session_id=session_id,
                user_id=request.user_id,
                current_scenario=request.scenario_id,
                current_level=request.difficulty_level,
                score=0,
                health=100,
                position={"x": 0, "y": 0},
                inventory=[],
                completed_objectives=[],
                current_objective=scenario["objectives"][0] if scenario["objectives"] else None,
                emotions_state={emotion: 50 for emotion in EmotionType},
                last_updated=datetime.now()
            )
            
            # Create session data
            session_data = GameSessionData(
                user_id=request.user_id,
                session_id=session_id,
                child_id=request.child_id,
                scenario_id=request.scenario_id,
                difficulty_level=request.difficulty_level,
                start_time=datetime.now(),
                emotions_detected=[],
                interactions=[],
                progress_data={"scenario": scenario}
            )
            
            # Store in memory
            self.active_sessions[session_id] = game_state
            self.session_history[session_id] = session_data
            
            return GameResponse(
                success=True,
                message="Game session started successfully",
                session_id=session_id,
                data={
                    "scenario": scenario,
                    "initial_state": game_state.dict(),
                    "objectives": scenario["objectives"]
                }
            )
            
        except Exception as e:
            return GameResponse(
                success=False,
                message=f"Failed to start game session: {str(e)}"
            )
    
    async def get_game_state(self, session_id: str, user_id: int) -> GameResponse:
        """Get current game state"""
        try:
            if session_id not in self.active_sessions:
                return GameResponse(
                    success=False,
                    message="Game session not found"
                )
            
            game_state = self.active_sessions[session_id]
            
            # Verify user owns this session
            if game_state.user_id != user_id:
                return GameResponse(
                    success=False,
                    message="Unauthorized access to game session"
                )
            
            return GameResponse(
                success=True,
                message="Game state retrieved successfully",
                session_id=session_id,
                data=game_state.dict()
            )
            
        except Exception as e:
            return GameResponse(
                success=False,
                message=f"Failed to get game state: {str(e)}"
            )
    
    async def process_game_action(self, action_data: GameActionData) -> GameResponse:
        """Process a game action and update state"""
        try:
            session_id = action_data.session_id
            
            if session_id not in self.active_sessions:
                return GameResponse(
                    success=False,
                    message="Game session not found"
                )
            
            game_state = self.active_sessions[session_id]
            session_data = self.session_history[session_id]
            
            # Verify user owns this session
            if game_state.user_id != action_data.user_id:
                return GameResponse(
                    success=False,
                    message="Unauthorized access to game session"
                )
            
            # Process the action based on type
            result = await self._process_action_by_type(game_state, action_data)
            
            # Update session data with the interaction
            session_data.interactions.append({
                "action": action_data.action_type,
                "target": action_data.target,
                "timestamp": action_data.timestamp.isoformat(),
                "result": result
            })
            
            # Update emotions if detected
            if action_data.emotion_detected:
                if action_data.emotion_detected not in session_data.emotions_detected:
                    session_data.emotions_detected.append(action_data.emotion_detected)
                
                # Update emotion state
                current_level = game_state.emotions_state.get(action_data.emotion_detected, 50)
                game_state.emotions_state[action_data.emotion_detected] = min(100, current_level + 10)
            
            # Update last updated time
            game_state.last_updated = datetime.now()
            
            return GameResponse(
                success=True,
                message="Action processed successfully",
                session_id=session_id,
                data={
                    "action_result": result,
                    "updated_state": {
                        "score": game_state.score,
                        "health": game_state.health,
                        "position": game_state.position,
                        "current_objective": game_state.current_objective,
                        "completed_objectives": game_state.completed_objectives
                    }
                }
            )
            
        except Exception as e:
            return GameResponse(
                success=False,
                message=f"Failed to process action: {str(e)}"
            )
    
    async def _process_action_by_type(self, game_state: GameState, action: GameActionData) -> Dict[str, Any]:
        """Process action based on its type"""
        result = {"success": False, "message": "Unknown action"}
        
        if action.action_type == GameAction.MOVE:
            if action.position:
                game_state.position.update(action.position)
                result = {"success": True, "message": "Moved successfully", "new_position": game_state.position}
        
        elif action.action_type == GameAction.INTERACT:
            if action.target:
                result = await self._handle_interaction(game_state, action.target)
        
        elif action.action_type == GameAction.SELECT:
            if action.target:
                game_state.inventory.append(action.target)
                game_state.score += 5
                result = {"success": True, "message": f"Selected {action.target}", "score_gained": 5}
        
        elif action.action_type == GameAction.ANSWER:
            if action.response:
                result = await self._handle_answer(game_state, action.response)
        
        elif action.action_type == GameAction.COMPLETE:
            if game_state.current_objective:
                result = await self._complete_objective(game_state)
        
        return result
    
    async def _handle_interaction(self, game_state: GameState, target: str) -> Dict[str, Any]:
        """Handle interaction with game objects"""
        scenario = self.scenarios.get(game_state.current_scenario, {})
        
        # Simple interaction logic
        if target == "friend":
            game_state.score += 15
            game_state.emotions_state[EmotionType.HAPPY] = min(100, game_state.emotions_state.get(EmotionType.HAPPY, 50) + 20)
            return {"success": True, "message": "Made a friend!", "score_gained": 15}
        
        elif target == "treasure":
            game_state.score += 25
            game_state.inventory.append("treasure")
            return {"success": True, "message": "Found treasure!", "score_gained": 25}
        
        elif target == "puzzle":
            game_state.score += 10
            return {"success": True, "message": "Solved puzzle!", "score_gained": 10}
        
        else:
            return {"success": True, "message": f"Interacted with {target}"}
    
    async def _handle_answer(self, game_state: GameState, response: str) -> Dict[str, Any]:
        """Handle answer responses"""
        # Simple answer evaluation
        if response.lower() in ["happy", "excited", "proud"]:
            game_state.score += 20
            emotion = EmotionType.HAPPY if response.lower() == "happy" else EmotionType.EXCITED
            game_state.emotions_state[emotion] = min(100, game_state.emotions_state.get(emotion, 50) + 15)
            return {"success": True, "message": "Great answer!", "score_gained": 20}
        else:
            game_state.score += 5
            return {"success": True, "message": "Good try!", "score_gained": 5}
    
    async def _complete_objective(self, game_state: GameState) -> Dict[str, Any]:
        """Complete current objective and move to next"""
        scenario = self.scenarios.get(game_state.current_scenario, {})
        
        if game_state.current_objective:
            game_state.completed_objectives.append(game_state.current_objective)
            game_state.score += 30
            
            # Move to next objective
            remaining_objectives = [obj for obj in scenario.get("objectives", []) 
                                 if obj not in game_state.completed_objectives]
            
            if remaining_objectives:
                game_state.current_objective = remaining_objectives[0]
                message = f"Objective completed! Next: {game_state.current_objective}"
            else:
                game_state.current_objective = None
                message = "All objectives completed! Great job!"
            
            return {"success": True, "message": message, "score_gained": 30}
        
        return {"success": False, "message": "No active objective to complete"}
    
    async def end_game_session(self, request: EndGameRequest) -> GameResponse:
        """End a game session"""
        try:
            session_id = request.session_id
            
            if session_id not in self.active_sessions:
                return GameResponse(
                    success=False,
                    message="Game session not found"
                )
            
            game_state = self.active_sessions[session_id]
            session_data = self.session_history[session_id]
            
            # Verify user owns this session
            if game_state.user_id != request.user_id:
                return GameResponse(
                    success=False,
                    message="Unauthorized access to game session"
                )
            
            # Update session data
            session_data.end_time = datetime.now()
            session_data.duration_seconds = int((session_data.end_time - session_data.start_time).total_seconds())
            session_data.completed = True
            session_data.score = request.final_score or game_state.score
            
            # Calculate completion percentage
            scenario = self.scenarios.get(game_state.current_scenario, {})
            total_objectives = len(scenario.get("objectives", []))
            completed_objectives = len(game_state.completed_objectives)
            completion_percentage = (completed_objectives / total_objectives * 100) if total_objectives > 0 else 100
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            return GameResponse(
                success=True,
                message="Game session ended successfully",
                session_id=session_id,
                data={
                    "final_score": session_data.score,
                    "duration_seconds": session_data.duration_seconds,
                    "completion_percentage": completion_percentage,
                    "objectives_completed": completed_objectives,
                    "total_objectives": total_objectives,
                    "emotions_detected": session_data.emotions_detected,
                    "total_interactions": len(session_data.interactions)
                }
            )
            
        except Exception as e:
            return GameResponse(
                success=False,
                message=f"Failed to end game session: {str(e)}"
            )
    
    async def get_available_scenarios(self) -> Dict[str, Any]:
        """Get list of available game scenarios"""
        return {
            "scenarios": self.scenarios,
            "total_count": len(self.scenarios)
        }

# Global game service instance
game_service = GameService()