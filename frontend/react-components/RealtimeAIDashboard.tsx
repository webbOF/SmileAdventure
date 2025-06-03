/**
 * Real-time AI Dashboard Component
 * React component for displaying live AI analysis and interventions
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { AlertTriangle, Brain, Activity, TrendingUp } from 'lucide-react';

interface StreamingAnalysis {
    analysis_id: string;
    session_id: string;
    timestamp: string;
    emotional_state: string;
    engagement_level: number;
    attention_score: number;
    overstimulation_risk: number;
    immediate_recommendations: string[];
    behavioral_insights: string[];
    intervention_needed: boolean;
    confidence_score: number;
}

interface RealTimeAlert {
    alert_id: string;
    session_id: string;
    timestamp: string;
    level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    intervention_type: string;
    message: string;
    auto_resolved: boolean;
}

interface RealtimeAIDashboardProps {
    sessionId: string;
    apiBaseUrl: string;
    authToken: string;
}

const RealtimeAIDashboard: React.FC<RealtimeAIDashboardProps> = ({
    sessionId,
    apiBaseUrl,
    authToken
}) => {
    // State management
    const [isConnected, setIsConnected] = useState(false);
    const [latestAnalysis, setLatestAnalysis] = useState<StreamingAnalysis | null>(null);
    const [alerts, setAlerts] = useState<RealTimeAlert[]>([]);
    const [dashboardData, setDashboardData] = useState<any>(null);
    const [recommendations, setRecommendations] = useState<string[]>([]);
    const [connectionError, setConnectionError] = useState<string | null>(null);

    // WebSocket connection
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const [reconnectAttempts, setReconnectAttempts] = useState(0);

    // Connect to WebSocket
    const connectWebSocket = useCallback(() => {
        try {
            const wsUrl = `ws://${apiBaseUrl.replace('http://', '').replace('https://', '')}/realtime-ai/stream/${sessionId}`;
            const ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log('WebSocket connected for real-time AI');
                setIsConnected(true);
                setConnectionError(null);
                setReconnectAttempts(0);

                // Send initial heartbeat
                ws.send(JSON.stringify({
                    type: 'heartbeat',
                    timestamp: new Date().toISOString()
                }));
            };

            ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    handleWebSocketMessage(message);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            ws.onclose = () => {
                console.log('WebSocket disconnected');
                setIsConnected(false);

                // Attempt to reconnect with exponential backoff
                if (reconnectAttempts < 5) {
                    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
                    reconnectTimeoutRef.current = setTimeout(() => {
                        setReconnectAttempts(prev => prev + 1);
                        connectWebSocket();
                    }, delay);
                } else {
                    setConnectionError('Failed to maintain WebSocket connection');
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                setConnectionError('WebSocket connection error');
            };

            wsRef.current = ws;

        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            setConnectionError('Failed to create WebSocket connection');
        }
    }, [sessionId, apiBaseUrl, reconnectAttempts]);

    // Handle WebSocket messages
    const handleWebSocketMessage = (message: any) => {
        switch (message.type) {
            case 'streaming_analysis':
                setLatestAnalysis(message.data);
                break;

            case 'intervention_alert':
                setAlerts(prev => [message.data, ...prev.slice(0, 9)]); // Keep last 10 alerts
                break;

            case 'dashboard_update':
                setDashboardData(message.data);
                break;

            case 'heartbeat_response':
            case 'gateway_heartbeat':
                // Connection is alive
                break;

            case 'error':
                console.error('WebSocket error message:', message.message);
                setConnectionError(message.message);
                break;

            default:
                console.log('Unknown message type:', message.type);
        }
    };

    // Fetch dashboard data
    const fetchDashboardData = async () => {
        try {
            const response = await fetch(`${apiBaseUrl}/realtime-ai/dashboard/${sessionId}`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setDashboardData(data.dashboard);
            }
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
        }
    };

    // Fetch recommendations
    const fetchRecommendations = async () => {
        try {
            const response = await fetch(`${apiBaseUrl}/realtime-ai/recommendations/${sessionId}`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setRecommendations(data.recommendations);
            }
        } catch (error) {
            console.error('Failed to fetch recommendations:', error);
        }
    };

    // Initialize component
    useEffect(() => {
        connectWebSocket();
        fetchDashboardData();
        fetchRecommendations();

        // Set up periodic data refresh
        const refreshInterval = setInterval(() => {
            fetchDashboardData();
            fetchRecommendations();
        }, 30000); // Refresh every 30 seconds

        return () => {
            clearInterval(refreshInterval);
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connectWebSocket]);

    // Send heartbeat periodically
    useEffect(() => {
        if (isConnected && wsRef.current) {
            const heartbeatInterval = setInterval(() => {
                if (wsRef.current?.readyState === WebSocket.OPEN) {
                    wsRef.current.send(JSON.stringify({
                        type: 'heartbeat',
                        timestamp: new Date().toISOString()
                    }));
                }
            }, 30000);

            return () => clearInterval(heartbeatInterval);
        }
    }, [isConnected]);

    // Helper functions
    const getEngagementColor = (level: number) => {
        if (level >= 0.8) return 'text-green-600';
        if (level >= 0.6) return 'text-yellow-600';
        return 'text-red-600';
    };

    const getAlertColor = (level: string) => {
        switch (level) {
            case 'CRITICAL': return 'bg-red-100 border-red-500 text-red-700';
            case 'HIGH': return 'bg-orange-100 border-orange-500 text-orange-700';
            case 'MEDIUM': return 'bg-yellow-100 border-yellow-500 text-yellow-700';
            case 'LOW': return 'bg-blue-100 border-blue-500 text-blue-700';
            default: return 'bg-gray-100 border-gray-500 text-gray-700';
        }
    };

    return (
        <div className="p-6 bg-white rounded-lg shadow-lg">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <Brain className="w-8 h-8 text-blue-600" />
                    <h2 className="text-2xl font-bold text-gray-800">Real-time AI Dashboard</h2>
                </div>

                {/* Connection status */}
                <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className={`text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                        {isConnected ? 'Connected' : 'Disconnected'}
                    </span>
                </div>
            </div>

            {/* Connection Error */}
            {connectionError && (
                <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                    <div className="flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" />
                        <span>{connectionError}</span>
                    </div>
                </div>
            )}

            {/* Latest Analysis */}
            {latestAnalysis && (
                <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <h3 className="text-lg font-semibold mb-3 text-blue-800">Latest AI Analysis</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-gray-800">{latestAnalysis.emotional_state}</div>
                            <div className="text-sm text-gray-600">Emotional State</div>
                        </div>
                        <div className="text-center">
                            <div className={`text-2xl font-bold ${getEngagementColor(latestAnalysis.engagement_level)}`}>
                                {Math.round(latestAnalysis.engagement_level * 100)}%
                            </div>
                            <div className="text-sm text-gray-600">Engagement</div>
                        </div>
                        <div className="text-center">
                            <div className={`text-2xl font-bold ${getEngagementColor(latestAnalysis.attention_score)}`}>
                                {Math.round(latestAnalysis.attention_score * 100)}%
                            </div>
                            <div className="text-sm text-gray-600">Attention</div>
                        </div>
                        <div className="text-center">
                            <div className={`text-2xl font-bold ${latestAnalysis.overstimulation_risk > 0.7 ? 'text-red-600' : latestAnalysis.overstimulation_risk > 0.4 ? 'text-yellow-600' : 'text-green-600'}`}>
                                {Math.round(latestAnalysis.overstimulation_risk * 100)}%
                            </div>
                            <div className="text-sm text-gray-600">Overstim Risk</div>
                        </div>
                    </div>

                    {latestAnalysis.intervention_needed && (
                        <div className="mt-3 p-2 bg-red-100 border border-red-400 text-red-700 rounded">
                            <strong>Intervention Needed:</strong> Immediate attention required
                        </div>
                    )}
                </div>
            )}

            <div className="grid md:grid-cols-2 gap-6">
                {/* Active Alerts */}
                <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-orange-500" />
                        Active Alerts
                    </h3>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                        {alerts.length === 0 ? (
                            <p className="text-gray-500 text-sm">No active alerts</p>
                        ) : (
                            alerts.map((alert) => (
                                <div
                                    key={alert.alert_id}
                                    className={`p-3 rounded border-l-4 ${getAlertColor(alert.level)}`}
                                >
                                    <div className="flex items-center justify-between">
                                        <span className="font-medium">{alert.level}</span>
                                        <span className="text-xs">
                                            {new Date(alert.timestamp).toLocaleTimeString()}
                                        </span>
                                    </div>
                                    <p className="text-sm mt-1">{alert.message}</p>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Recommendations */}
                <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-green-500" />
                        Live Recommendations
                    </h3>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                        {recommendations.length === 0 ? (
                            <p className="text-gray-500 text-sm">No recommendations available</p>
                        ) : (
                            recommendations.map((recommendation, index) => (
                                <div key={index} className="p-3 bg-white rounded border border-gray-200">
                                    <p className="text-sm">{recommendation}</p>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>

            {/* Session Info */}
            {dashboardData && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-blue-500" />
                        Session Overview
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        {dashboardData.session_info && (
                            <>
                                <div>
                                    <div className="font-medium text-gray-700">Duration</div>
                                    <div className="text-gray-600">{dashboardData.session_info.duration_minutes} min</div>
                                </div>
                                <div>
                                    <div className="font-medium text-gray-700">Interactions</div>
                                    <div className="text-gray-600">{dashboardData.session_info.total_interactions}</div>
                                </div>
                                <div>
                                    <div className="font-medium text-gray-700">Status</div>
                                    <div className="text-gray-600">{dashboardData.session_info.status}</div>
                                </div>
                                <div>
                                    <div className="font-medium text-gray-700">Child ID</div>
                                    <div className="text-gray-600">{dashboardData.session_info.child_id}</div>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default RealtimeAIDashboard;
