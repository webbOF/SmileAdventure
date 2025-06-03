// aiService.js
// AI Service - Integration with LLM Service
// Handles real-time AI analysis, insights, and recommendations

import api from './api.js';

// API endpoints for AI functionality
const AI_ENDPOINTS = {
  ANALYZE_SESSION: '/realtime-ai/analyze-session',
  ANALYZE_EMOTIONAL_PATTERNS: '/realtime-ai/analyze-emotional-patterns', 
  ANALYZE_BEHAVIORAL_PATTERNS: '/realtime-ai/analyze-behavioral-patterns',
  GENERATE_RECOMMENDATIONS: '/realtime-ai/generate-recommendations',
  ANALYZE_PROGRESS: '/realtime-ai/analyze-progress',
  START_MONITORING: '/realtime-ai/start-monitoring',
  STOP_MONITORING: '/realtime-ai/stop-monitoring',
  HEALTH_CHECK: '/realtime-ai/health'
};

// WebSocket connection for real-time updates
let wsConnection = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_INTERVAL = 3000;

// Event listeners for real-time updates
const eventListeners = new Map();

/**
 * AI Service Class
 * Handles all AI-related API calls and real-time communication
 */
class AIService {
  
  /**
   * Initialize WebSocket connection for real-time AI insights
   * @param {string} sessionId - Current game session ID
   * @param {function} onInsight - Callback for real-time insights
   * @param {function} onError - Error callback
   */
  static initializeRealTimeConnection(sessionId, onInsight, onError) {
    try {
      const token = localStorage.getItem('authToken');
      const wsUrl = `ws://localhost:8008/api/v1/ws/insights/${sessionId}?token=${token}`;
      
      wsConnection = new WebSocket(wsUrl);
      
      wsConnection.onopen = () => {
        console.log('🔗 AI WebSocket connection established');
        reconnectAttempts = 0;
        
        // Send initial monitoring request
        this.sendWebSocketMessage({
          type: 'start_monitoring',
          session_id: sessionId,
          timestamp: new Date().toISOString()
        });
      };
      
      wsConnection.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📊 Real-time AI insight received:', data);
          
          // Process different types of AI insights
          switch (data.type) {
            case 'emotional_insight':
              onInsight({
                type: 'emotion',
                data: data.analysis,
                timestamp: data.timestamp
              });
              break;
              
            case 'behavioral_insight':
              onInsight({
                type: 'behavior',
                data: data.analysis,
                timestamp: data.timestamp
              });
              break;
              
            case 'recommendation':
              onInsight({
                type: 'recommendation',
                data: data.recommendations,
                timestamp: data.timestamp
              });
              break;
              
            case 'progress_update':
              onInsight({
                type: 'progress',
                data: data.progress,
                timestamp: data.timestamp
              });
              break;
              
            default:
              console.log('Unknown insight type:', data.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
          onError && onError(error);
        }
      };
      
      wsConnection.onclose = (event) => {
        console.log('🔌 AI WebSocket connection closed:', event.code);
        this.handleReconnection(sessionId, onInsight, onError);
      };
      
      wsConnection.onerror = (error) => {
        console.error('❌ AI WebSocket error:', error);
        onError && onError(error);
      };
      
    } catch (error) {
      console.error('Failed to initialize WebSocket connection:', error);
      onError && onError(error);
    }
  }
  
  /**
   * Handle WebSocket reconnection with exponential backoff
   */
  static handleReconnection(sessionId, onInsight, onError) {
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      const delay = RECONNECT_INTERVAL * Math.pow(2, reconnectAttempts - 1);
      
      console.log(`🔄 Attempting WebSocket reconnection (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}) in ${delay}ms`);
      
      setTimeout(() => {
        this.initializeRealTimeConnection(sessionId, onInsight, onError);
      }, delay);
    } else {
      console.error('❌ Max reconnection attempts reached');
      onError && onError(new Error('WebSocket connection failed after maximum retry attempts'));
    }
  }
  
  /**
   * Send message through WebSocket connection
   * @param {Object} message - Message to send
   */
  static sendWebSocketMessage(message) {
    if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
      wsConnection.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not open. Message not sent:', message);
    }
  }
  
  /**
   * Close WebSocket connection
   */
  static closeRealTimeConnection() {
    if (wsConnection) {
      wsConnection.close();
      wsConnection = null;
      console.log('🔌 AI WebSocket connection closed');
    }
  }
  
  /**
   * Analyze game session data for comprehensive insights
   * @param {Object} sessionData - Game session data
   * @param {Object} options - Analysis options
   * @returns {Promise<Object>} Analysis results
   */
  static async analyzeSession(sessionData, options = {}) {
    try {
      const response = await api.post(AI_ENDPOINTS.ANALYZE_SESSION, {
        session_data: sessionData,
        analysis_type: options.analysisType || 'comprehensive',
        include_recommendations: options.includeRecommendations !== false,
        child_context: options.childContext || null
      });
      
      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Session analysis failed:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message,
        fallback: this.generateFallbackAnalysis(sessionData)
      };
    }
  }
  
  /**
   * Analyze emotional patterns in real-time
   * @param {Object} emotionalData - Emotional data from session
   * @returns {Promise<Object>} Emotional analysis
   */
  static async analyzeEmotionalPatterns(emotionalData) {
    try {
      const response = await api.post(AI_ENDPOINTS.ANALYZE_EMOTIONAL_PATTERNS, emotionalData);
      
      return {
        success: true,
        patterns: response.data.dominant_emotions || [],
        stability: response.data.emotional_stability_score || 0.5,
        transitions: response.data.emotional_transitions || [],
        triggers: response.data.triggers_identified || [],
        strategies: response.data.calming_strategies_effective || [],
        insights: response.data.emotional_pattern_insights || []
      };
    } catch (error) {
      console.error('Emotional analysis failed:', error);
      return {
        success: false,
        error: error.message,
        fallback: {
          patterns: ['neutral'],
          stability: 0.5,
          insights: ['Emotional analysis temporarily unavailable']
        }
      };
    }
  }
  
  /**
   * Analyze behavioral patterns
   * @param {Object} behavioralData - Behavioral data from session
   * @returns {Promise<Object>} Behavioral analysis
   */
  static async analyzeBehavioralPatterns(behavioralData) {
    try {
      const response = await api.post(AI_ENDPOINTS.ANALYZE_BEHAVIORAL_PATTERNS, behavioralData);
      
      return {
        success: true,
        engagement: response.data.social_engagement_level || 0.5,
        communication: response.data.communication_effectiveness || 0.5,
        patterns: response.data.behavioral_patterns_observed || [],
        attention: response.data.attention_patterns || {},
        insights: response.data.behavioral_insights || []
      };
    } catch (error) {
      console.error('Behavioral analysis failed:', error);
      return {
        success: false,
        error: error.message,
        fallback: {
          engagement: 0.5,
          communication: 0.5,
          insights: ['Behavioral analysis temporarily unavailable']
        }
      };
    }
  }
  
  /**
   * Generate AI-powered recommendations
   * @param {Object} sessionData - Session data for context
   * @param {Object} context - Additional context (child profile, history, etc.)
   * @returns {Promise<Object>} Recommendations
   */
  static async generateRecommendations(sessionData, context = {}) {
    try {
      const response = await api.post(AI_ENDPOINTS.GENERATE_RECOMMENDATIONS, {
        session_data: sessionData,
        context: context
      });
      
      return {
        success: true,
        immediate: response.data.immediate_interventions || [],
        sessionAdjustments: response.data.session_adjustments || [],
        environmental: response.data.environmental_modifications || [],
        skillFocus: response.data.skill_development_focus || [],
        parentGuidance: response.data.parent_guidance || [],
        clinical: response.data.clinical_considerations || [],
        nextSession: response.data.next_session_preparation || [],
        longTerm: response.data.long_term_goals || []
      };
    } catch (error) {
      console.error('Recommendation generation failed:', error);
      return {
        success: false,
        error: error.message,
        fallback: {
          immediate: ['Continue current approach'],
          clinical: ['Regular progress monitoring recommended']
        }
      };
    }
  }
  
  /**
   * Analyze progress across multiple sessions
   * @param {Array} sessionHistory - Array of session data
   * @param {number|string} childId - Child ID
   * @param {number} timeframeDays - Analysis timeframe
   * @returns {Promise<Object>} Progress analysis
   */
  static async analyzeProgress(sessionHistory, childId, timeframeDays = 30) {
    try {
      const response = await api.post(AI_ENDPOINTS.ANALYZE_PROGRESS, {
        session_history: sessionHistory,
        child_id: childId,
        analysis_timeframe_days: timeframeDays
      });
      
      return {
        success: true,
        trend: response.data.overall_progress_trend || 'stable',
        skills: response.data.skill_development_trends || {},
        milestones: response.data.milestone_achievements || [],
        improvements: response.data.areas_of_improvement || [],
        attention: response.data.areas_needing_attention || [],
        insights: response.data.progress_insights || [],
        comparison: response.data.comparative_analysis || {}
      };
    } catch (error) {
      console.error('Progress analysis failed:', error);
      return {
        success: false,
        error: error.message,
        fallback: {
          trend: 'stable',
          insights: ['Progress analysis temporarily unavailable']
        }
      };
    }
  }
  
  /**
   * Start real-time monitoring for a session
   * @param {string} sessionId - Session ID to monitor
   * @returns {Promise<Object>} Monitoring status
   */
  static async startMonitoring(sessionId) {
    try {
      const response = await api.post(`${AI_ENDPOINTS.START_MONITORING}/${sessionId}`);
      return {
        success: true,
        monitoringId: response.data.monitoring_id,
        status: response.data.status
      };
    } catch (error) {
      console.error('Failed to start monitoring:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * Stop real-time monitoring for a session
   * @param {string} sessionId - Session ID to stop monitoring
   * @returns {Promise<Object>} Monitoring status
   */
  static async stopMonitoring(sessionId) {
    try {
      const response = await api.post(`${AI_ENDPOINTS.STOP_MONITORING}/${sessionId}`);
      return {
        success: true,
        status: response.data.status
      };
    } catch (error) {
      console.error('Failed to stop monitoring:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * Check AI service health
   * @returns {Promise<Object>} Health status
   */
  static async checkHealth() {
    try {
      const response = await api.get(AI_ENDPOINTS.HEALTH_CHECK);
      return {
        success: true,
        status: response.data.status,
        openaiConnected: response.data.openai_status === 'connected'
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * Generate fallback analysis when AI service is unavailable
   * @param {Object} sessionData - Session data
   * @returns {Object} Fallback analysis
   */
  static generateFallbackAnalysis(sessionData) {
    return {
      insights: {
        overall_engagement: 0.5,
        emotional_stability: 0.5,
        learning_progress: 0.5,
        key_observations: ['Session completed successfully'],
        fallback: true
      },
      recommendations: {
        immediate: ['Continue current approach'],
        clinical: ['AI analysis temporarily unavailable - manual review recommended']
      }
    };
  }
  
  /**
   * Process real-time emotion data
   * @param {Object} emotionData - Real-time emotion data
   */
  static processRealTimeEmotion(emotionData) {
    // Send emotion data through WebSocket for real-time analysis
    this.sendWebSocketMessage({
      type: 'emotion_update',
      data: emotionData,
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Process real-time behavioral data
   * @param {Object} behaviorData - Real-time behavioral data
   */
  static processRealTimeBehavior(behaviorData) {
    // Send behavioral data through WebSocket for real-time analysis
    this.sendWebSocketMessage({
      type: 'behavior_update',
      data: behaviorData,
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Subscribe to specific AI insight types
   * @param {string} eventType - Type of insight to subscribe to
   * @param {function} callback - Callback function
   */
  static subscribe(eventType, callback) {
    if (!eventListeners.has(eventType)) {
      eventListeners.set(eventType, []);
    }
    eventListeners.get(eventType).push(callback);
  }
  
  /**
   * Unsubscribe from AI insight notifications
   * @param {string} eventType - Type of insight to unsubscribe from
   * @param {function} callback - Callback function to remove
   */
  static unsubscribe(eventType, callback) {
    if (eventListeners.has(eventType)) {
      const callbacks = eventListeners.get(eventType);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * Notify all subscribers of an event
   * @param {string} eventType - Type of event to notify about
   * @param {object} data - Event data
   */
  static notifySubscribers(eventType, data) {
    if (eventListeners.has(eventType)) {
      const callbacks = eventListeners.get(eventType);
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in ${eventType} event callback:`, error);
        }
      });
    }
  }
  
  /**
   * Get insight history from a session
   * @param {string} sessionId - Session ID to get insights for
   * @param {string} insightType - Type of insights to retrieve
   * @returns {Promise<Object>} Insight history
   */
  static async getSessionInsightHistory(sessionId, insightType = 'all') {
    try {
      const endpoint = `/realtime-ai/insights-history/${sessionId}?type=${insightType}`;
      const response = await api.get(endpoint);
      return {
        success: true,
        insights: response.data.insights ?? [],
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Failed to get insight history:', error);
      return {
        success: false,
        error: error.message,
        insights: []
      };
    }
  }

  /**
   * Connect to AI WebSocket service with session parameters
   * @param {Object} params - Connection parameters
   * @param {string} params.session_id - Session ID
   * @param {string|number} params.child_id - Child ID
   * @returns {Promise<Object>} Connection status
   */
  static async connectWebSocket(params) {
    try {
      // Store current session info
      const sessionId = params.session_id;
      
      // Setup listeners for insights and errors
      const onInsight = (insight) => {
        // Broadcast insights to relevant subscribers based on type
        if (insight.type === 'emotion') {
          this.notifySubscribers('emotion_insight', insight.data);
        } else if (insight.type === 'behavior') {
          this.notifySubscribers('behavior_insight', insight.data);
        } else if (insight.type === 'recommendation') {
          this.notifySubscribers('recommendation', insight.data);
        } else if (insight.type === 'progress') {
          this.notifySubscribers('progress_update', insight.data);
        }
        
        // Also notify generic insight subscribers
        this.notifySubscribers('any_insight', insight);
      };
      
      const onError = (error) => {
        this.notifySubscribers('connection_error', {
          message: error.message || 'WebSocket connection error',
          timestamp: new Date().toISOString()
        });
      };
      
      // Initialize real-time connection
      this.initializeRealTimeConnection(sessionId, onInsight, onError);
      
      // Start monitoring for this session
      await this.startMonitoring(sessionId);
      
      return {
        success: true,
        connected: true,
        sessionId: sessionId,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      return {
        success: false,
        connected: false,
        error: error.message
      };
    }
  }
  
  /**
   * Disconnect from AI WebSocket service
   * @returns {Promise<Object>} Disconnection status
   */
  static async disconnectWebSocket() {
    try {
      this.closeRealTimeConnection();
      
      return {
        success: true,
        connected: false,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Failed to disconnect WebSocket:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
}

export default AIService;
