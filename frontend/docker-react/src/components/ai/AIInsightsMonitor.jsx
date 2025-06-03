// AIInsightsMonitor.jsx
// Component to demonstrate real-time AI service notifications
import React, { useState, useEffect } from 'react';
import AIService from '../../services/aiService.js';
import { Card, Alert, Badge, ListGroup, Button } from 'react-bootstrap';

/**
 * AIInsightsMonitor - Demonstrates the use of AIService subscriptions
 * Shows how to integrate with the AIService notification mechanism
 * 
 * @param {Object} props
 * @param {String} props.sessionId - Current session ID
 * @param {Boolean} props.enabled - Whether the monitor is enabled
 */
const AIInsightsMonitor = ({ sessionId, enabled = true }) => {
    // State to track notifications from different channels
    const [notifications, setNotifications] = useState({
        emotional: [],
        behavioral: [],
        recommendations: [],
        critical: []
    });

    const [isSubscribed, setIsSubscribed] = useState(false);
    const [aiStatus, setAiStatus] = useState('unknown');

    // Handle emotional insight notifications
    const handleEmotionalInsight = (data) => {
        console.log('Emotional insight received:', data);
        setNotifications(prev => ({
            ...prev,
            emotional: [
                {
                    id: Date.now(),
                    type: 'emotional',
                    timestamp: new Date().toISOString(),
                    content: data
                },
                ...prev.emotional.slice(0, 4) // Keep last 5 notifications
            ]
        }));
    };

    // Handle behavioral insight notifications
    const handleBehavioralInsight = (data) => {
        console.log('Behavioral insight received:', data);
        setNotifications(prev => ({
            ...prev,
            behavioral: [
                {
                    id: Date.now(),
                    type: 'behavioral',
                    timestamp: new Date().toISOString(),
                    content: data
                },
                ...prev.behavioral.slice(0, 4) // Keep last 5 notifications
            ]
        }));
    };

    // Handle recommendation notifications
    const handleRecommendation = (data) => {
        console.log('Recommendation received:', data);
        setNotifications(prev => ({
            ...prev,
            recommendations: [
                {
                    id: Date.now(),
                    type: 'recommendation',
                    timestamp: new Date().toISOString(),
                    content: data
                },
                ...prev.recommendations.slice(0, 4) // Keep last 5 notifications
            ]
        }));
    };

    // Handle critical recommendation notifications
    const handleCriticalRecommendation = (data) => {
        console.log('CRITICAL recommendation received:', data);
        // Play a sound or show a more prominent notification for critical recommendations
        const audio = new Audio('/assets/sounds/notification.mp3');
        audio.play().catch(e => console.log('Audio play failed:', e));

        setNotifications(prev => ({
            ...prev,
            critical: [
                {
                    id: Date.now(),
                    type: 'critical',
                    timestamp: new Date().toISOString(),
                    content: data
                },
                ...prev.critical.slice(0, 4) // Keep last 5 notifications
            ]
        }));
    };

    // Subscribe to AI service notifications when component mounts
    useEffect(() => {
        if (enabled && sessionId && !isSubscribed) {
            // Subscribe to different event types
            AIService.subscribe('emotion_insight', handleEmotionalInsight);
            AIService.subscribe('behavior_insight', handleBehavioralInsight);
            AIService.subscribe('recommendation', handleRecommendation);
            AIService.subscribe('critical_recommendation', handleCriticalRecommendation);

            setIsSubscribed(true);

            // Check AI service health
            checkAIServiceHealth();
        }

        // Cleanup function to unsubscribe when component unmounts
        return () => {
            if (isSubscribed) {
                AIService.unsubscribe('emotion_insight', handleEmotionalInsight);
                AIService.unsubscribe('behavior_insight', handleBehavioralInsight);
                AIService.unsubscribe('recommendation', handleRecommendation);
                AIService.unsubscribe('critical_recommendation', handleCriticalRecommendation);

                setIsSubscribed(false);
            }
        };
    }, [enabled, sessionId]);

    // Check AI service health periodically
    const checkAIServiceHealth = async () => {
        try {
            const health = await AIService.checkHealth();
            setAiStatus(health.success ? 'connected' : 'disconnected');
        } catch (error) {
            console.error('Failed to check AI service health:', error);
            setAiStatus('error');
        }
    };

    // Trigger a test notification (for demonstration purposes)
    const triggerTestNotification = () => {
        // Use the notifySubscribers method to broadcast an event
        AIService.notifySubscribers('emotion_insight', {
            dominantEmotion: 'joy',
            intensity: 0.85,
            timestamp: new Date().toISOString(),
            isTest: true
        });

        setTimeout(() => {
            AIService.notifySubscribers('recommendation', {
                type: 'immediate',
                text: 'This is a test recommendation',
                priority: 'medium',
                isTest: true
            });
        }, 1000);
    };

    // Get appropriate status badge for AI service
    const getStatusBadge = () => {
        switch (aiStatus) {
            case 'connected':
                return <Badge bg="success">Online</Badge>;
            case 'disconnected':
                return <Badge bg="danger">Offline</Badge>;
            case 'error':
                return <Badge bg="warning">Error</Badge>;
            default:
                return <Badge bg="secondary">Unknown</Badge>;
        }
    };

    // Render notifications list
    const renderNotificationsList = (notificationList, title, variant) => {
        if (notificationList.length === 0) {
            return (
                <Alert variant="light" className="text-center">
                    No {title.toLowerCase()} notifications yet
                </Alert>
            );
        }

        return (
            <ListGroup variant="flush">
                {notificationList.map((notification) => (
                    <ListGroup.Item
                        key={notification.id}
                        variant={variant}
                        className="d-flex flex-column"
                    >
                        <div className="d-flex justify-content-between">
                            <strong>{title} #{notification.id}</strong>
                            <small>{new Date(notification.timestamp).toLocaleTimeString()}</small>
                        </div>
                        <div className="mt-2">
                            {JSON.stringify(notification.content)}
                        </div>
                    </ListGroup.Item>
                ))}
            </ListGroup>
        );
    };

    if (!enabled || !sessionId) {
        return (
            <Alert variant="warning">
                AI Insights Monitor is disabled or missing session ID.
            </Alert>
        );
    }

    return (
        <Card className="ai-insights-monitor">
            <Card.Header className="d-flex justify-content-between align-items-center">
                <div>
                    <h5 className="mb-0">AI Insights Monitor</h5>
                    <small className="text-muted">Session: {sessionId}</small>
                </div>
                <div>
                    AI Service: {getStatusBadge()}
                </div>
            </Card.Header>
            <Card.Body>
                {notifications.critical.length > 0 && (
                    <div className="mb-4">
                        <h6 className="text-danger">
                            Critical Recommendations ({notifications.critical.length})
                        </h6>
                        {renderNotificationsList(
                            notifications.critical,
                            'Critical',
                            'danger'
                        )}
                    </div>
                )}

                <div className="mb-3">
                    <h6>Latest Emotional Insights ({notifications.emotional.length})</h6>
                    {renderNotificationsList(
                        notifications.emotional,
                        'Emotional',
                        'info'
                    )}
                </div>

                <div className="mb-3">
                    <h6>Latest Behavioral Insights ({notifications.behavioral.length})</h6>
                    {renderNotificationsList(
                        notifications.behavioral,
                        'Behavioral',
                        'light'
                    )}
                </div>

                <div className="mb-3">
                    <h6>Latest Recommendations ({notifications.recommendations.length})</h6>
                    {renderNotificationsList(
                        notifications.recommendations,
                        'Recommendation',
                        'warning'
                    )}
                </div>

                <div className="text-center mt-4">
                    <Button
                        variant="outline-primary"
                        onClick={triggerTestNotification}
                    >
                        Trigger Test Notification
                    </Button>
                    <Button
                        variant="outline-info"
                        onClick={checkAIServiceHealth}
                        className="ms-2"
                    >
                        Check AI Service Health
                    </Button>
                </div>
            </Card.Body>
        </Card>
    );
};

export default AIInsightsMonitor;
