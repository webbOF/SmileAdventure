/**
 * AI Integration Example
 * Demonstrates how to use the AI-enhanced frontend components
 */

import React, { useState, useEffect } from 'react';
import { AIInsightsPanel } from '../ai';
import AIService from '../../services/aiService.js';

const ExampleAIIntegration = () => {
  const [sessionId] = useState('session-12345');
  const [childId] = useState('child-67890');
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [sessionData, setSessionData] = useState({
    child_id: 'child-67890',
    session_id: 'session-12345',
    timestamp: new Date().toISOString(),
    therapist_id: 'therapist-123',
    child_profile: {
      name: 'Emma',
      age: 8,
      diagnosis: 'Autism Spectrum Disorder',
      communication_level: 'verbal',
      sensory_preferences: ['visual', 'tactile'],
      behavioral_patterns: ['routine-focused', 'social-seeking'],
      current_goals: [
        'Improve social communication',
        'Develop emotional regulation',
        'Increase attention span'
      ]
    }
  });

  // Start AI analysis session
  const startAISession = async () => {
    try {
      setIsSessionActive(true);

      // Initialize AI service connection
      await AIService.connectWebSocket({
        session_id: sessionId,
        child_id: childId
      });

      console.log('AI session started successfully');
    } catch (error) {
      console.error('Failed to start AI session:', error);
      setIsSessionActive(false);
    }
  };

  // Stop AI analysis session
  const stopAISession = async () => {
    try {
      await AIService.disconnectWebSocket();
      setIsSessionActive(false);
      console.log('AI session stopped');
    } catch (error) {
      console.error('Error stopping AI session:', error);
    }
  };

  // Handle recommendation selection
  const handleRecommendationSelect = (recommendation) => {
    console.log('Recommendation selected:', recommendation);

    // You can implement custom logic here:
    // - Log the recommendation usage
    // - Update session notes
    // - Trigger specific actions
    // - Send feedback to AI service

    // Example: Send feedback to AI service
    AIService.sendWebSocketMessage({
      type: 'recommendation_feedback',
      recommendation_id: recommendation.id,
      action: 'applied',
      session_id: sessionId,
      timestamp: new Date().toISOString()
    });
  };

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      if (isSessionActive) {
        stopAISession();
      }
    };
  }, [isSessionActive]);

  return (
    <div className="ai-integration-example">
      <div className="example-header">
        <h1>🤖 AI-Enhanced Therapy Session</h1>
        <div className="session-controls">
          <button
            onClick={startAISession}
            disabled={isSessionActive}
            className="start-btn"
          >
            {isSessionActive ? '✅ AI Active' : '🚀 Start AI Analysis'}
          </button>

          {isSessionActive && (
            <button
              onClick={stopAISession}
              className="stop-btn"
            >
              ⏹️ Stop AI Analysis
            </button>
          )}
        </div>
      </div>

      <div className="session-info">
        <div className="info-card">
          <h3>👤 Child Profile</h3>
          <p><strong>Name:</strong> {sessionData.child_profile.name}</p>
          <p><strong>Age:</strong> {sessionData.child_profile.age}</p>
          <p><strong>Diagnosis:</strong> {sessionData.child_profile.diagnosis}</p>
          <p><strong>Goals:</strong> {sessionData.child_profile.current_goals.join(', ')}</p>
        </div>

        <div className="info-card">
          <h3>🔍 Session Details</h3>
          <p><strong>Session ID:</strong> {sessionId}</p>
          <p><strong>Status:</strong> {isSessionActive ? '🟢 Active' : '🔴 Inactive'}</p>
          <p><strong>AI Analysis:</strong> {isSessionActive ? 'Running' : 'Stopped'}</p>
        </div>
      </div>

      {/* Main AI Insights Panel */}
      <AIInsightsPanel
        sessionId={sessionId}
        childId={childId}
        sessionData={sessionData}
        isActive={isSessionActive}
        onRecommendationSelect={handleRecommendationSelect}
      />

      {/* Usage Instructions */}
      <div className="usage-instructions">
        <h3>📋 How to Use AI Components</h3>
        <div className="instructions-grid">
          <div className="instruction-card">
            <h4>🔄 Real-time Insights</h4>
            <ul>
              <li>View live AI analysis of the session</li>
              <li>Monitor emotional and behavioral patterns</li>
              <li>Get instant feedback on therapy progress</li>
            </ul>
          </div>

          <div className="instruction-card">
            <h4>🎯 Clinical Recommendations</h4>
            <ul>
              <li>Access AI-generated clinical suggestions</li>
              <li>View categorized recommendations by priority</li>
              <li>Implement evidence-based interventions</li>
            </ul>
          </div>

          <div className="instruction-card">
            <h4>📈 Progress Predictions</h4>
            <ul>
              <li>Visualize therapy progress trends</li>
              <li>Predict future milestones</li>
              <li>Track skill development over time</li>
            </ul>
          </div>

          <div className="instruction-card">
            <h4>💡 Intervention Suggestions</h4>
            <ul>
              <li>Get real-time intervention ideas</li>
              <li>Apply categorized interventions</li>
              <li>Track intervention effectiveness</li>
            </ul>
          </div>
        </div>
      </div>

      <style jsx>{`
        .ai-integration-example {
          max-width: 1400px;
          margin: 0 auto;
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .example-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
          padding-bottom: 20px;
          border-bottom: 2px solid #e9ecef;
        }

        .example-header h1 {
          margin: 0;
          color: #2c3e50;
          font-size: 2rem;
        }

        .session-controls {
          display: flex;
          gap: 15px;
        }

        .start-btn, .stop-btn {
          padding: 12px 24px;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .start-btn {
          background: #28a745;
          color: white;
        }

        .start-btn:hover:not(:disabled) {
          background: #1e7e34;
        }

        .start-btn:disabled {
          background: #6c757d;
          cursor: not-allowed;
        }

        .stop-btn {
          background: #dc3545;
          color: white;
        }

        .stop-btn:hover {
          background: #c82333;
        }

        .session-info {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-bottom: 30px;
        }

        .info-card {
          background: #f8f9fa;
          padding: 20px;
          border-radius: 12px;
          border-left: 4px solid #007bff;
        }

        .info-card h3 {
          margin: 0 0 15px 0;
          color: #2c3e50;
          font-size: 1.2rem;
        }

        .info-card p {
          margin: 8px 0;
          color: #495057;
        }

        .usage-instructions {
          margin-top: 40px;
          padding: 30px;
          background: #f8f9fa;
          border-radius: 12px;
        }

        .usage-instructions h3 {
          margin: 0 0 20px 0;
          color: #2c3e50;
          font-size: 1.5rem;
        }

        .instructions-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
        }

        .instruction-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .instruction-card h4 {
          margin: 0 0 15px 0;
          color: #2c3e50;
          font-size: 1.1rem;
        }

        .instruction-card ul {
          margin: 0;
          padding-left: 20px;
        }

        .instruction-card li {
          margin-bottom: 8px;
          color: #495057;
          line-height: 1.5;
        }

        @media (max-width: 768px) {
          .example-header {
            flex-direction: column;
            gap: 20px;
            text-align: center;
          }

          .session-info {
            grid-template-columns: 1fr;
          }

          .instructions-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default ExampleAIIntegration;
