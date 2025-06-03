// AI Insights Panel - Real-time AI insights display
// Clinical recommendation viewer, Progress prediction charts, Intervention suggestion interface

import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import {
    Brain,
    Activity,
    TrendingUp,
    AlertCircle,
    Eye,
    Heart,
    Target,
    CheckCircle,
    Clock,
    Lightbulb,
    BarChart3,
    RefreshCw
} from 'lucide-react';
import AIService from '../../services/aiService.js';
import ClinicalRecommendationViewer from './ClinicalRecommendationViewer.jsx';
import ProgressPredictionCharts from './ProgressPredictionCharts.jsx';
import InterventionSuggestionInterface from './InterventionSuggestionInterface.jsx';

const AIInsightsPanel = ({
    sessionId,
    childId,
    sessionData = {},
    isActive = false,
    onRecommendationSelect = () => { }
}) => {
    // State management
    const [realTimeInsights, setRealTimeInsights] = useState([]);
    const [emotionalPatterns, setEmotionalPatterns] = useState(null);
    const [behavioralPatterns, setBehavioralPatterns] = useState(null);
    const [recommendations, setRecommendations] = useState(null);
    const [progressAnalysis, setProgressAnalysis] = useState(null);
    const [aiServiceHealth, setAiServiceHealth] = useState({ status: 'unknown' });
    const [isLoading, setIsLoading] = useState(false);
    const [connectionStatus, setConnectionStatus] = useState('disconnected');
    const [activeTab, setActiveTab] = useState('realtime');
    const [error, setError] = useState(null);

    const insightsEndRef = useRef(null);
    const connectionRetryCount = useRef(0);
    const maxRetries = 3;

    // Initialize real-time connection when component mounts or sessionId changes
    useEffect(() => {
        if (sessionId && isActive) {
            initializeAIConnection();
            checkAIServiceHealth();
        }

        return () => {
            AIService.closeRealTimeConnection();
            setConnectionStatus('disconnected');
        };
    }, [sessionId, isActive]);

    // Auto-scroll to newest insights
    useEffect(() => {
        if (insightsEndRef.current) {
            insightsEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [realTimeInsights]);

    // Initialize AI connection with retry logic
    const initializeAIConnection = async () => {
        try {
            setConnectionStatus('connecting');
            setError(null);

            await AIService.initializeRealTimeConnection(
                sessionId,
                handleRealTimeInsight,
                handleConnectionError
            );

            setConnectionStatus('connected');
            connectionRetryCount.current = 0;

            // Start initial analysis
            await performInitialAnalysis();

        } catch (error) {
            console.error('Failed to initialize AI connection:', error);
            handleConnectionError(error);
        }
    };

    // Handle real-time insights from WebSocket
    const handleRealTimeInsight = (insight) => {
        const formattedInsight = {
            id: `insight_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            timestamp: insight.timestamp || new Date().toISOString(),
            type: insight.type,
            data: insight.data,
            confidence: insight.confidence || 0.8,
            urgency: determineUrgency(insight)
        };

        setRealTimeInsights(prev => [...prev, formattedInsight]);

        // Update specific analysis based on insight type
        switch (insight.type) {
            case 'emotion':
                updateEmotionalAnalysis(insight.data);
                break;
            case 'behavior':
                updateBehavioralAnalysis(insight.data);
                break;
            case 'recommendation':
                updateRecommendations(insight.data);
                break;
            case 'progress':
                updateProgressAnalysis(insight.data);
                break;
        }
    };

    // Handle connection errors with retry logic
    const handleConnectionError = (error) => {
        console.error('AI Connection Error:', error);
        setConnectionStatus('error');
        setError(error.message || 'Connection failed');

        if (connectionRetryCount.current < maxRetries) {
            connectionRetryCount.current++;
            setTimeout(() => {
                console.log(`Retrying connection (${connectionRetryCount.current}/${maxRetries})`);
                initializeAIConnection();
            }, 3000 * connectionRetryCount.current);
        }
    };

    // Perform initial comprehensive analysis
    const performInitialAnalysis = async () => {
        if (!sessionData || Object.keys(sessionData).length === 0) return;

        setIsLoading(true);

        try {            // Parallel execution of multiple analyses
            const [
                emotionalResult,
                behavioralResult,
                recommendationsResult
            ] = await Promise.allSettled([
                AIService.analyzeEmotionalPatterns(sessionData.emotions || {}),
                AIService.analyzeBehavioralPatterns(sessionData.behaviors || {}),
                AIService.generateRecommendations(sessionData, { child_id: childId })
            ]);

            // Process results
            if (emotionalResult.status === 'fulfilled' && emotionalResult.value.success) {
                setEmotionalPatterns(emotionalResult.value);
            }

            if (behavioralResult.status === 'fulfilled' && behavioralResult.value.success) {
                setBehavioralPatterns(behavioralResult.value);
            }

            if (recommendationsResult.status === 'fulfilled' && recommendationsResult.value.success) {
                setRecommendations(recommendationsResult.value);
            }

        } catch (error) {
            console.error('Initial analysis failed:', error);
            setError('Analysis failed: ' + error.message);
        } finally {
            setIsLoading(false);
        }
    };

    // Check AI service health
    const checkAIServiceHealth = async () => {
        try {
            const health = await AIService.checkHealth();
            setAiServiceHealth(health);
        } catch (error) {
            setAiServiceHealth({
                success: false,
                status: 'unhealthy',
                error: error.message
            });
        }
    };

    // Utility functions
    const determineUrgency = (insight) => {
        if (insight.type === 'emotion' && insight.data?.emotional_intensity > 0.8) {
            return 'high';
        }
        if (insight.type === 'behavior' && insight.data?.attention_level < 0.3) {
            return 'medium';
        }
        return 'low';
    };

    const updateEmotionalAnalysis = (emotionData) => {
        setEmotionalPatterns(prev => ({
            ...prev,
            latest: emotionData,
            lastUpdated: new Date().toISOString()
        }));
    };

    const updateBehavioralAnalysis = (behaviorData) => {
        setBehavioralPatterns(prev => ({
            ...prev,
            latest: behaviorData,
            lastUpdated: new Date().toISOString()
        }));
    };

    const updateRecommendations = (newRecommendations) => {
        setRecommendations(prev => ({
            ...prev,
            realTime: newRecommendations,
            lastUpdated: new Date().toISOString()
        }));
    };

    const updateProgressAnalysis = (progressData) => {
        setProgressAnalysis(prev => ({
            ...prev,
            latest: progressData,
            lastUpdated: new Date().toISOString()
        }));
    };

    const refreshAnalysis = async () => {
        await performInitialAnalysis();
    };

    const getConnectionStatusColor = () => {
        switch (connectionStatus) {
            case 'connected': return 'text-green-500';
            case 'connecting': return 'text-yellow-500';
            case 'error': return 'text-red-500';
            default: return 'text-gray-500';
        }
    };

    const getConnectionStatusIcon = () => {
        switch (connectionStatus) {
            case 'connected': return <CheckCircle className="w-4 h-4" />;
            case 'connecting': return <RefreshCw className="w-4 h-4 animate-spin" />;
            case 'error': return <AlertCircle className="w-4 h-4" />;
            default: return <Clock className="w-4 h-4" />;
        }
    };

    // Render functions
    const renderRealTimeInsights = () => (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                    <Activity className="w-5 h-5 text-blue-500" />
                    Real-time Insights
                </h3>
                <div className={`flex items-center gap-2 ${getConnectionStatusColor()}`}>
                    {getConnectionStatusIcon()}
                    <span className="text-sm capitalize">{connectionStatus}</span>
                </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                {realTimeInsights.length === 0 ? (
                    <div className="text-center text-gray-500 py-8">
                        <Brain className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p>Waiting for AI insights...</p>
                        <p className="text-sm">Start interacting to see real-time analysis</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {realTimeInsights.map((insight) => (
                            <div key={insight.id} className="bg-white rounded-lg p-3 border-l-4 border-blue-500">
                                <div className="flex items-start justify-between">
                                    <div className="flex items-start gap-3">
                                        {insight.type === 'emotion' && <Heart className="w-4 h-4 text-red-500 mt-1" />}
                                        {insight.type === 'behavior' && <Eye className="w-4 h-4 text-green-500 mt-1" />}
                                        {insight.type === 'recommendation' && <Lightbulb className="w-4 h-4 text-yellow-500 mt-1" />}
                                        {insight.type === 'progress' && <TrendingUp className="w-4 h-4 text-purple-500 mt-1" />}

                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="text-sm font-medium capitalize">{insight.type}</span>
                                                {insight.urgency === 'high' && (
                                                    <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">
                                                        High Priority
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-sm text-gray-700">{formatInsightData(insight)}</p>
                                        </div>
                                    </div>

                                    <div className="text-xs text-gray-500">
                                        {new Date(insight.timestamp).toLocaleTimeString()}
                                    </div>
                                </div>
                            </div>
                        ))}
                        <div ref={insightsEndRef} />
                    </div>
                )}
            </div>
        </div>
    );

    const formatInsightData = (insight) => {
        switch (insight.type) {
            case 'emotion':
                return `Emotional state: ${insight.data?.primary_emotion || 'Analyzing...'} (Confidence: ${Math.round((insight.confidence || 0) * 100)}%)`;
            case 'behavior':
                return `Behavioral pattern: ${insight.data?.pattern || 'Observing...'} - Engagement: ${Math.round((insight.data?.engagement_level || 0) * 100)}%`;
            case 'recommendation':
                return insight.data?.suggestion || 'New recommendation available';
            case 'progress':
                return `Progress update: ${insight.data?.milestone || 'Tracking progress...'}`;
            default:
                return JSON.stringify(insight.data);
        }
    };

    const renderAnalysisSummary = () => (
        <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-purple-500" />
                Session Analysis
            </h3>

            {isLoading ? (
                <div className="text-center py-8">
                    <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-3 text-blue-500" />
                    <p>Analyzing session data...</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Emotional Analysis Card */}
                    <div className="bg-gradient-to-br from-red-50 to-pink-50 rounded-lg p-4">
                        <h4 className="font-medium text-red-800 mb-3 flex items-center gap-2">
                            <Heart className="w-4 h-4" />
                            Emotional Patterns
                        </h4>
                        {emotionalPatterns ? (
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-sm">Stability Score:</span>
                                    <span className="text-sm font-medium">
                                        {Math.round((emotionalPatterns.stability || 0) * 100)}%
                                    </span>
                                </div>
                                <div className="text-xs text-gray-600">
                                    Dominant: {emotionalPatterns.patterns?.[0] || 'Neutral'}
                                </div>
                            </div>
                        ) : (
                            <p className="text-sm text-gray-600">No emotional data available</p>
                        )}
                    </div>

                    {/* Behavioral Analysis Card */}
                    <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-4">
                        <h4 className="font-medium text-green-800 mb-3 flex items-center gap-2">
                            <Eye className="w-4 h-4" />
                            Behavioral Insights
                        </h4>
                        {behavioralPatterns ? (
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-sm">Engagement:</span>
                                    <span className="text-sm font-medium">
                                        {Math.round((behavioralPatterns.engagement || 0) * 100)}%
                                    </span>
                                </div>
                                <div className="text-xs text-gray-600">
                                    Communication: {Math.round((behavioralPatterns.communication || 0) * 100)}%
                                </div>
                            </div>
                        ) : (
                            <p className="text-sm text-gray-600">No behavioral data available</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );

    const renderTabNavigation = () => (
        <div className="border-b border-gray-200 mb-4">
            <nav className="-mb-px flex space-x-8">
                {[
                    { id: 'realtime', label: 'Real-time', icon: Activity },
                    { id: 'clinical', label: 'Clinical', icon: Target },
                    { id: 'progress', label: 'Progress', icon: TrendingUp },
                    { id: 'interventions', label: 'Interventions', icon: Lightbulb }
                ].map(({ id, label, icon: Icon }) => (
                    <button
                        key={id}
                        onClick={() => setActiveTab(id)}
                        className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${activeTab === id
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        <Icon className="w-4 h-4" />
                        {label}
                    </button>
                ))}
            </nav>
        </div>
    );

    // Main render
    return (
        <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-3">
                    <Brain className="w-6 h-6 text-blue-500" />
                    AI Insights Panel
                </h2>

                <div className="flex items-center gap-3">
                    {/* AI Service Health Indicator */}
                    <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${aiServiceHealth.success ? 'bg-green-500' : 'bg-red-500'
                            }`} />
                        <span className="text-xs text-gray-600">
                            AI Service {aiServiceHealth.success ? 'Online' : 'Offline'}
                        </span>
                    </div>

                    {/* Refresh Button */}
                    <button
                        onClick={refreshAnalysis}
                        disabled={isLoading}
                        className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="Refresh Analysis"
                    >
                        <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>

            {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-red-500" />
                        <span className="text-sm text-red-700">{error}</span>
                    </div>
                </div>
            )}

            {renderTabNavigation()}

            <div className="space-y-6">
                {activeTab === 'realtime' && (
                    <>
                        {renderRealTimeInsights()}
                        {renderAnalysisSummary()}
                    </>
                )}

                {activeTab === 'clinical' && (
                    <ClinicalRecommendationViewer
                        recommendations={recommendations}
                        sessionData={sessionData}
                        childId={childId}
                        onRecommendationSelect={onRecommendationSelect}
                    />
                )}

                {activeTab === 'progress' && (
                    <ProgressPredictionCharts
                        sessionData={sessionData}
                        childId={childId}
                        progressAnalysis={progressAnalysis}
                    />
                )}        {activeTab === 'interventions' && (
                    <InterventionSuggestionInterface
                        sessionId={sessionId}
                        childProfile={sessionData}
                        onInterventionApplied={onRecommendationSelect}
                    />
                )}
            </div>
        </div>
    );
};

// PropTypes validation
AIInsightsPanel.propTypes = {
    sessionId: PropTypes.string.isRequired,
    childId: PropTypes.string.isRequired,
    sessionData: PropTypes.object,
    isActive: PropTypes.bool,
    onRecommendationSelect: PropTypes.func
};

AIInsightsPanel.defaultProps = {
    sessionData: {},
    isActive: false,
    onRecommendationSelect: () => { }
};

export default AIInsightsPanel;
