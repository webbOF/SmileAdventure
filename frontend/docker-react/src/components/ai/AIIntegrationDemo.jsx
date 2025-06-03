// AIIntegrationDemo.jsx
// Demo component that showcases AI integration features
// Uses AIService for real-time updates, notifications, and AI-powered features

import React, { useState, useEffect, useCallback } from 'react';
import { Container, Row, Col, Card, Button, Alert, Badge, Spinner } from 'react-bootstrap';
import AIService from '../../services/aiService.js';

/**
 * AIIntegrationDemo - Demonstrates comprehensive AI integration
 * Shows how to use the AIService for various AI-powered features
 */
const AIIntegrationDemo = () => {
    // State for session information
    const [sessionId, setSessionId] = useState(null);
    const [childId, setChildId] = useState(null);

    // State for AI integration features
    const [aiStatus, setAiStatus] = useState({ connected: false, loading: false });
    const [notifications, setNotifications] = useState([]);
    const [analysisResults, setAnalysisResults] = useState(null);
    const [recommendations, setRecommendations] = useState(null);

    // State for demo controls
    const [activeFeature, setActiveFeature] = useState('notifications');
    const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(false);

    /**
     * Create a new demo session
     */
    const createDemoSession = async () => {
        setAiStatus(prev => ({ ...prev, loading: true }));
        try {
            // In a real app, this would be a real session ID
            const newSessionId = `demo-${Date.now()}`;
            setSessionId(newSessionId);
            setChildId('demo-child-1');

            // Check AI service health
            const healthCheck = await AIService.checkHealth();
            setAiStatus({ connected: healthCheck.success, loading: false });

            // Add a welcome notification
            addNotification({
                type: 'system',
                title: 'Demo Session Created',
                message: `New AI session ${newSessionId} started`,
                timestamp: new Date().toISOString()
            });

        } catch (error) {
            console.error('Failed to create demo session:', error);
            setAiStatus({ connected: false, loading: false });

            addNotification({
                type: 'error',
                title: 'Session Creation Failed',
                message: error.message || 'Could not create demo session',
                timestamp: new Date().toISOString()
            });
        }
    };

    /**
     * Subscribe to AI service events
     */
    const subscribeToAiEvents = useCallback(() => {
        // Define handlers for different AI events
        const emotionHandler = (data) => {
            addNotification({
                type: 'emotion',
                title: 'Emotional Insight',
                message: `Detected ${data.dominantEmotion || 'emotion'} with ${Math.round((data.intensity || 0.5) * 100)}% confidence`,
                timestamp: data.timestamp || new Date().toISOString(),
                data
            });
        };

        const behaviorHandler = (data) => {
            addNotification({
                type: 'behavior',
                title: 'Behavioral Insight',
                message: `Engagement level: ${Math.round((data.engagement || 0.5) * 100)}%`,
                timestamp: data.timestamp || new Date().toISOString(),
                data
            });
        };

        const recommendationHandler = (data) => {
            addNotification({
                type: 'recommendation',
                title: 'New Recommendation',
                message: data.text || 'New recommendation available',
                timestamp: data.timestamp || new Date().toISOString(),
                data
            });

            // Also update recommendations state
            setRecommendations(prev => {
                if (!prev) return { items: [data] };
                return {
                    ...prev,
                    items: [data, ...prev.items.slice(0, 4)]
                };
            });
        };

        const criticalHandler = (data) => {
            addNotification({
                type: 'critical',
                title: 'Critical Alert',
                message: data.recommendation || 'Critical intervention needed',
                timestamp: data.timestamp || new Date().toISOString(),
                data
            });

            // Play sound alert for critical notifications
            try {
                const audio = new Audio('/assets/sounds/alert.mp3');
                audio.play().catch(e => console.log('Could not play audio alert'));
            } catch (e) {
                console.log('Audio playback not supported');
            }
        };

        // Subscribe to all event types
        AIService.subscribe('emotion_insight', emotionHandler);
        AIService.subscribe('behavior_insight', behaviorHandler);
        AIService.subscribe('recommendation', recommendationHandler);
        AIService.subscribe('critical_recommendation', criticalHandler);

        // Return unsubscribe function
        return () => {
            AIService.unsubscribe('emotion_insight', emotionHandler);
            AIService.unsubscribe('behavior_insight', behaviorHandler);
            AIService.unsubscribe('recommendation', recommendationHandler);
            AIService.unsubscribe('critical_recommendation', criticalHandler);
        };
    }, []);

    /**
     * Initialize real-time connection
     */
    const startRealTimeConnection = async () => {
        if (!sessionId) return;

        setIsRealTimeEnabled(true);

        try {
            // Define insight and error handlers
            const handleInsight = (insight) => {
                console.log('Real-time insight received:', insight);

                // Add as notification
                addNotification({
                    type: insight.type || 'insight',
                    title: `${insight.type} Insight`,
                    message: JSON.stringify(insight.data).substring(0, 50) + '...',
                    timestamp: insight.timestamp || new Date().toISOString(),
                    data: insight.data
                });

                // Update relevant state based on insight type
                if (insight.type === 'emotion' || insight.type === 'emotional_insight') {
                    AIService.notifySubscribers('emotion_insight', insight.data);
                }
                else if (insight.type === 'behavior' || insight.type === 'behavioral_insight') {
                    AIService.notifySubscribers('behavior_insight', insight.data);
                }
                else if (insight.type === 'recommendation') {
                    AIService.notifySubscribers('recommendation', insight.data);
                }
            };

            const handleError = (error) => {
                console.error('WebSocket error:', error);
                setIsRealTimeEnabled(false);
                addNotification({
                    type: 'error',
                    title: 'Connection Error',
                    message: error.message || 'WebSocket connection failed',
                    timestamp: new Date().toISOString()
                });
            };

            // Initialize WebSocket connection
            AIService.initializeRealTimeConnection(sessionId, handleInsight, handleError);

            // Start AI monitoring
            await AIService.startMonitoring(sessionId);

            addNotification({
                type: 'system',
                title: 'Real-time Connection',
                message: 'Connected to AI real-time service',
                timestamp: new Date().toISOString()
            });
        } catch (error) {
            console.error('Failed to initialize real-time connection:', error);
            setIsRealTimeEnabled(false);

            addNotification({
                type: 'error',
                title: 'Connection Failed',
                message: error.message || 'Could not connect to real-time AI service',
                timestamp: new Date().toISOString()
            });
        }
    };

    /**
     * Stop real-time connection
     */
    const stopRealTimeConnection = async () => {
        if (!sessionId) return;

        try {
            // Stop monitoring and close connection
            await AIService.stopMonitoring(sessionId);
            AIService.closeRealTimeConnection();
            setIsRealTimeEnabled(false);

            addNotification({
                type: 'system',
                title: 'Connection Closed',
                message: 'Disconnected from AI real-time service',
                timestamp: new Date().toISOString()
            });
        } catch (error) {
            console.error('Failed to stop real-time connection:', error);

            addNotification({
                type: 'error',
                title: 'Disconnect Failed',
                message: error.message || 'Could not disconnect properly',
                timestamp: new Date().toISOString()
            });
        }
    };

    /**
     * Run a comprehensive AI analysis on session data
     */
    const runAIAnalysis = async () => {
        if (!sessionId || !childId) return;

        setAiStatus(prev => ({ ...prev, loading: true }));

        try {
            // Create a sample session data object
            // In a real app, this would be actual session data
            const sampleSessionData = {
                session_id: sessionId,
                child_id: childId,
                duration: 1800, // 30 minutes
                activities: [
                    { name: 'Introduction', duration: 300, engagement: 0.7 },
                    { name: 'Main Exercise', duration: 1200, engagement: 0.85 },
                    { name: 'Conclusion', duration: 300, engagement: 0.6 }
                ],
                emotional_markers: {
                    joy: 0.6,
                    neutral: 0.3,
                    frustration: 0.1
                },
                behavioral_markers: {
                    attention: 0.75,
                    participation: 0.8,
                    communication: 0.65
                }
            };

            // Options for analysis
            const options = {
                analysisType: 'comprehensive',
                includeRecommendations: true,
                childContext: {
                    age: 7,
                    focus_areas: ['attention', 'social_skills'],
                    previous_progress: 'moderate'
                }
            };

            // Run comprehensive analysis
            const analysisResult = await AIService.analyzeSession(
                sampleSessionData,
                options
            );

            if (analysisResult.success) {
                setAnalysisResults(analysisResult.data);

                addNotification({
                    type: 'success',
                    title: 'Analysis Complete',
                    message: 'Comprehensive AI analysis completed successfully',
                    timestamp: new Date().toISOString()
                });

                // Get recommendations based on analysis
                const recommendationsResult = await AIService.generateRecommendations(
                    sampleSessionData,
                    options.childContext
                );

                if (recommendationsResult.success) {
                    setRecommendations(recommendationsResult);

                    // Notify subscribers of new recommendations
                    recommendationsResult.immediate?.forEach(rec => {
                        AIService.notifySubscribers('recommendation', {
                            type: 'immediate',
                            text: rec,
                            priority: 'high',
                            timestamp: new Date().toISOString()
                        });
                    });
                }

            } else {
                addNotification({
                    type: 'error',
                    title: 'Analysis Failed',
                    message: analysisResult.error || 'Could not complete analysis',
                    timestamp: new Date().toISOString()
                });
            }
        } catch (error) {
            console.error('AI analysis failed:', error);
            addNotification({
                type: 'error',
                title: 'Analysis Error',
                message: error.message || 'An error occurred during analysis',
                timestamp: new Date().toISOString()
            });
        } finally {
            setAiStatus(prev => ({ ...prev, loading: false }));
        }
    };

    /**
     * Trigger a test event to demonstrate notifications
     */
    const triggerTestEvent = async () => {
        // Simulate different types of events
        const eventTypes = ['emotion', 'behavior', 'recommendation', 'critical'];
        const randomType = eventTypes[Math.floor(Math.random() * eventTypes.length)];

        switch (randomType) {
            case 'emotion':
                // Simulate emotional insight
                AIService.notifySubscribers('emotion_insight', {
                    dominantEmotion: ['joy', 'neutral', 'surprise', 'interest'][Math.floor(Math.random() * 4)],
                    intensity: Math.random() * 0.5 + 0.5, // 0.5-1.0
                    stability: Math.random() * 0.7 + 0.3, // 0.3-1.0
                    timestamp: new Date().toISOString()
                });
                break;

            case 'behavior':
                // Simulate behavioral insight
                AIService.notifySubscribers('behavior_insight', {
                    engagement: Math.random() * 0.5 + 0.5, // 0.5-1.0
                    communication: Math.random() * 0.7 + 0.3, // 0.3-1.0
                    attention: {
                        overall: Math.random() * 0.8 + 0.2 // 0.2-1.0
                    },
                    patterns: [
                        'Sustained focus on interactive elements',
                        'Positive response to feedback'
                    ],
                    timestamp: new Date().toISOString()
                });
                break;

            case 'recommendation':
                // Simulate recommendation
                AIService.notifySubscribers('recommendation', {
                    type: 'immediate',
                    text: 'Introduce more visual elements to maintain engagement',
                    priority: 'medium',
                    timestamp: new Date().toISOString()
                });
                break;

            case 'critical':
                // Simulate critical recommendation
                AIService.notifySubscribers('critical_recommendation', {
                    recommendation: 'Take a short break - signs of frustration detected',
                    importance: 'high',
                    timestamp: new Date().toISOString()
                });
                break;
        }

        // Simulate processing real-time data 
        if (randomType === 'emotion') {
            AIService.processRealTimeEmotion({
                timestamp: new Date().toISOString(),
                emotion_detected: 'joy',
                confidence: 0.92,
                face_position: { x: 120, y: 80 }
            });
        } else if (randomType === 'behavior') {
            AIService.processRealTimeBehavior({
                timestamp: new Date().toISOString(),
                attention_level: 0.85,
                activity_level: 0.7,
                interaction_count: 3
            });
        }
    };

    /**
     * Helper function to add a notification
     */
    const addNotification = (notification) => {
        setNotifications(prev => [
            {
                id: Date.now(),
                ...notification
            },
            ...prev.slice(0, 9) // Keep last 10 notifications
        ]);
    };

    /**
     * Clear all notifications
     */
    const clearNotifications = () => {
        setNotifications([]);
    };

    /**
     * Handle implementation of a recommendation
     */
    const handleImplementRecommendation = (recommendation) => {
        // In a real app, this would perform some action
        AIService.notifySubscribers('recommendation_implemented', {
            recommendation,
            sessionId,
            timestamp: new Date().toISOString()
        });

        addNotification({
            type: 'success',
            title: 'Recommendation Applied',
            message: `Applied: ${recommendation.text || recommendation}`,
            timestamp: new Date().toISOString()
        });
    };

    // Set up event subscriptions
    useEffect(() => {
        // Only set up subscriptions if we have a session ID
        if (sessionId) {
            const unsubscribe = subscribeToAiEvents();
            return unsubscribe;
        }
    }, [sessionId, subscribeToAiEvents]);

    // Clean up when component unmounts
    useEffect(() => {
        return () => {
            if (isRealTimeEnabled && sessionId) {
                AIService.closeRealTimeConnection();
            }
        };
    }, [isRealTimeEnabled, sessionId]);

    /**
     * Render the notification panel
     */
    const renderNotificationPanel = () => {
        return (
            <Card className="mb-4">
                <Card.Header className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">AI Notifications</h5>
                    <div>
                        <Button
                            variant="outline-secondary"
                            size="sm"
                            onClick={clearNotifications}
                            disabled={notifications.length === 0}
                        >
                            Clear
                        </Button>
                    </div>
                </Card.Header>
                <Card.Body className="notification-container" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                    {notifications.length === 0 ? (
                        <Alert variant="light" className="text-center">
                            No notifications yet. Start the AI connection or run an analysis.
                        </Alert>
                    ) : (
                        notifications.map(notification => (
                            <Alert
                                key={notification.id}
                                variant={getAlertVariantForType(notification.type)}
                                className="mb-2"
                            >
                                <div className="d-flex justify-content-between align-items-start">
                                    <strong>{notification.title}</strong>
                                    <small>{new Date(notification.timestamp).toLocaleTimeString()}</small>
                                </div>
                                <p className="mb-0 mt-1">{notification.message}</p>
                            </Alert>
                        ))
                    )}
                </Card.Body>
            </Card>
        );
    };

    /**
     * Render the analysis results panel
     */
    const renderAnalysisPanel = () => {
        if (!analysisResults) {
            return (
                <Alert variant="info" className="text-center">
                    Run an analysis to see results here.
                </Alert>
            );
        }

        return (
            <Card className="mb-4">
                <Card.Header>
                    <h5 className="mb-0">Analysis Results</h5>
                </Card.Header>
                <Card.Body>
                    <pre className="analysis-json">
                        {JSON.stringify(analysisResults, null, 2)}
                    </pre>
                </Card.Body>
            </Card>
        );
    };

    /**
     * Render the recommendations panel
     */
    const renderRecommendationsPanel = () => {
        if (!recommendations || !recommendations.immediate || recommendations.immediate.length === 0) {
            return (
                <Alert variant="info" className="text-center">
                    No recommendations available. Run an analysis to generate recommendations.
                </Alert>
            );
        }

        return (
            <Card className="mb-4">
                <Card.Header>
                    <h5 className="mb-0">AI Recommendations</h5>
                </Card.Header>
                <Card.Body>
                    <h6>Immediate Interventions</h6>
                    {recommendations.immediate.map((rec, index) => (
                        <Alert
                            key={index}
                            variant="warning"
                            className="d-flex justify-content-between align-items-center"
                        >
                            <div>{rec}</div>
                            <Button
                                variant="outline-primary"
                                size="sm"
                                onClick={() => handleImplementRecommendation(rec)}
                            >
                                Implement
                            </Button>
                        </Alert>
                    ))}

                    {recommendations.sessionAdjustments && recommendations.sessionAdjustments.length > 0 && (
                        <>
                            <h6 className="mt-3">Session Adjustments</h6>
                            {recommendations.sessionAdjustments.map((rec, index) => (
                                <Alert key={index} variant="info">{rec}</Alert>
                            ))}
                        </>
                    )}

                    {recommendations.skillFocus && recommendations.skillFocus.length > 0 && (
                        <>
                            <h6 className="mt-3">Skill Development Focus</h6>
                            {recommendations.skillFocus.map((rec, index) => (
                                <Alert key={index} variant="light">{rec}</Alert>
                            ))}
                        </>
                    )}
                </Card.Body>
            </Card>
        );
    };

    /**
     * Helper function to determine alert variant
     */
    const getAlertVariantForType = (type) => {
        switch (type) {
            case 'error': return 'danger';
            case 'critical': return 'danger';
            case 'success': return 'success';
            case 'system': return 'secondary';
            case 'recommendation': return 'warning';
            case 'emotion': return 'info';
            case 'behavior': return 'light';
            default: return 'primary';
        }
    };

    return (
        <Container className="ai-integration-demo my-4">
            <Card className="mb-4">
                <Card.Header className="bg-primary text-white">
                    <h4 className="mb-0">AI Integration Demonstration</h4>
                </Card.Header>
                <Card.Body>
                    <Row>
                        <Col>
                            <p>
                                This demo showcases the integration between the frontend and AI services.
                                It demonstrates real-time AI insights, notifications, analyses, and recommendations.
                            </p>

                            <div className="mb-4 d-flex gap-2">
                                {!sessionId ? (
                                    <Button
                                        variant="primary"
                                        onClick={createDemoSession}
                                        disabled={aiStatus.loading}
                                    >
                                        {aiStatus.loading ? (
                                            <>
                                                <Spinner
                                                    as="span"
                                                    animation="border"
                                                    size="sm"
                                                    role="status"
                                                    aria-hidden="true"
                                                />
                                                <span className="ms-2">Creating...</span>
                                            </>
                                        ) : 'Create Demo Session'}
                                    </Button>
                                ) : (
                                    <>
                                        {isRealTimeEnabled ? (
                                            <Button
                                                variant="danger"
                                                onClick={stopRealTimeConnection}
                                            >
                                                Stop Real-time Connection
                                            </Button>
                                        ) : (
                                            <Button
                                                variant="success"
                                                onClick={startRealTimeConnection}
                                            >
                                                Start Real-time Connection
                                            </Button>
                                        )}

                                        <Button
                                            variant="primary"
                                            onClick={runAIAnalysis}
                                            disabled={aiStatus.loading}
                                        >
                                            {aiStatus.loading ? (
                                                <>
                                                    <Spinner as="span" animation="border" size="sm" />
                                                    <span className="ms-2">Analyzing...</span>
                                                </>
                                            ) : 'Run AI Analysis'}
                                        </Button>

                                        <Button
                                            variant="outline-secondary"
                                            onClick={triggerTestEvent}
                                        >
                                            Trigger Test Event
                                        </Button>
                                    </>
                                )}
                            </div>

                            <div className="d-flex align-items-center mb-3">
                                <div className="me-3">
                                    <strong>Status:</strong> {aiStatus.connected ? (
                                        <Badge bg="success">AI Service Connected</Badge>
                                    ) : (
                                        <Badge bg="danger">AI Service Disconnected</Badge>
                                    )}
                                </div>

                                {sessionId && (
                                    <div className="me-3">
                                        <strong>Session ID:</strong> <code>{sessionId}</code>
                                    </div>
                                )}

                                {isRealTimeEnabled && (
                                    <Badge bg="info">Real-time Active</Badge>
                                )}
                            </div>

                            <div className="mb-4">
                                <Button
                                    variant={activeFeature === 'notifications' ? 'primary' : 'outline-primary'}
                                    className="me-2"
                                    onClick={() => setActiveFeature('notifications')}
                                >
                                    Notifications
                                </Button>
                                <Button
                                    variant={activeFeature === 'analysis' ? 'primary' : 'outline-primary'}
                                    className="me-2"
                                    onClick={() => setActiveFeature('analysis')}
                                >
                                    Analysis Results
                                </Button>
                                <Button
                                    variant={activeFeature === 'recommendations' ? 'primary' : 'outline-primary'}
                                    onClick={() => setActiveFeature('recommendations')}
                                >
                                    Recommendations
                                </Button>
                            </div>
                        </Col>
                    </Row>

                    <Row>
                        <Col>
                            {activeFeature === 'notifications' && renderNotificationPanel()}
                            {activeFeature === 'analysis' && renderAnalysisPanel()}
                            {activeFeature === 'recommendations' && renderRecommendationsPanel()}
                        </Col>
                    </Row>
                </Card.Body>
            </Card>
        </Container>
    );
};

export default AIIntegrationDemo;
