// Clinical Recommendation Viewer - AI-powered clinical insights and recommendations
// Displays clinical recommendations, intervention strategies, and professional guidance

import React, { useState } from 'react';
import PropTypes from 'prop-types';
import {
    Target,
    Clock,
    User,
    Brain,
    Zap,
    FileText,
    Star,
    ArrowRight,
    Info,
    Lightbulb,
    Shield
} from 'lucide-react';

const ClinicalRecommendationViewer = ({
    recommendations = null,
    sessionData = {},
    childId,
    onRecommendationSelect = () => { }
}) => {
    const [selectedCategory, setSelectedCategory] = useState('immediate');
    const [selectedRecommendation, setSelectedRecommendation] = useState(null);

    // Categories for organizing recommendations
    const categories = [
        {
            id: 'immediate',
            label: 'Immediate Actions',
            icon: Zap,
            color: 'red',
            description: 'Actions to take right now during the session'
        },
        {
            id: 'sessionAdjustments',
            label: 'Session Adjustments',
            icon: Target,
            color: 'blue',
            description: 'Modifications for the current session'
        },
        {
            id: 'environmental',
            label: 'Environment',
            icon: Shield,
            color: 'green',
            description: 'Environmental modifications and setup changes'
        },
        {
            id: 'skillFocus',
            label: 'Skill Focus',
            icon: Brain,
            color: 'purple',
            description: 'Skills to prioritize and develop'
        },
        {
            id: 'parentGuidance',
            label: 'Parent Guidance',
            icon: User,
            color: 'orange',
            description: 'Recommendations for parents and caregivers'
        },
        {
            id: 'clinical',
            label: 'Clinical Notes',
            icon: FileText,
            color: 'gray',
            description: 'Clinical observations and professional notes'
        },
        {
            id: 'longTerm',
            label: 'Long-term Goals',
            icon: Star,
            color: 'yellow',
            description: 'Goals and strategies for future sessions'
        }
    ];

    // Handle recommendation selection
    const handleRecommendationClick = (recommendation, category) => {
        setSelectedRecommendation({ ...recommendation, category });
        onRecommendationSelect(recommendation, category);
    };

    // Get priority level styling
    const getPriorityStyle = (priority) => {
        switch (priority?.toLowerCase()) {
            case 'high':
                return 'bg-red-100 text-red-800 border-red-200';
            case 'medium':
                return 'bg-yellow-100 text-yellow-800 border-yellow-200';
            case 'low':
                return 'bg-green-100 text-green-800 border-green-200';
            default:
                return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };

    // Get category color classes
    const getCategoryColors = (color) => {
        const colors = {
            red: 'bg-red-50 border-red-200 text-red-800',
            blue: 'bg-blue-50 border-blue-200 text-blue-800',
            green: 'bg-green-50 border-green-200 text-green-800',
            purple: 'bg-purple-50 border-purple-200 text-purple-800',
            orange: 'bg-orange-50 border-orange-200 text-orange-800',
            gray: 'bg-gray-50 border-gray-200 text-gray-800',
            yellow: 'bg-yellow-50 border-yellow-200 text-yellow-800'
        };
        return colors[color] || colors.gray;
    };

    // Render recommendation card
    const renderRecommendationCard = (recommendation, index, category) => {
        const recommendationId = `${category}_${index}`;

        return (
            <div
                key={recommendationId}
                className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleRecommendationClick(recommendation, category)}
            >
                <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-1">
                            {typeof recommendation === 'string'
                                ? recommendation
                                : recommendation.title || recommendation.description || 'Recommendation'
                            }
                        </h4>

                        {recommendation.rationale && (
                            <p className="text-sm text-gray-600 mb-2">
                                <strong>Rationale:</strong> {recommendation.rationale}
                            </p>
                        )}

                        {recommendation.details && (
                            <p className="text-sm text-gray-700">{recommendation.details}</p>
                        )}
                    </div>

                    <div className="ml-3 flex flex-col gap-2">
                        {recommendation.priority && (
                            <span className={`px-2 py-1 text-xs rounded-full border ${getPriorityStyle(recommendation.priority)}`}>
                                {recommendation.priority}
                            </span>
                        )}

                        {recommendation.urgency && (
                            <div className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                <span className="text-xs text-gray-600">{recommendation.urgency}</span>
                            </div>
                        )}
                    </div>
                </div>

                {recommendation.implementation && (
                    <div className="bg-blue-50 rounded-md p-3 mb-3">
                        <h5 className="text-sm font-medium text-blue-900 mb-1 flex items-center gap-1">
                            <Lightbulb className="w-3 h-3" />
                            Implementation
                        </h5>
                        <p className="text-sm text-blue-800">{recommendation.implementation}</p>
                    </div>
                )}

                {recommendation.expectedOutcome && (
                    <div className="bg-green-50 rounded-md p-3 mb-3">
                        <h5 className="text-sm font-medium text-green-900 mb-1 flex items-center gap-1">
                            <Target className="w-3 h-3" />
                            Expected Outcome
                        </h5>
                        <p className="text-sm text-green-800">{recommendation.expectedOutcome}</p>
                    </div>
                )}

                <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                    <div className="flex items-center gap-2">
                        {recommendation.evidenceLevel && (
                            <span className="text-xs text-gray-500">
                                Evidence: {recommendation.evidenceLevel}
                            </span>
                        )}
                    </div>

                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            handleRecommendationClick(recommendation, category);
                        }}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center gap-1"
                    >
                        Apply <ArrowRight className="w-3 h-3" />
                    </button>
                </div>
            </div>
        );
    };

    // Render category section
    const renderCategorySection = (categoryData) => {
        const categoryRecommendations = recommendations?.[categoryData.id] || [];

        if (!Array.isArray(categoryRecommendations) || categoryRecommendations.length === 0) {
            return (
                <div className="text-center py-8 text-gray-500">
                    <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p>No {categoryData.label.toLowerCase()} available</p>
                    <p className="text-sm">Recommendations will appear here when AI analysis is complete</p>
                </div>
            );
        }

        return (
            <div className="space-y-4">
                {categoryRecommendations.map((recommendation, index) =>
                    renderRecommendationCard(recommendation, index, categoryData.id)
                )}
            </div>
        );
    };

    // Render category tabs
    const renderCategoryTabs = () => (
        <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-1 overflow-x-auto">
                {categories.map((category) => {
                    const Icon = category.icon;
                    const recommendationCount = recommendations?.[category.id]?.length || 0;

                    return (
                        <button
                            key={category.id}
                            onClick={() => setSelectedCategory(category.id)}
                            className={`whitespace-nowrap py-3 px-4 border-b-2 font-medium text-sm flex items-center gap-2 ${selectedCategory === category.id
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            <Icon className="w-4 h-4" />
                            {category.label}
                            {recommendationCount > 0 && (
                                <span className="bg-gray-200 text-gray-800 text-xs rounded-full px-2 py-1 ml-1">
                                    {recommendationCount}
                                </span>
                            )}
                        </button>
                    );
                })}
            </nav>
        </div>
    );

    // Get selected category data
    const selectedCategoryData = categories.find(cat => cat.id === selectedCategory);

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                    <Target className="w-5 h-5 text-blue-500" />
                    Clinical Recommendations
                </h3>

                {recommendations && (
                    <div className="text-sm text-gray-600">
                        Last updated: {new Date().toLocaleTimeString()}
                    </div>
                )}
            </div>

            {/* No recommendations state */}
            {!recommendations && (
                <div className="text-center py-12">
                    <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Recommendations Available</h3>
                    <p className="text-gray-600 mb-4">
                        AI recommendations will appear here once session analysis is complete.
                    </p>
                    <div className="bg-blue-50 rounded-lg p-4 text-left max-w-md mx-auto">
                        <h4 className="font-medium text-blue-900 mb-2">To generate recommendations:</h4>
                        <ul className="text-sm text-blue-800 space-y-1">
                            <li>• Ensure the session is active</li>
                            <li>• Allow AI to analyze session data</li>
                            <li>• Recommendations will update in real-time</li>
                        </ul>
                    </div>
                </div>
            )}

            {/* Recommendations content */}
            {recommendations && (
                <>
                    {/* Category description */}
                    {selectedCategoryData && (
                        <div className={`rounded-lg p-4 border ${getCategoryColors(selectedCategoryData.color)}`}>
                            <div className="flex items-center gap-2 mb-2">
                                <selectedCategoryData.icon className="w-5 h-5" />
                                <h4 className="font-medium">{selectedCategoryData.label}</h4>
                            </div>
                            <p className="text-sm">{selectedCategoryData.description}</p>
                        </div>
                    )}

                    {/* Category tabs */}
                    {renderCategoryTabs()}

                    {/* Selected category content */}
                    {selectedCategoryData && renderCategorySection(selectedCategoryData)}
                </>
            )}

            {/* Selected recommendation detail modal */}
            {selectedRecommendation && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                        <div className="p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold">Recommendation Details</h3>
                                <button
                                    onClick={() => setSelectedRecommendation(null)}
                                    className="text-gray-400 hover:text-gray-600"
                                >
                                    ×
                                </button>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <h4 className="font-medium mb-2">Description</h4>
                                    <p className="text-gray-700">
                                        {typeof selectedRecommendation === 'string'
                                            ? selectedRecommendation
                                            : selectedRecommendation.title || selectedRecommendation.description
                                        }
                                    </p>
                                </div>

                                {selectedRecommendation.implementation && (
                                    <div>
                                        <h4 className="font-medium mb-2">How to Implement</h4>
                                        <p className="text-gray-700">{selectedRecommendation.implementation}</p>
                                    </div>
                                )}

                                <div className="flex justify-end gap-3 pt-4 border-t">
                                    <button
                                        onClick={() => setSelectedRecommendation(null)}
                                        className="px-4 py-2 text-gray-600 hover:text-gray-800"
                                    >
                                        Close
                                    </button>
                                    <button
                                        onClick={() => {
                                            onRecommendationSelect(selectedRecommendation, selectedRecommendation.category);
                                            setSelectedRecommendation(null);
                                        }}
                                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                                    >
                                        Apply Recommendation
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

// PropTypes validation
ClinicalRecommendationViewer.propTypes = {
    recommendations: PropTypes.object,
    sessionData: PropTypes.object,
    childId: PropTypes.string,
    onRecommendationSelect: PropTypes.func
};

ClinicalRecommendationViewer.defaultProps = {
    recommendations: null,
    sessionData: {},
    childId: null,
    onRecommendationSelect: () => { }
};

export default ClinicalRecommendationViewer;
