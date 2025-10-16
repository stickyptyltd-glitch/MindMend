"""
Advanced AI Model Orchestrator
Intelligently routes requests to optimal AI providers
Tracks performance and trains custom models from responses
"""

import os
import json
import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import numpy as np

# Import analytics and crisis systems
from models.model_training_analytics import ModelTrainingAnalytics, ModelResponse
from models.universal_crisis_predictor import UniversalCrisisPredictor, CrisisSeverity

# Import existing models
from models.ai_manager import AIManager
from models.therapy_ai_integration import TherapyAIIntegration

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Types of AI tasks"""
    CRISIS_DETECTION = "crisis_detection"
    THERAPY_RESPONSE = "therapy_response"
    EMOTION_ANALYSIS = "emotion_analysis"
    EXERCISE_GENERATION = "exercise_generation"
    TREATMENT_PLANNING = "treatment_planning"
    CONVERSATION = "conversation"
    ASSESSMENT = "assessment"
    RESEARCH = "research"

class ProviderStatus(Enum):
    """Provider availability status"""
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"

@dataclass
class ProviderConfig:
    """Configuration for each AI provider"""
    name: str
    type: str  # openai, anthropic, google, huggingface, ollama
    models: List[str]
    capabilities: List[TaskType]
    cost_per_token: float
    max_tokens_per_minute: int
    priority: int  # Lower is higher priority
    requires_api_key: bool
    is_local: bool
    status: ProviderStatus = ProviderStatus.AVAILABLE

@dataclass
class ModelRequest:
    """Request to AI model"""
    task_type: TaskType
    prompt: str
    context: Dict[str, Any]
    user_tier: str
    max_cost: Optional[float] = None
    required_models: Optional[List[str]] = None
    timeout: float = 30.0

@dataclass
class ModelEnsembleResponse:
    """Response from multiple models"""
    primary_response: str
    consensus_response: Optional[str]
    individual_responses: List[ModelResponse]
    total_cost: float
    total_latency: float
    models_used: List[str]
    confidence: float
    metadata: Dict[str, Any]

class AIOrchestrator:
    """
    Central AI orchestration system
    Routes requests to optimal providers and manages multi-model consensus
    """

    def __init__(self):
        self.analytics = ModelTrainingAnalytics()
        self.crisis_predictor = UniversalCrisisPredictor()
        self.ai_manager = AIManager()
        self.therapy_ai = TherapyAIIntegration()

        # Initialize providers
        self.providers = self._initialize_providers()

        # Provider health tracking
        self.provider_health = {
            provider.name: {
                'success_rate': 1.0,
                'avg_latency': 0.0,
                'error_count': 0,
                'last_error': None,
                'requests_this_minute': 0
            }
            for provider in self.providers.values()
        }

        # Task routing configuration
        self.task_routes = self._configure_task_routes()

        # Async executor
        self.executor = ThreadPoolExecutor(max_workers=6)

        # Response cache
        self.response_cache = {}
        self.cache_ttl = 300  # 5 minutes

    def _initialize_providers(self) -> Dict[str, ProviderConfig]:
        """Initialize AI provider configurations"""

        providers = {}

        # OpenAI
        providers['openai'] = ProviderConfig(
            name='openai',
            type='openai',
            models=['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'],
            capabilities=[TaskType.THERAPY_RESPONSE, TaskType.CONVERSATION,
                         TaskType.EXERCISE_GENERATION, TaskType.TREATMENT_PLANNING],
            cost_per_token=0.00003,  # Average
            max_tokens_per_minute=90000,
            priority=1,
            requires_api_key=True,
            is_local=False
        )

        # Anthropic Claude (when integrated)
        providers['anthropic'] = ProviderConfig(
            name='anthropic',
            type='anthropic',
            models=['claude-3-opus', 'claude-3-sonnet', 'claude-instant'],
            capabilities=[TaskType.CRISIS_DETECTION, TaskType.THERAPY_RESPONSE,
                         TaskType.ASSESSMENT, TaskType.TREATMENT_PLANNING],
            cost_per_token=0.00002,
            max_tokens_per_minute=100000,
            priority=2,
            requires_api_key=True,
            is_local=False,
            status=ProviderStatus.UNAVAILABLE  # Not yet integrated
        )

        # Google Gemini (when integrated)
        providers['google'] = ProviderConfig(
            name='google',
            type='google',
            models=['gemini-1.5-pro', 'gemini-1.5-flash'],
            capabilities=[TaskType.EMOTION_ANALYSIS, TaskType.ASSESSMENT,
                         TaskType.CONVERSATION, TaskType.RESEARCH],
            cost_per_token=0.00001,
            max_tokens_per_minute=120000,
            priority=3,
            requires_api_key=True,
            is_local=False,
            status=ProviderStatus.UNAVAILABLE  # Not yet integrated
        )

        # Hugging Face
        providers['huggingface'] = ProviderConfig(
            name='huggingface',
            type='huggingface',
            models=['mental-bert', 'emotion-roberta', 'dialogpt'],
            capabilities=[TaskType.EMOTION_ANALYSIS, TaskType.CRISIS_DETECTION,
                         TaskType.ASSESSMENT],
            cost_per_token=0.0,  # Free tier
            max_tokens_per_minute=60000,
            priority=4,
            requires_api_key=False,
            is_local=False,
            status=ProviderStatus.UNAVAILABLE  # Not yet integrated
        )

        # Ollama (Local)
        providers['ollama'] = ProviderConfig(
            name='ollama',
            type='ollama',
            models=['llama2', 'mistral', 'phi-2'],
            capabilities=[TaskType.CONVERSATION, TaskType.THERAPY_RESPONSE,
                         TaskType.EXERCISE_GENERATION],
            cost_per_token=0.0,  # Local
            max_tokens_per_minute=1000000,  # No limit
            priority=5,
            requires_api_key=False,
            is_local=True
        )

        # Custom Models
        providers['custom'] = ProviderConfig(
            name='custom',
            type='custom',
            models=['crisis_detector', 'emotion_classifier', 'therapy_enhancer'],
            capabilities=[TaskType.CRISIS_DETECTION, TaskType.EMOTION_ANALYSIS],
            cost_per_token=0.0,  # Local
            max_tokens_per_minute=1000000,  # No limit
            priority=6,
            requires_api_key=False,
            is_local=True
        )

        return providers

    def _configure_task_routes(self) -> Dict[TaskType, Dict[str, List[str]]]:
        """Configure routing for each task type by user tier"""

        return {
            TaskType.CRISIS_DETECTION: {
                'free': ['custom', 'ollama'],
                'basic': ['custom', 'ollama', 'huggingface'],
                'premium': ['anthropic', 'custom', 'openai'],
                'enterprise': ['anthropic', 'openai', 'custom', 'google']
            },
            TaskType.THERAPY_RESPONSE: {
                'free': ['ollama'],
                'basic': ['openai:gpt-3.5-turbo', 'ollama'],
                'premium': ['openai:gpt-4o', 'anthropic:claude-3-sonnet'],
                'enterprise': ['openai:gpt-4o', 'anthropic:claude-3-opus', 'google:gemini-1.5-pro']
            },
            TaskType.EMOTION_ANALYSIS: {
                'free': ['custom', 'ollama'],
                'basic': ['huggingface', 'custom'],
                'premium': ['google:gemini-1.5-flash', 'huggingface'],
                'enterprise': ['google:gemini-1.5-pro', 'openai:gpt-4o-vision']
            },
            TaskType.EXERCISE_GENERATION: {
                'free': ['ollama'],
                'basic': ['openai:gpt-3.5-turbo'],
                'premium': ['openai:gpt-4o-mini', 'anthropic:claude-instant'],
                'enterprise': ['openai:gpt-4o', 'anthropic:claude-3-sonnet']
            },
            TaskType.TREATMENT_PLANNING: {
                'free': ['ollama'],
                'basic': ['openai:gpt-3.5-turbo'],
                'premium': ['openai:gpt-4o', 'anthropic:claude-3-sonnet'],
                'enterprise': ['anthropic:claude-3-opus', 'openai:gpt-4o', 'google:gemini-1.5-pro']
            }
        }

    async def process_request(self, request: ModelRequest) -> ModelEnsembleResponse:
        """
        Process request through optimal AI providers
        """

        start_time = time.time()

        # Special handling for crisis detection
        if request.task_type == TaskType.CRISIS_DETECTION:
            return await self._handle_crisis_detection(request)

        # Get available providers for this request
        available_providers = self._get_available_providers(request)

        if not available_providers:
            logger.error(f"No available providers for {request.task_type}")
            return self._create_fallback_response(request)

        # Determine how many models to use
        num_models = self._determine_ensemble_size(request)

        # Execute requests in parallel
        tasks = []
        for i in range(min(num_models, len(available_providers))):
            provider = available_providers[i]
            task = asyncio.create_task(
                self._call_provider(provider, request)
            )
            tasks.append(task)

        # Wait for responses
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors
        valid_responses = [r for r in responses if isinstance(r, ModelResponse)]

        if not valid_responses:
            logger.error("All provider calls failed")
            return self._create_fallback_response(request)

        # Log responses for training
        for response in valid_responses:
            await self.analytics.capture_model_response(
                session_id=request.context.get('session_id', 'unknown'),
                input_text=request.prompt,
                model_name=response.model_name,
                provider=response.provider,
                response=response.response,
                confidence=response.confidence,
                latency=response.latency,
                cost=response.cost
            )

        # Generate consensus if multiple models
        if len(valid_responses) > 1:
            consensus = await self._generate_consensus(valid_responses, request)
        else:
            consensus = valid_responses[0].response

        # Calculate metrics
        total_cost = sum(r.cost for r in valid_responses)
        total_latency = time.time() - start_time
        avg_confidence = np.mean([r.confidence for r in valid_responses])

        return ModelEnsembleResponse(
            primary_response=valid_responses[0].response,
            consensus_response=consensus if len(valid_responses) > 1 else None,
            individual_responses=valid_responses,
            total_cost=total_cost,
            total_latency=total_latency,
            models_used=[r.model_name for r in valid_responses],
            confidence=avg_confidence,
            metadata={
                'task_type': request.task_type.value,
                'user_tier': request.user_tier,
                'num_models': len(valid_responses)
            }
        )

    async def _handle_crisis_detection(self, request: ModelRequest) -> ModelEnsembleResponse:
        """Special handling for crisis detection"""

        # Always use universal crisis predictor
        crisis_result = await self.crisis_predictor.predict_crisis(
            text=request.prompt,
            user_tier=request.user_tier,
            context=request.context,
            force_free=request.user_tier == 'free'
        )

        # Create response
        response_text = self._format_crisis_response(crisis_result)

        # Log for training
        model_response = ModelResponse(
            model_name='universal_crisis_predictor',
            provider='custom',
            response=response_text,
            confidence=crisis_result.confidence,
            latency=crisis_result.latency,
            cost=crisis_result.cost,
            timestamp=datetime.now(),
            session_id=request.context.get('session_id', 'unknown'),
            crisis_detected=crisis_result.is_crisis,
            risk_level=crisis_result.severity.value
        )

        await self.analytics.capture_model_response(
            session_id=request.context.get('session_id', 'unknown'),
            input_text=request.prompt,
            model_name=model_response.model_name,
            provider=model_response.provider,
            response=model_response.response,
            confidence=model_response.confidence,
            latency=model_response.latency,
            cost=model_response.cost,
            crisis_detected=crisis_result.is_crisis,
            risk_level=crisis_result.severity.value
        )

        return ModelEnsembleResponse(
            primary_response=response_text,
            consensus_response=None,
            individual_responses=[model_response],
            total_cost=crisis_result.cost,
            total_latency=crisis_result.latency,
            models_used=[crisis_result.model_used],
            confidence=crisis_result.confidence,
            metadata={
                'task_type': TaskType.CRISIS_DETECTION.value,
                'user_tier': request.user_tier,
                'crisis_detected': crisis_result.is_crisis,
                'severity': crisis_result.severity.value,
                'requires_human_review': crisis_result.requires_human_review
            }
        )

    def _format_crisis_response(self, crisis_result) -> str:
        """Format crisis detection result as response"""

        if not crisis_result.is_crisis:
            return "No immediate crisis indicators detected. Continue monitoring."

        response = f"Crisis Risk Level: {crisis_result.severity.value.upper()}\n"
        response += f"Confidence: {crisis_result.confidence:.1%}\n\n"

        if crisis_result.risk_factors:
            response += "Risk Factors Identified:\n"
            for factor in crisis_result.risk_factors:
                response += f"• {factor}\n"
            response += "\n"

        if crisis_result.recommended_actions:
            response += "Recommended Actions:\n"
            for action in crisis_result.recommended_actions:
                response += f"• {action}\n"

        if crisis_result.requires_human_review:
            response += "\n⚠️ This assessment requires human review"

        return response

    def _get_available_providers(self, request: ModelRequest) -> List[ProviderConfig]:
        """Get available providers for request"""

        # Get route configuration
        routes = self.task_routes.get(request.task_type, {})
        tier_providers = routes.get(request.user_tier, ['ollama'])

        available = []
        for provider_spec in tier_providers:
            if ':' in provider_spec:
                provider_name, model = provider_spec.split(':')
            else:
                provider_name = provider_spec
                model = None

            provider = self.providers.get(provider_name)
            if not provider:
                continue

            # Check availability
            if provider.status != ProviderStatus.AVAILABLE:
                continue

            # Check API key requirement
            if provider.requires_api_key:
                if provider.name == 'openai' and not os.getenv('OPENAI_API_KEY'):
                    continue
                # Add checks for other providers when integrated

            # Check cost constraint
            if request.max_cost and provider.cost_per_token > 0:
                estimated_cost = provider.cost_per_token * 1000  # Estimate 1000 tokens
                if estimated_cost > request.max_cost:
                    continue

            available.append(provider)

        # Sort by priority
        available.sort(key=lambda p: p.priority)

        return available

    def _determine_ensemble_size(self, request: ModelRequest) -> int:
        """Determine how many models to use"""

        # Base ensemble size on user tier and task importance
        tier_sizes = {
            'free': 1,
            'basic': 1,
            'premium': 2,
            'enterprise': 3
        }

        base_size = tier_sizes.get(request.user_tier, 1)

        # Increase for critical tasks
        if request.task_type in [TaskType.CRISIS_DETECTION, TaskType.TREATMENT_PLANNING]:
            base_size = min(base_size + 1, 4)

        return base_size

    async def _call_provider(self,
                            provider: ProviderConfig,
                            request: ModelRequest) -> ModelResponse:
        """Call a specific provider"""

        start_time = time.time()

        try:
            # Route to appropriate implementation
            if provider.name == 'openai':
                response = await self._call_openai(provider, request)
            elif provider.name == 'ollama':
                response = await self._call_ollama(provider, request)
            elif provider.name == 'custom':
                response = await self._call_custom(provider, request)
            else:
                # Provider not yet implemented
                raise NotImplementedError(f"Provider {provider.name} not implemented")

            # Update health metrics
            self._update_provider_health(provider.name, success=True,
                                        latency=time.time() - start_time)

            return response

        except Exception as e:
            logger.error(f"Error calling {provider.name}: {e}")
            self._update_provider_health(provider.name, success=False, error=str(e))
            raise

    async def _call_openai(self,
                          provider: ProviderConfig,
                          request: ModelRequest) -> ModelResponse:
        """Call OpenAI API"""

        # Use existing AI manager
        response_text = await asyncio.get_event_loop().run_in_executor(
            self.executor,
            self.ai_manager.get_therapeutic_response,
            request.prompt,
            request.context.get('context', '')
        )

        return ModelResponse(
            model_name='gpt-4o',
            provider='openai',
            response=response_text,
            confidence=0.85,  # Default confidence
            latency=time.time(),
            cost=0.003,  # Estimated
            timestamp=datetime.now(),
            session_id=request.context.get('session_id', 'unknown')
        )

    async def _call_ollama(self,
                          provider: ProviderConfig,
                          request: ModelRequest) -> ModelResponse:
        """Call Ollama local model"""

        # Placeholder - would call actual Ollama API
        await asyncio.sleep(0.1)  # Simulate processing

        return ModelResponse(
            model_name='llama2',
            provider='ollama',
            response=f"[Ollama Response] {request.prompt[:100]}...",
            confidence=0.75,
            latency=0.1,
            cost=0.0,
            timestamp=datetime.now(),
            session_id=request.context.get('session_id', 'unknown')
        )

    async def _call_custom(self,
                          provider: ProviderConfig,
                          request: ModelRequest) -> ModelResponse:
        """Call custom model"""

        # Use crisis predictor for crisis detection
        if request.task_type == TaskType.CRISIS_DETECTION:
            result = await self.crisis_predictor.predict_crisis(
                text=request.prompt,
                user_tier='free',
                context=request.context,
                force_free=True
            )

            return ModelResponse(
                model_name='custom_crisis',
                provider='custom',
                response=self._format_crisis_response(result),
                confidence=result.confidence,
                latency=result.latency,
                cost=0.0,
                timestamp=datetime.now(),
                session_id=request.context.get('session_id', 'unknown'),
                crisis_detected=result.is_crisis,
                risk_level=result.severity.value
            )

        # Placeholder for other custom models
        return ModelResponse(
            model_name='custom_model',
            provider='custom',
            response="Custom model response",
            confidence=0.7,
            latency=0.05,
            cost=0.0,
            timestamp=datetime.now(),
            session_id=request.context.get('session_id', 'unknown')
        )

    async def _generate_consensus(self,
                                 responses: List[ModelResponse],
                                 request: ModelRequest) -> str:
        """Generate consensus from multiple model responses"""

        # For now, use simple voting/averaging
        # In production, would use more sophisticated consensus algorithms

        if len(responses) == 1:
            return responses[0].response

        # For crisis detection, use majority vote
        if request.task_type == TaskType.CRISIS_DETECTION:
            crisis_votes = sum(1 for r in responses if r.crisis_detected)
            if crisis_votes > len(responses) / 2:
                return "CONSENSUS: Crisis indicators detected. Immediate intervention recommended."
            else:
                return "CONSENSUS: No immediate crisis detected based on multiple assessments."

        # For other tasks, return highest confidence response
        best_response = max(responses, key=lambda r: r.confidence)
        return best_response.response

    def _create_fallback_response(self, request: ModelRequest) -> ModelEnsembleResponse:
        """Create fallback response when all providers fail"""

        fallback_text = (
            "I'm having trouble processing your request at the moment. "
            "Please try again or contact support if the issue persists."
        )

        return ModelEnsembleResponse(
            primary_response=fallback_text,
            consensus_response=None,
            individual_responses=[],
            total_cost=0.0,
            total_latency=0.0,
            models_used=['fallback'],
            confidence=0.0,
            metadata={
                'error': 'All providers failed',
                'task_type': request.task_type.value
            }
        )

    def _update_provider_health(self,
                               provider_name: str,
                               success: bool,
                               latency: float = 0,
                               error: Optional[str] = None):
        """Update provider health metrics"""

        health = self.provider_health.get(provider_name)
        if not health:
            return

        # Update success rate (exponential moving average)
        alpha = 0.1
        health['success_rate'] = (
            alpha * (1.0 if success else 0.0) +
            (1 - alpha) * health['success_rate']
        )

        # Update latency
        if success and latency > 0:
            health['avg_latency'] = (
                alpha * latency +
                (1 - alpha) * health['avg_latency']
            )

        # Update error tracking
        if not success:
            health['error_count'] += 1
            health['last_error'] = error

        # Update provider status based on health
        if health['success_rate'] < 0.5:
            self.providers[provider_name].status = ProviderStatus.DEGRADED
        elif health['success_rate'] < 0.1:
            self.providers[provider_name].status = ProviderStatus.UNAVAILABLE

    async def train_from_feedback(self,
                                 session_id: str,
                                 feedback: Dict[str, Any]) -> bool:
        """Train models from user feedback"""

        # Update stored responses with feedback
        # This would update the analytics database with ground truth

        logger.info(f"Training from feedback for session {session_id}")

        # Trigger model retraining if enough data
        recommendations = self.analytics.get_model_recommendations('general')

        if recommendations.get('training_progress', {}).get('samples_until_training', 1000) <= 0:
            # Start background training
            asyncio.create_task(self._background_training())

        return True

    async def _background_training(self):
        """Background task for model training"""

        logger.info("Starting background model training...")

        try:
            # Train custom crisis model
            model_path = await self.analytics.train_custom_crisis_model()

            if model_path:
                # Update crisis predictor with new model
                self.crisis_predictor.load_custom_model()
                logger.info(f"New crisis model deployed: {model_path}")

        except Exception as e:
            logger.error(f"Background training failed: {e}")

    async def get_system_report(self) -> Dict[str, Any]:
        """Get comprehensive system report"""

        # Get reports from subsystems
        analytics_report = await self.analytics.generate_model_report()
        crisis_status = self.crisis_predictor.get_system_status()

        # Compile provider status
        provider_status = {}
        for name, provider in self.providers.items():
            health = self.provider_health[name]
            provider_status[name] = {
                'status': provider.status.value,
                'success_rate': health['success_rate'],
                'avg_latency': health['avg_latency'],
                'error_count': health['error_count'],
                'is_available': provider.status == ProviderStatus.AVAILABLE
            }

        return {
            'timestamp': datetime.now().isoformat(),
            'providers': provider_status,
            'crisis_system': crisis_status,
            'analytics': analytics_report,
            'capabilities': {
                'free_tier': ['crisis_detection', 'basic_therapy', 'exercises'],
                'premium_features': list(TaskType.__members__.keys())
            }
        }

# Create singleton instance
ai_orchestrator = AIOrchestrator()