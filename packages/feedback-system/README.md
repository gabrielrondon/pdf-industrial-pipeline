# PDF Pipeline Feedback System

A modular feedback system for enhancing ML training through user engagement and gamification.

## Features

- 🎯 **Document-specific feedback questions** based on judicial document types
- 🚩 **Flag missing information** feature for users to report AI oversights  
- 💰 **Credit reward system** with tiered incentives
- 🏆 **Quality multipliers** for consistent and accurate feedback
- 📊 **Peer validation** system for shared documents
- 🔧 **Easy integration/removal** - self-contained package

## Installation

```bash
# Install the package
npm install @pdf-pipeline/feedback-system

# Build the package
cd packages/feedback-system
npm run build
```

## Quick Start

```typescript
import { 
  FeedbackProvider, 
  DocumentFeedback, 
  useFeedback 
} from '@pdf-pipeline/feedback-system';

// Wrap your app
<FeedbackProvider>
  <DocumentFeedback documentId="123" documentType="iptu" />
</FeedbackProvider>
```

## Package Structure

```
packages/feedback-system/
├── src/
│   ├── types/           # TypeScript definitions
│   ├── services/        # Business logic and API calls
│   ├── components/      # React components
│   ├── hooks/          # React hooks
│   └── utils/          # Helper functions
├── dist/               # Built files
└── package.json
```

## Easy Removal

To remove the feedback system:

1. Remove package dependency from consuming apps
2. Remove feedback-related imports
3. Delete the `packages/feedback-system` directory
4. Remove feedback tables from database (optional)

## API Integration

The package provides a clean interface to integrate with your existing:
- Credit system
- ML pipeline
- User authentication
- Document processing

See the [Integration Guide](./docs/integration.md) for detailed setup instructions.