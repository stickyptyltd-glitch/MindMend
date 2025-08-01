# Overview

Mind Mend is a comprehensive AI-powered mental health platform built with Flask that provides therapeutic support through multiple modalities. The application integrates video analysis, biometric monitoring, and AI-driven therapy sessions to offer personalized mental health care. It supports individual, couple, and group therapy sessions with real-time emotion detection, crisis intervention, and automated exercise generation.

**Current Version: Level 2**
- Real OpenAI GPT-4o integration for authentic therapeutic responses
- Session-specific AI prompts for individual, couple, and group therapy
- Premium human counselor hooks with payment gateway preparation
- Advanced video assessment placeholders with microexpression analysis hooks
- Enhanced crisis detection with multi-modal analysis preparation

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap-based responsive design
- **Real-time Communication**: Socket.IO for live video analysis and biometric data streaming
- **Video Processing**: Client-side JavaScript for camera capture and frame processing
- **Biometric Integration**: JavaScript classes for connecting to various wearable devices (Apple Watch, Fitbit, Garmin, etc.)
- **Dashboard**: Interactive charts and data visualization using Chart.js

## Backend Architecture
- **Web Framework**: Flask with SQLAlchemy ORM for database operations
- **Database**: SQLite with automatic table creation and migration support
- **AI Processing**: Modular AI manager supporting multiple models (OpenAI GPT-4o primary, with fallback responses)
- **Video Analysis**: Real-time facial emotion recognition and microexpression detection
- **Health Monitoring**: Crisis detection system scanning text and behavior for risk indicators
- **Exercise Generation**: AI-powered personalized therapeutic exercise recommendations

## Data Storage
- **Primary Database**: SQLite with models for sessions, biometric data, and video analysis
- **Session Storage**: Flask sessions for user state management
- **Real-time Data**: In-memory buffering for live biometric streams
- **File Storage**: Local filesystem for static assets and data directory

## Security & Privacy
- **Crisis Detection**: Multi-level risk assessment with immediate intervention protocols
- **Data Privacy**: Local data storage with session-based user management
- **Video Processing**: Client-side frame capture with selective server transmission

## AI Integration Architecture
- **Primary AI**: OpenAI GPT-4o for therapeutic responses and analysis (Level 2: ACTIVE)
- **Session-Specific Prompts**: Different therapeutic approaches for individual, couple, and group sessions
- **Fallback System**: Local dummy responses when API unavailable
- **Multi-modal Analysis**: Combined text, video, and biometric data processing (Level 3+ preparation)
- **Context-aware Responses**: Session type and historical data consideration
- **Future AI Modules**: Placeholder classes for microexpression analysis and biosensor integration

## Level 2 Features (Current)
- **Real AI Responses**: OpenAI GPT-4o integration with authentic therapeutic conversations
- **Enhanced Session Types**: Specialized prompts for individual, couple, and group therapy
- **Premium Counselor Hooks**: Placeholder routes and UI for human therapist services
- **Video Assessment Platform**: Advanced video analysis preparation with WebRTC hooks
- **Payment Integration Hooks**: Stripe/PayPal preparation for premium services
- **Microexpression Analysis Preparation**: Future AI modules and integration points documented

# External Dependencies

## AI Services
- **OpenAI API**: GPT-4o model for therapeutic conversations and advanced analysis
- **OpenAI Vision API**: Facial emotion recognition and video frame analysis

## Frontend Libraries
- **Bootstrap**: UI framework with dark theme support
- **Chart.js**: Data visualization for biometric trends and progress tracking
- **Socket.IO**: Real-time bidirectional communication
- **Font Awesome**: Icon library for enhanced UI

## Backend Dependencies
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM with SQLite support
- **Flask-SocketIO**: WebSocket integration for real-time features
- **Werkzeug**: WSGI utilities and middleware

## Biometric Device Integration
- **Apple HealthKit**: Apple Watch integration (requires native app)
- **Fitbit API**: Fitness tracker data access
- **Garmin Connect**: Sports watch integration
- **Samsung Health**: Android health platform
- **Web HID API**: Generic device connectivity
- **Simulation Layer**: Mock data for development and testing

## Development Tools
- **Replit Environment**: Cloud-based development with automatic deployment
- **Environment Variables**: Configuration management for API keys and secrets
- **Logging**: Built-in Python logging for debugging and monitoring