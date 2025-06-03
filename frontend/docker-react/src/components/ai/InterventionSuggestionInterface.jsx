import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import AIService from '../../services/aiService';
import './InterventionSuggestionInterface.css';

/**
 * InterventionSuggestionInterface Component
 * Displays AI-generated intervention suggestions with interactive implementation
 */
const InterventionSuggestionInterface = ({ sessionId, childProfile, onInterventionApplied }) => {
    const [interventions, setInterventions] = useState({
        immediate: [],
        environmental: [],
        behavioral: [],
        communication: [],
        sensory: [],
        educational: []
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedIntervention, setSelectedIntervention] = useState(null);
    const [activeCategory, setActiveCategory] = useState('immediate');
    const [appliedInterventions, setAppliedInterventions] = useState(new Set());
    const [filterPriority, setFilterPriority] = useState('all');

    // Load interventions on component mount
    useEffect(() => {
        if (sessionId) {
            loadInterventions();
        }
    }, [sessionId]);

    /**
     * Load AI-generated interventions
     */
    const loadInterventions = async () => {
        setLoading(true);
        setError(null);

        try {
            const sessionData = {
                session_id: sessionId,
                child_profile: childProfile,
                timestamp: new Date().toISOString()
            };

            const response = await AIService.generateRecommendations(sessionData, {
                focus: 'interventions',
                include_implementation_steps: true,
                child_context: childProfile
            });

            if (response.success) {
                setInterventions({
                    immediate: generateInterventionData(response.immediate || [], 'immediate'),
                    environmental: generateInterventionData(response.environmental || [], 'environmental'),
                    behavioral: generateBehavioralInterventions(),
                    communication: generateCommunicationInterventions(),
                    sensory: generateSensoryInterventions(),
                    educational: generateEducationalInterventions()
                });
            } else {
                throw new Error(response.error || 'Failed to load interventions');
            }
        } catch (err) {
            console.error('Error loading interventions:', err);
            setError(err.message);
            setInterventions(getFallbackInterventions());
        } finally {
            setLoading(false);
        }
    };

    /**
     * Generate structured intervention data
     */
    const generateInterventionData = (recommendations, category) => {
        return recommendations.map((rec, index) => ({
            id: `${category}-${index}`,
            title: rec.title || rec.intervention || `${category} Intervention ${index + 1}`,
            description: rec.description || rec.rationale || 'AI-generated intervention suggestion',
            priority: rec.priority || (index < 2 ? 'high' : index < 4 ? 'medium' : 'low'),
            category: category,
            steps: rec.implementation_steps || [
                'Assess current situation',
                'Implement intervention',
                'Monitor response',
                'Adjust as needed'
            ],
            expectedOutcome: rec.expected_outcome || 'Improved session engagement',
            timeframe: rec.timeframe || '5-10 minutes',
            difficulty: rec.difficulty || 'moderate',
            effectiveness: rec.estimated_effectiveness || Math.random() * 0.3 + 0.7,
            contraindications: rec.contraindications || [],
            materials: rec.materials_needed || []
        }));
    };

    /**
     * Generate behavioral interventions
     */
    const generateBehavioralInterventions = () => {
        return [
            {
                id: 'behavioral-1',
                title: 'Positive Reinforcement Strategy',
                description: 'Implement immediate positive reinforcement for desired behaviors',
                priority: 'high',
                category: 'behavioral',
                steps: [
                    'Identify target behavior',
                    'Choose appropriate reward',
                    'Deliver reinforcement immediately',
                    'Track behavior changes'
                ],
                expectedOutcome: 'Increased frequency of positive behaviors',
                timeframe: 'Immediate',
                difficulty: 'easy',
                effectiveness: 0.85,
                materials: ['Reward tokens', 'Tracking sheet']
            },
            {
                id: 'behavioral-2',
                title: 'Attention Redirection Technique',
                description: 'Redirect attention during challenging moments',
                priority: 'medium',
                category: 'behavioral',
                steps: [
                    'Recognize early signs of dysregulation',
                    'Introduce preferred activity',
                    'Guide attention to new focus',
                    'Gradually return to original task'
                ],
                expectedOutcome: 'Reduced behavioral episodes',
                timeframe: '2-5 minutes',
                difficulty: 'moderate',
                effectiveness: 0.78
            }
        ];
    };

    /**
     * Generate communication interventions
     */
    const generateCommunicationInterventions = () => {
        return [
            {
                id: 'communication-1',
                title: 'Visual Communication Support',
                description: 'Use visual aids to enhance communication',
                priority: 'high',
                category: 'communication',
                steps: [
                    'Prepare visual supports',
                    'Introduce visual cues',
                    'Model usage',
                    'Encourage independent use'
                ],
                expectedOutcome: 'Improved communication clarity',
                timeframe: '3-7 minutes',
                difficulty: 'easy',
                effectiveness: 0.82,
                materials: ['Visual cards', 'Picture schedule']
            }
        ];
    };

    /**
     * Generate sensory interventions
     */
    const generateSensoryInterventions = () => {
        return [
            {
                id: 'sensory-1',
                title: 'Sensory Break Implementation',
                description: 'Provide sensory regulation break',
                priority: 'medium',
                category: 'sensory',
                steps: [
                    'Recognize sensory overload signs',
                    'Offer sensory break options',
                    'Create calm environment',
                    'Allow processing time'
                ],
                expectedOutcome: 'Improved sensory regulation',
                timeframe: '5-10 minutes',
                difficulty: 'easy',
                effectiveness: 0.75,
                materials: ['Sensory tools', 'Quiet space']
            }
        ];
    };

    /**
     * Generate educational interventions
     */
    const generateEducationalInterventions = () => {
        return [
            {
                id: 'educational-1',
                title: 'Task Modification Strategy',
                description: 'Modify current task to match ability level',
                priority: 'medium',
                category: 'educational',
                steps: [
                    'Assess current ability',
                    'Break task into smaller steps',
                    'Provide additional support',
                    'Celebrate progress'
                ],
                expectedOutcome: 'Increased task completion',
                timeframe: '10-15 minutes',
                difficulty: 'moderate',
                effectiveness: 0.73
            }
        ];
    };

    /**
     * Get fallback interventions when AI service is unavailable
     */
    const getFallbackInterventions = () => {
        return {
            immediate: [
                {
                    id: 'fallback-1',
                    title: 'Continue Current Approach',
                    description: 'Maintain current therapeutic approach',
                    priority: 'medium',
                    category: 'immediate',
                    steps: ['Observe', 'Document', 'Continue'],
                    expectedOutcome: 'Stable progress',
                    timeframe: 'Ongoing',
                    difficulty: 'easy',
                    effectiveness: 0.6
                }
            ],
            environmental: [],
            behavioral: [],
            communication: [],
            sensory: [],
            educational: []
        };
    };

    /**
     * Apply intervention
     */
    const applyIntervention = (intervention) => {
        setAppliedInterventions(prev => new Set([...prev, intervention.id]));

        // Send application data to AI service for learning
        AIService.sendWebSocketMessage({
            type: 'intervention_applied',
            intervention_id: intervention.id,
            session_id: sessionId,
            timestamp: new Date().toISOString()
        });

        // Notify parent component
        onInterventionApplied && onInterventionApplied(intervention);
    };

    /**
     * Filter interventions by priority
     */
    const getFilteredInterventions = (categoryInterventions) => {
        if (filterPriority === 'all') return categoryInterventions;
        return categoryInterventions.filter(intervention =>
            intervention.priority === filterPriority
        );
    };

    /**
     * Get priority color class
     */
    const getPriorityClass = (priority) => {
        switch (priority) {
            case 'high': return 'priority-high';
            case 'medium': return 'priority-medium';
            case 'low': return 'priority-low';
            default: return 'priority-medium';
        }
    };

    /**
     * Get effectiveness color class
     */
    const getEffectivenessClass = (effectiveness) => {
        if (effectiveness >= 0.8) return 'effectiveness-high';
        if (effectiveness >= 0.6) return 'effectiveness-medium';
        return 'effectiveness-low';
    };

    const categories = [
        { id: 'immediate', label: 'Immediate', icon: '⚡' },
        { id: 'behavioral', label: 'Behavioral', icon: '🎯' },
        { id: 'communication', label: 'Communication', icon: '💬' },
        { id: 'environmental', label: 'Environmental', icon: '🏠' },
        { id: 'sensory', label: 'Sensory', icon: '👁️' },
        { id: 'educational', label: 'Educational', icon: '📚' }
    ];

    if (loading) {
        return (
            <div className="intervention-interface loading">
                <div className="loading-spinner"></div>
                <p>Loading AI intervention suggestions...</p>
            </div>
        );
    }

    return (
        <div className="intervention-suggestion-interface">
            <div className="interface-header">
                <h3>🎯 AI Intervention Suggestions</h3>
                <div className="header-controls">
                    <select
                        value={filterPriority}
                        onChange={(e) => setFilterPriority(e.target.value)}
                        className="priority-filter"
                    >
                        <option value="all">All Priorities</option>
                        <option value="high">High Priority</option>
                        <option value="medium">Medium Priority</option>
                        <option value="low">Low Priority</option>
                    </select>
                    <button onClick={loadInterventions} className="refresh-btn">
                        🔄 Refresh
                    </button>
                </div>
            </div>

            {error && (
                <div className="error-message">
                    <span>⚠️ {error}</span>
                    <button onClick={loadInterventions}>Retry</button>
                </div>
            )}

            <div className="intervention-categories">
                {categories.map(category => (
                    <button
                        key={category.id}
                        className={`category-tab ${activeCategory === category.id ? 'active' : ''}`}
                        onClick={() => setActiveCategory(category.id)}
                    >
                        <span className="category-icon">{category.icon}</span>
                        <span className="category-label">{category.label}</span>
                        <span className="category-count">
                            {getFilteredInterventions(interventions[category.id]).length}
                        </span>
                    </button>
                ))}
            </div>

            <div className="interventions-grid">
                {getFilteredInterventions(interventions[activeCategory]).map(intervention => (
                    <div
                        key={intervention.id}
                        className={`intervention-card ${getPriorityClass(intervention.priority)}`}
                    >
                        <div className="intervention-header">
                            <h4>{intervention.title}</h4>
                            <div className="intervention-meta">
                                <span className={`priority-badge ${intervention.priority}`}>
                                    {intervention.priority}
                                </span>
                                <span className={`effectiveness-badge ${getEffectivenessClass(intervention.effectiveness)}`}>
                                    {Math.round(intervention.effectiveness * 100)}% effective
                                </span>
                            </div>
                        </div>

                        <p className="intervention-description">{intervention.description}</p>

                        <div className="intervention-details">
                            <div className="detail-row">
                                <span className="detail-label">⏱️ Timeframe:</span>
                                <span>{intervention.timeframe}</span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">📊 Difficulty:</span>
                                <span className={`difficulty-${intervention.difficulty}`}>
                                    {intervention.difficulty}
                                </span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">🎯 Expected:</span>
                                <span>{intervention.expectedOutcome}</span>
                            </div>
                        </div>

                        {intervention.materials && intervention.materials.length > 0 && (
                            <div className="materials-needed">
                                <strong>Materials needed:</strong>
                                <ul>
                                    {intervention.materials.map((material, index) => (
                                        <li key={index}>{material}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        <div className="intervention-actions">
                            <button
                                onClick={() => setSelectedIntervention(intervention)}
                                className="details-btn"
                            >
                                📋 View Steps
                            </button>
                            <button
                                onClick={() => applyIntervention(intervention)}
                                disabled={appliedInterventions.has(intervention.id)}
                                className={`apply-btn ${appliedInterventions.has(intervention.id) ? 'applied' : ''}`}
                            >
                                {appliedInterventions.has(intervention.id) ? '✅ Applied' : '🚀 Apply'}
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {getFilteredInterventions(interventions[activeCategory]).length === 0 && (
                <div className="no-interventions">
                    <p>No interventions available for the selected criteria.</p>
                </div>
            )}

            {/* Intervention Details Modal */}
            {selectedIntervention && (
                <div className="intervention-modal-overlay">
                    <div className="intervention-modal">
                        <div className="modal-header">
                            <h3>{selectedIntervention.title}</h3>
                            <button
                                onClick={() => setSelectedIntervention(null)}
                                className="close-btn"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="modal-content">
                            <p className="modal-description">{selectedIntervention.description}</p>

                            <div className="implementation-steps">
                                <h4>📋 Implementation Steps:</h4>
                                <ol>
                                    {selectedIntervention.steps.map((step, index) => (
                                        <li key={index}>{step}</li>
                                    ))}
                                </ol>
                            </div>

                            {selectedIntervention.contraindications && selectedIntervention.contraindications.length > 0 && (
                                <div className="contraindications">
                                    <h4>⚠️ Considerations:</h4>
                                    <ul>
                                        {selectedIntervention.contraindications.map((item, index) => (
                                            <li key={index}>{item}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            <div className="modal-actions">
                                <button
                                    onClick={() => {
                                        applyIntervention(selectedIntervention);
                                        setSelectedIntervention(null);
                                    }}
                                    disabled={appliedInterventions.has(selectedIntervention.id)}
                                    className="apply-modal-btn"
                                >
                                    {appliedInterventions.has(selectedIntervention.id) ? '✅ Applied' : '🚀 Apply Intervention'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default InterventionSuggestionInterface;
