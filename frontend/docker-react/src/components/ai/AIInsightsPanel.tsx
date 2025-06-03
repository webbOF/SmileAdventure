// AI Insights Panel - Real-time AI insights display
// Clinical recommendation viewer, Progress prediction charts, Intervention suggestion interface

import React, { useState, useEffect, useRef } from 'react';
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
import AIService from '../../services/aiService';
import ClinicalRecommendationViewer from './ClinicalRecommendationViewer';
import ProgressPredictionCharts from './ProgressPredictionCharts';
import InterventionSuggestionInterface from './InterventionSuggestionInterface';

const AIInsightsPanel = ({
    sessionId,
    childId,
    sessionData,
    isActive = false,
    onRecommendationSelect
}) => {
    // State management
    const [insights, setInsights] = useState({
        emotional: null,
        behavioral: null,
        recommendations: null,
        progress: null
    });

    const [realTimeData, setRealTimeData] = useState([]);
    const [connectionStatus, setConnectionStatus] = useState('disconnected');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [selectedTab, setSelectedTab] = useState('overview');
    const [error, setError] = useState(null);

    const wsInitialized = useRef(false);
    const analysisCache = useRef(new Map());

    // Initialize real-time AI connection
    useEffect(() => {
        if (isActive && sessionId && !wsInitialized.current) {
            initializeAIConnection();
            wsInitialized.current = true;
        }

        return () => {
            if (wsInitialized.current) {
                AIService.closeRealTimeConnection();
                wsInitialized.current = false;
            }
        };
    }, [isActive, sessionId]);

    // Perform initial analysis when session data changes
    useEffect(() => {
        if (sessionData && Object.keys(sessionData).length > 0) {
            performComprehensiveAnalysis();
        }
    }, [sessionData]);

    /**
     * Initialize AI connection and set up real-time handlers
     */
    const initializeAIConnection = async () => {
        try {
            setConnectionStatus('connecting');

            // Initialize WebSocket connection
            AIService.initializeRealTimeConnection(
                sessionId,
                handleRealTimeInsight,
                handleConnectionError
            );

            // Start monitoring
            const monitoringResult = await AIService.startMonitoring(sessionId);
            if (monitoringResult.success) {
                setConnectionStatus('connected');
            } else {
                throw new Error(monitoringResult.error);
            }

        } catch (error) {
            console.error('Failed to initialize AI connection:', error);
            setConnectionStatus('error');
            setError(error.message);
        }
    };

    /**
     * Handle real-time insights from WebSocket
     */
    const handleRealTimeInsight = (insight) => {
        const timestamp = new Date();

        setRealTimeData(prev => [
            ...prev.slice(-19), // Keep last 20 insights
            { ...insight, timestamp }
        ]);

        // Update insights based on type
        switch (insight.type) {
            case 'emotion':
                setInsights(prev => ({
                    ...prev,
                    emotional: { ...insight.data, timestamp }
                }));
                break;

            case 'behavior':
                setInsights(prev => ({
                    ...prev,
                    behavioral: { ...insight.data, timestamp }
                }));
                break;

            case 'recommendation':
                setInsights(prev => ({
                    ...prev,
                    recommendations: { ...insight.data, timestamp }
                }));
                break;

            case 'progress':
                setInsights(prev => ({
                    ...prev,
                    progress: { ...insight.data, timestamp }
                }));
                break;
        }
    };

    /**
     * Handle connection errors
     */
    const handleConnectionError = (error) => {
        console.error('AI connection error:', error);
        setConnectionStatus('error');
        setError(error.message);
    };

    /**
     * Perform comprehensive analysis of session data
     */
    const performComprehensiveAnalysis = async () => {
        if (!sessionData || isAnalyzing) return;

        setIsAnalyzing(true);
        setError(null);

        try {
            // Check cache first
            const cacheKey = `${sessionId}_${JSON.stringify(sessionData).length}`;
            if (analysisCache.current.has(cacheKey)) {
                setInsights(analysisCache.current.get(cacheKey));
                setIsAnalyzing(false);
                return;
            }

            // Perform parallel analysis
            const [
                sessionAnalysis,
                emotionalAnalysis,
                behavioralAnalysis,
                recommendations,
                progressAnalysis
            ] = await Promise.allSettled([
                AIService.analyzeSession(sessionData, { childContext: { id: childId } }),
                AIService.analyzeEmotionalPatterns(sessionData.emotionalData || {}),
                AIService.analyzeBehavioralPatterns(sessionData.behavioralData || {}),
                AIService.generateRecommendations(sessionData, { childId }),
                childId ? AIService.analyzeProgress([sessionData], childId) : Promise.resolve({ success: false })
            ]);

            const newInsights = {
                session: sessionAnalysis.status === 'fulfilled' ? sessionAnalysis.value : null,
                emotional: emotionalAnalysis.status === 'fulfilled' ? emotionalAnalysis.value : null,
                behavioral: behavioralAnalysis.status === 'fulfilled' ? behavioralAnalysis.value : null,
                recommendations: recommendations.status === 'fulfilled' ? recommendations.value : null,
                progress: progressAnalysis.status === 'fulfilled' ? progressAnalysis.value : null
            };

            setInsights(newInsights);

            // Cache the results
            analysisCache.current.set(cacheKey, newInsights);

        } catch (error) {
            console.error('Comprehensive analysis failed:', error);
            setError('Failed to analyze session data');
        } finally {
            setIsAnalyzing(false);
        }
    };

    /**
     * Refresh analysis
     */
    const refreshAnalysis = () => {
        analysisCache.current.clear();
        performComprehensiveAnalysis();
    };

    /**
     * Get connection status indicator
     */
    const getConnectionIndicator = () => {
        const statusConfig = {
            connected: { color: 'text-green-500', icon: '●', label: 'Connected' },
            connecting: { color: 'text-yellow-500', icon: '●', label: 'Connecting...' },
            disconnected: { color: 'text-gray-500', icon: '●', label: 'Disconnected' },
            error: { color: 'text-red-500', icon: '●', label: 'Connection Error' }
        };

        const status = statusConfig[connectionStatus] || statusConfig.disconnected;

        return (
            <div className={`flex items-center space-x-2 ${status.color}`}>
                <span className="text-lg">{status.icon}</span>
                <span className="text-sm font-medium">{status.label}</span>
            </div>
        );
    };

    /**
     * Render overview tab content
     */
    const renderOverview = () => (
        <div className="space-y-6">
            {/* Real-time Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Emotional State Card */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center space-x-3">
                        <Heart className="h-6 w-6 text-blue-600" />
                        <div>
                            <h3 className="font-semibold text-blue-900">Emotional State</h3>
                            {insights.emotional?.success ? (
                                <div className="space-y-1">
                                    <p className="text-sm text-blue-700">
                                        Stability: {(insights.emotional.stability * 100).toFixed(0)}%
                                    </p>
                                    <p className="text-xs text-blue-600">
                                        Patterns: {insights.emotional.patterns.slice(0, 2).join(', ')}
                                    </p>
                                </div>
                            ) : (
                                <p className="text-sm text-blue-600">Analyzing...</p>
                            )}
                        </div>
                    </div>
                </div>

                {/* Behavioral Engagement Card */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center space-x-3">
                        <Activity className="h-6 w-6 text-green-600" />
                        <div>
                            <h3 className="font-semibold text-green-900">Engagement</h3>
                            {insights.behavioral?.success ? (
                                <div className="space-y-1">
                                    <p className="text-sm text-green-700">
                                        Level: {(insights.behavioral.engagement * 100).toFixed(0)}%
                                    </p>
                                    <p className="text-xs text-green-600">
                                        Communication: {(insights.behavioral.communication * 100).toFixed(0)}%
                                    </p>
                                </div>
                            ) : (
                                <p className="text-sm text-green-600">Analyzing...</p>
                            )}
                        </div>
                    </div>
                </div>

                {/* Progress Trend Card */}
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <div className="flex items-center space-x-3">
                        <TrendingUp className="h-6 w-6 text-purple-600" />
                        <div>
                            <h3 className="font-semibold text-purple-900">Progress</h3>
                            {insights.progress?.success ? (
                                <div className="space-y-1">
                                    <p className="text-sm text-purple-700">
                                        Trend: {insights.progress.trend}
                                    </p>
                                    <p className="text-xs text-purple-600">
                                        Milestones: {insights.progress.milestones.length}
                                    </p>
                                </div>
                            ) : (
                                <p className="text-sm text-purple-600">Analyzing...</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Real-time Insights Stream */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <Eye className="h-5 w-5 mr-2" />
                    Real-time Insights
                </h3>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                    {realTimeData.length > 0 ? (
                        realTimeData.slice(-5).map((insight, index) => (
                            <div key={index} className="flex items-start space-x-3 p-2 bg-white rounded border">
                                <span className="text-xs text-gray-500 mt-1">
                                    {insight.timestamp.toLocaleTimeString()}
                                </span>
                                <div className="flex-1">
                                    <span className="text-sm font-medium capitalize">{insight.type}:</span>
                                    <span className="text-sm text-gray-700 ml-2">
                                        {JSON.stringify(insight.data).substring(0, 100)}...
                                    </span>
                                </div>
                            </div>
                        ))
                    ) : (
                        <p className="text-sm text-gray-500 italic">No real-time insights yet...</p>
                    )}
                </div>
            </div>
        </div>
    );

    return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                    <Brain className="h-6 w-6 text-indigo-600" />
                    <h2 className="text-lg font-semibold text-gray-900">AI Insights</h2>
                    {getConnectionIndicator()}
                </div>

                <div className="flex items-center space-x-2">
                    {isAnalyzing && (
                        <RefreshCw className="h-4 w-4 text-gray-400 animate-spin" />
                    )}
                    <button
                        onClick={refreshAnalysis}
                        className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                        disabled={isAnalyzing}
                    >
                        <RefreshCw className="h-4 w-4" />
                    </button>
                </div>
            </div>

            {/* Error Display */}
            {error && (
                <div className="p-4 bg-red-50 border-b border-red-200">
                    <div className="flex items-center space-x-2">
                        <AlertCircle className="h-5 w-5 text-red-500" />
                        <p className="text-sm text-red-700">{error}</p>
                    </div>
                </div>
            )}

            {/* Navigation Tabs */}
            <div className="border-b border-gray-200">
                <nav className="flex space-x-8 px-4">
                    {[
                        { id: 'overview', label: 'Overview', icon: BarChart3 },
                        { id: 'clinical', label: 'Clinical', icon: Target },
                        { id: 'progress', label: 'Progress', icon: TrendingUp },
                        { id: 'interventions', label: 'Interventions', icon: Lightbulb }
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setSelectedTab(tab.id)}
                            className={`flex items-center space-x-2 py-3 px-1 border-b-2 font-medium text-sm transition-colors ${selectedTab === tab.id
                                    ? 'border-indigo-500 text-indigo-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            <tab.icon className="h-4 w-4" />
                            <span>{tab.label}</span>
                        </button>
                    ))}
                </nav>
            </div>

            {/* Content */}
            <div className="p-4">
                {selectedTab === 'overview' && renderOverview()}

                {selectedTab === 'clinical' && (
                    <ClinicalRecommendationViewer
                        recommendations={insights.recommendations}
                        onRecommendationSelect={onRecommendationSelect}
                    />
                )}

                {selectedTab === 'progress' && (
                    <ProgressPredictionCharts
                        progressData={insights.progress}
                        emotionalData={insights.emotional}
                        behavioralData={insights.behavioral}
                    />
                )}

                {selectedTab === 'interventions' && (
                    <InterventionSuggestionInterface
                        sessionData={sessionData}
                        recommendations={insights.recommendations}
                        onInterventionApply={onRecommendationSelect}
                    />
                )}
            </div>
        </div>
    );
};

export default AIInsightsPanel;
