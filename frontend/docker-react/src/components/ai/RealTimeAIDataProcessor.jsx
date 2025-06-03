// RealTimeAIDataProcessor.jsx
// Real-time data processing component to analyze session data
// Demonstrates how to use AIService for real-time data processing

import React, { useState, useEffect, useRef } from 'react';
import { Card, Button, Alert, ProgressBar, Spinner, Badge } from 'react-bootstrap';
import AIService from '../../services/aiService.js';

/**
 * RealTimeAIDataProcessor - Processes real-time data using AIService
 * Shows how to send data to AI service for analysis in real-time
 */
const RealTimeAIDataProcessor = ({
    sessionId,
    isActive = false,
    sampleRate = 3000, // ms between samples
    onInsightGenerated = () => { }
}) => {
    // State for real-time processing
    const [isProcessing, setIsProcessing] = useState(false);
    const [processingStats, setProcessingStats] = useState({
        emotionSamples: 0,
        behaviorSamples: 0,
        lastProcessedAt: null
    });
    const [status, setStatus] = useState('idle');
    const [error, setError] = useState(null);

    // References to track intervals and status
    const processingInterval = useRef(null);
    const isComponentMounted = useRef(true);

    // Start real-time data processing
    const startProcessing = () => {
        if (!sessionId || isProcessing) return;

        setIsProcessing(true);
        setStatus('active');
        setError(null);

        // Set up interval to send data regularly
        processingInterval.current = setInterval(() => {
            if (isComponentMounted.current) {
                processEmotionalData();
                processBehavioralData();
            }
        }, sampleRate);
    };

    // Stop real-time data processing
    const stopProcessing = () => {
        if (processingInterval.current) {
            clearInterval(processingInterval.current);
            processingInterval.current = null;
        }

        setIsProcessing(false);
        setStatus('stopped');
    };

    // Generate and send emotional data to AI service
    const processEmotionalData = () => {
        try {
            // Generate simulated emotional data
            // In a real application, this would come from sensors, cameras, etc.
            const emotions = ['neutral', 'joy', 'interest', 'surprise', 'frustration'];
            const primaryEmotion = emotions[Math.floor(Math.random() * 3)]; // Bias toward first 3
            const secondaryEmotion = emotions[Math.floor(Math.random() * emotions.length)];

            const emotionData = {
                timestamp: new Date().toISOString(),
                primary_emotion: primaryEmotion,
                primary_confidence: 0.7 + (Math.random() * 0.3), // 0.7-1.0
                secondary_emotion: secondaryEmotion,
                secondary_confidence: 0.3 + (Math.random() * 0.4), // 0.3-0.7
                emotional_stability: 0.5 + (Math.random() * 0.5), // 0.5-1.0
                gaze_direction: {
                    x: Math.random() * 100,
                    y: Math.random() * 100
                },
                facial_expressions: {
                    smile_intensity: Math.random(),
                    brow_position: Math.random() - 0.5 // -0.5 to 0.5
                }
            };

            // Send data to AI service via WebSocket
            AIService.processRealTimeEmotion(emotionData);

            // Update processing stats
            setProcessingStats(prev => ({
                ...prev,
                emotionSamples: prev.emotionSamples + 1,
                lastProcessedAt: new Date().toISOString()
            }));

        } catch (error) {
            console.error('Error processing emotional data:', error);
            setError('Failed to process emotional data');
        }
    };

    // Generate and send behavioral data to AI service
    const processBehavioralData = () => {
        try {
            // Generate simulated behavioral data
            // In a real application, this would come from interaction tracking
            const behaviorData = {
                timestamp: new Date().toISOString(),
                attention_span: 0.6 + (Math.random() * 0.4), // 0.6-1.0
                activity_level: 0.4 + (Math.random() * 0.6), // 0.4-1.0
                interaction_patterns: {
                    response_time_ms: 500 + (Math.random() * 1500), // 500-2000ms
                    accuracy: 0.7 + (Math.random() * 0.3), // 0.7-1.0
                    completion_rate: 0.8 + (Math.random() * 0.2) // 0.8-1.0
                },
                engagement_metrics: {
                    time_on_task_seconds: Math.floor(Math.random() * 30) + 15, // 15-45 seconds
                    idle_periods: Math.floor(Math.random() * 3),
                    interaction_count: Math.floor(Math.random() * 5) + 1 // 1-5 interactions
                }
            };

            // Send data to AI service via WebSocket
            AIService.processRealTimeBehavior(behaviorData);

            // Update processing stats
            setProcessingStats(prev => ({
                ...prev,
                behaviorSamples: prev.behaviorSamples + 1,
                lastProcessedAt: new Date().toISOString()
            }));

        } catch (error) {
            console.error('Error processing behavioral data:', error);
            setError('Failed to process behavioral data');
        }
    };

    // Handle component activation/deactivation
    useEffect(() => {
        if (isActive && !isProcessing && sessionId) {
            startProcessing();
        } else if (!isActive && isProcessing) {
            stopProcessing();
        }

        // Cleanup function
        return () => {
            if (processingInterval.current) {
                clearInterval(processingInterval.current);
            }
        };
    }, [isActive, sessionId]);

    // Handle unmounting
    useEffect(() => {
        isComponentMounted.current = true;

        return () => {
            isComponentMounted.current = false;
            if (processingInterval.current) {
                clearInterval(processingInterval.current);
            }
        };
    }, []);

    // Get status badge
    const getStatusBadge = () => {
        switch (status) {
            case 'active':
                return <Badge bg="success">Processing</Badge>;
            case 'stopped':
                return <Badge bg="warning">Stopped</Badge>;
            case 'error':
                return <Badge bg="danger">Error</Badge>;
            default:
                return <Badge bg="secondary">Idle</Badge>;
        }
    };

    // Manual sample processing
    const processSingleSample = () => {
        processEmotionalData();
        processBehavioralData();
    };

    return (
        <Card className="real-time-processor mb-4">
            <Card.Header className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Real-Time AI Data Processor</h5>
                {getStatusBadge()}
            </Card.Header>

            <Card.Body>
                {!sessionId ? (
                    <Alert variant="warning">
                        Session ID required to start real-time processing
                    </Alert>
                ) : (
                    <>
                        <div className="mb-3">
                            <p>
                                <strong>Session ID:</strong> {sessionId}
                                <br />
                                <strong>Sample Rate:</strong> {sampleRate}ms
                            </p>

                            {isProcessing ? (
                                <div className="d-flex align-items-center mb-3">
                                    <Spinner animation="border" size="sm" className="me-2" />
                                    <span>Sending real-time data to AI service...</span>
                                </div>
                            ) : (
                                <p>Processor is currently idle</p>
                            )}
                        </div>

                        <div className="d-flex gap-2 mb-4">
                            {isProcessing ? (
                                <Button
                                    variant="danger"
                                    onClick={stopProcessing}
                                >
                                    Stop Processing
                                </Button>
                            ) : (
                                <Button
                                    variant="primary"
                                    onClick={startProcessing}
                                >
                                    Start Processing
                                </Button>
                            )}

                            <Button
                                variant="outline-secondary"
                                onClick={processSingleSample}
                                disabled={isProcessing}
                            >
                                Process Single Sample
                            </Button>
                        </div>

                        {error && (
                            <Alert variant="danger" className="mb-3">
                                {error}
                            </Alert>
                        )}

                        <Card className="mb-3">
                            <Card.Header>
                                <h6 className="mb-0">Processing Statistics</h6>
                            </Card.Header>
                            <Card.Body>
                                <div className="mb-3">
                                    <div className="d-flex justify-content-between mb-1">
                                        <span>Emotional Data Samples:</span>
                                        <strong>{processingStats.emotionSamples}</strong>
                                    </div>
                                    <ProgressBar
                                        now={Math.min(processingStats.emotionSamples, 10) * 10}
                                        variant="info"
                                        className="mb-3"
                                    />

                                    <div className="d-flex justify-content-between mb-1">
                                        <span>Behavioral Data Samples:</span>
                                        <strong>{processingStats.behaviorSamples}</strong>
                                    </div>
                                    <ProgressBar
                                        now={Math.min(processingStats.behaviorSamples, 10) * 10}
                                        variant="primary"
                                    />
                                </div>

                                {processingStats.lastProcessedAt && (
                                    <small className="text-muted">
                                        Last sample processed at: {
                                            new Date(processingStats.lastProcessedAt).toLocaleTimeString()
                                        }
                                    </small>
                                )}
                            </Card.Body>
                        </Card>

                        <Alert variant="info">
                            <strong>How it works:</strong> This component simulates collecting real-time emotional and behavioral
                            data from a child's session and sends it to the AI service for analysis via WebSockets.
                            In a real application, this data would come from cameras, sensors, or interaction tracking.
                        </Alert>
                    </>
                )}
            </Card.Body>
        </Card>
    );
};

export default RealTimeAIDataProcessor;
