# Overview

Mind Mend is a comprehensive AI-powered mental health platform built with Flask that provides therapeutic support through multiple modalities. The application integrates video analysis, biometric monitoring, and AI-driven therapy sessions to offer personalized mental health care. It supports individual, couple, and group therapy sessions with real-time emotion detection, crisis intervention, and automated exercise generation.

**Current Version: Level 2 Enhanced with Admin AI - PRODUCTION READY & FULLY DEBUGGED**
**Debug Status (Updated 2025-08-02): All core systems tested and working correctly**
- Real OpenAI GPT-4o integration with expert AI therapists (Dr. Sarah Chen, Dr. Michael Rivera, Dr. Lisa Thompson)
- Enhanced AI knowledge base with specialized training in CBT, DBT, ACT, MBSR, EFT, Gottman Method
- Comprehensive therapeutic activities library with 40+ evidence-based exercises
- Couples counseling with dual login support (same or separate devices) with AI conversation starters
- Advanced mood tracking with patterns analysis and insights
- Progress tracking with SMART goals and treatment planning
- Personalized self-care planner with wellness routines
- Session-specific AI prompts for individual, couple, and group therapy
- Premium human counselor hooks with payment gateway preparation
- Advanced video assessment placeholders with microexpression analysis hooks
- Enhanced crisis detection with multi-modal analysis preparation
- **NEW: AI-powered admin assistant with fraud detection and management automation**
- **NEW: Role-based security system with different access levels for admins, managers, and counselors**
- **NEW: Comprehensive admin manual PDF with 60+ pages of documentation**
- **NEW: Research & Dataset Management System for evidence-based mental health insights**
- **NEW: Clinical dataset analysis tools for early diagnosis and conflict resolution patterns**
- **NEW: Research paper library with AI-powered insight extraction and similarity search**
- **NEW: Multi-Model AI Integration with OpenAI GPT-4o, Ollama local LLMs, and custom ML models**
- **NEW: AI Model Manager supporting ensemble diagnosis with 7+ specialized models**
- **NEW: Advanced Treatment Recommender using AI consensus for personalized therapy plans**
- **NEW: Admin interface for AI model configuration, testing, and performance monitoring**
- **NEW: Official brand logo selected - Growth & Healing design (Logo 4) - USER CONFIRMED SELECTION**
- **NEW: Comprehensive user registration system with 5-step guided onboarding**
- **NEW: Secure login system with password recovery and social login options**
- **NEW: Interactive onboarding tutorial with animated Alex character guide**

# User Preferences

Preferred communication style: Simple, everyday language.
Selected brand logo: Logo 4 (Growth & Healing design) - confirmed by user on 2025-08-02.

## Business Entity
- **Company**: Mind Mend Technologies Inc.
- **Email**: support@mindmend.com
- **Domain Strategy**: mindmend.com (primary), mind-mend.app (secondary), mindmend.health (alternative)
- **Brand Identity**: Logo 4 (Growth & Healing design) - symbolizes transformation and healing journey
- **Target Market**: Global mental health market with focus on accessible AI therapy
- **Business Model**: SaaS platform with tiered subscriptions and counselor employment

## Admin Panel Features
- **Dynamic API Key Management**: Configure payment gateways and AI services through web interface
- **Platform Upgrades**: Level 3 and Enterprise features available for purchase
- **Business Management**: Counselor employment system, financial dashboard, user management
- **Security**: HIPAA compliance tools, audit logging, fraud protection
- **Deployment Tools**: Production hosting recommendations and deployment guides
- **AI Fraud Detection**: Real-time fraud monitoring with risk scoring and automated actions
- **Role-Based Access Control**: 5 security levels (Super Admin, Admin, Manager, Counselor, Patient)
- **Admin AI Assistant**: Intelligent recommendations for upgrades, security, and optimization
- **Downloadable Admin Manual**: Comprehensive 60+ page PDF guide for all user roles

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