# WebBOF Frontend React Application

This is the React-based frontend for the WebBOF application.

## AI Integration Components

The WebBOF frontend includes a set of AI-powered components that provide real-time insights, clinical recommendations, progress predictions, and intervention suggestions. These components integrate seamlessly with the `aiService.js` service.

### Key Components

- **AIInsightsPanel**: Main component for displaying AI insights
- **ClinicalRecommendationViewer**: Displays AI-generated clinical recommendations
- **ProgressPredictionCharts**: Shows progress charts and predictions
- **InterventionSuggestionInterface**: Offers real-time intervention suggestions

### JavaScript Migration

All AI components have been successfully migrated from TypeScript to JavaScript for better compatibility with the rest of the codebase. This migration includes:

1. Converting TypeScript interfaces and types to JSDoc comments
2. Updating import statements to use the `.js` extension 
3. Converting type declarations to JavaScript-friendly formats
4. Enhancing error handling for runtime type safety

### Usage Example

```jsx
import React from 'react';
import { AIInsightsPanel } from './components/ai';
import AIService from './services/aiService.js';

const MyComponent = () => {
  const sessionId = 'session-12345';
  const childId = 'child-67890';

  const handleRecommendation = (rec) => {
    console.log('Selected recommendation:', rec);
  };

  return (
    <AIInsightsPanel 
      sessionId={sessionId}
      childId={childId}
      isActive={true}
      onRecommendationSelect={handleRecommendation}
    />
  );
};
```

## Getting Started

1. Install dependencies: `npm install`
2. Start the development server: `npm start`
3. Build for production: `npm run build`

## WebSocket Connection

The AI components establish a WebSocket connection to the AI service for real-time updates. The connection is managed by the `aiService.js` service, which handles:

- Connection establishment and error recovery
- Authentication and session management
- Real-time insight processing
- Subscribe/unsubscribe pattern for notifications
