# SDK Code Transformation Guide

**Project:** MindMend Gemini Migration
**Purpose:** Before/after code examples for OpenAI → Gemini migration
**Date:** 2025-10-10

---

## Overview

This document provides concrete code examples showing how to transform OpenAI API calls to Vertex AI (Gemini) equivalents. Each example includes:

1. **Before:** Current OpenAI implementation
2. **After:** New Gemini implementation
3. **Notes:** Key differences and migration tips

---

## Table of Contents

1. [Basic Setup & Authentication](#1-basic-setup--authentication)
2. [Simple Text Generation](#2-simple-text-generation)
3. [Streaming Responses](#3-streaming-responses)
4. [System Prompts & Context](#4-system-prompts--context)
5. [Temperature & Sampling Parameters](#5-temperature--sampling-parameters)
6. [Error Handling](#6-error-handling)
7. [Abstraction Layer Implementation](#7-abstraction-layer-implementation)
8. [Flask Route Migration](#8-flask-route-migration)
9. [Async Operations](#9-async-operations)
10. [Cost & Token Management](#10-cost--token-management)

---

## 1. Basic Setup & Authentication

### Before (OpenAI)

```python
import openai
import os

# Authentication via API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Alternative: using client object
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

### After (Vertex AI / Gemini)

```python
import vertexai
from vertexai.generative_models import GenerativeModel
import os

# Authentication via Workload Identity (GKE) or Application Default Credentials
# No explicit API key needed if running on GCP

# Initialize Vertex AI
vertexai.init(
    project=os.getenv("VERTEX_AI_PROJECT", "mindmend-production"),
    location=os.getenv("VERTEX_AI_LOCATION", "australia-southeast1")
)

# Create model instance
model = GenerativeModel("gemini-1.5-pro")
```

### Notes

- **Authentication:**
  - OpenAI uses API keys (explicit credentials)
  - Gemini uses Workload Identity or ADC (implicit credentials)
  - No secrets in code for Gemini when running on GKE

- **Initialization:**
  - OpenAI is global or per-client
  - Gemini requires project + location initialization

- **Model Selection:**
  - OpenAI: `gpt-3.5-turbo`, `gpt-4`
  - Gemini: `gemini-1.5-pro`, `gemini-1.5-flash`

---

## 2. Simple Text Generation

### Before (OpenAI)

```python
import openai

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful therapist."},
        {"role": "user", "content": "I feel anxious today."}
    ]
)

ai_response = response.choices[0].message.content
print(ai_response)
```

### After (Vertex AI / Gemini)

```python
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="mindmend-production", location="australia-southeast1")
model = GenerativeModel("gemini-1.5-pro")

# Gemini doesn't have separate system/user roles
# Combine system prompt with user message
prompt = """You are a helpful therapist.

User: I feel anxious today."""

response = model.generate_content(prompt)
ai_response = response.text
print(ai_response)
```

### Alternative (Gemini with Chat)

```python
from vertexai.generative_models import GenerativeModel

model = GenerativeModel(
    "gemini-1.5-pro",
    system_instruction="You are a helpful therapist."  # System instruction
)

chat = model.start_chat()
response = chat.send_message("I feel anxious today.")
ai_response = response.text
print(ai_response)
```

### Notes

- **Message Format:**
  - OpenAI uses structured message array with roles
  - Gemini uses freeform text or chat sessions
  - System prompts: OpenAI has explicit system role, Gemini uses `system_instruction` parameter

- **Response Access:**
  - OpenAI: `response.choices[0].message.content`
  - Gemini: `response.text`

- **Chat Sessions:**
  - OpenAI: Stateless, pass full history each time
  - Gemini: Stateful chat sessions available via `start_chat()`

---

## 3. Streaming Responses

### Before (OpenAI)

```python
import openai

stream = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Tell me about anxiety."}
    ],
    stream=True  # Enable streaming
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        content = chunk.choices[0].delta.content
        print(content, end="", flush=True)
```

### After (Vertex AI / Gemini)

```python
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="mindmend-production", location="australia-southeast1")
model = GenerativeModel("gemini-1.5-pro")

# Enable streaming with stream=True
response_stream = model.generate_content(
    "Tell me about anxiety.",
    stream=True  # Enable streaming
)

for chunk in response_stream:
    print(chunk.text, end="", flush=True)
```

### Notes

- **Streaming API:**
  - Both support streaming responses
  - OpenAI yields delta chunks
  - Gemini yields complete text chunks (not deltas)

- **Chunk Access:**
  - OpenAI: `chunk.choices[0].delta.content`
  - Gemini: `chunk.text`

- **Use Cases:**
  - Critical for real-time therapy conversations
  - Improves perceived latency
  - Enables progressive UI updates

---

## 4. System Prompts & Context

### Before (OpenAI)

```python
import openai

# System prompt as separate message
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": """You are MindMend, an empathetic AI therapist.
Your role is to provide supportive, evidence-based mental health guidance.
Always validate the user's feelings and suggest coping strategies."""
        },
        {"role": "user", "content": "I'm feeling overwhelmed."}
    ]
)
```

### After (Vertex AI / Gemini) - Option 1: Inline

```python
from vertexai.generative_models import GenerativeModel

model = GenerativeModel("gemini-1.5-pro")

# Combine system prompt with user message
full_prompt = """You are MindMend, an empathetic AI therapist.
Your role is to provide supportive, evidence-based mental health guidance.
Always validate the user's feelings and suggest coping strategies.

User: I'm feeling overwhelmed."""

response = model.generate_content(full_prompt)
```

### After (Vertex AI / Gemini) - Option 2: System Instruction

```python
from vertexai.generative_models import GenerativeModel

# System instruction as model parameter (recommended)
model = GenerativeModel(
    "gemini-1.5-pro",
    system_instruction="""You are MindMend, an empathetic AI therapist.
Your role is to provide supportive, evidence-based mental health guidance.
Always validate the user's feelings and suggest coping strategies."""
)

# User message only
response = model.generate_content("I'm feeling overwhelmed.")
```

### After (Vertex AI / Gemini) - Option 3: Chat with History

```python
from vertexai.generative_models import GenerativeModel, Content, Part

model = GenerativeModel(
    "gemini-1.5-pro",
    system_instruction="You are MindMend, an empathetic AI therapist."
)

# Start chat with history
chat = model.start_chat(
    history=[
        Content(role="user", parts=[Part.from_text("Hello")]),
        Content(role="model", parts=[Part.from_text("Hello! How are you feeling today?")])
    ]
)

# Continue conversation
response = chat.send_message("I'm feeling overwhelmed.")
```

### Notes

- **System Prompts:**
  - OpenAI: Explicit system role in messages array
  - Gemini: Use `system_instruction` parameter (preferred) or inline in prompt

- **Context Management:**
  - OpenAI: Pass full message history each time
  - Gemini: Use chat sessions for stateful conversations

- **Best Practice for Gemini:**
  - Use `system_instruction` for persistent persona
  - Use chat history for multi-turn conversations
  - Inline system prompts for one-off completions

---

## 5. Temperature & Sampling Parameters

### Before (OpenAI)

```python
import openai

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Generate therapy exercises"}],
    temperature=0.8,           # Creativity (0-2)
    max_tokens=1000,           # Max output length
    top_p=0.9,                 # Nucleus sampling
    frequency_penalty=0.0,     # Penalize repetition
    presence_penalty=0.0       # Penalize reusing topics
)
```

### After (Vertex AI / Gemini)

```python
from vertexai.generative_models import GenerativeModel, GenerationConfig

model = GenerativeModel("gemini-1.5-pro")

generation_config = GenerationConfig(
    temperature=0.8,           # Creativity (0-2)
    max_output_tokens=1000,    # Max output length (note: max_OUTPUT_tokens)
    top_p=0.9,                 # Nucleus sampling
    top_k=40,                  # NEW: Top-K sampling (Gemini-specific)
    # NOTE: No frequency_penalty or presence_penalty in Gemini
)

response = model.generate_content(
    "Generate therapy exercises",
    generation_config=generation_config
)
```

### Parameter Mapping Table

| OpenAI Parameter | Gemini Parameter | Notes |
|-----------------|------------------|-------|
| `temperature` | `temperature` | Direct mapping (0-2) |
| `max_tokens` | `max_output_tokens` | Different name, same concept |
| `top_p` | `top_p` | Direct mapping |
| N/A | `top_k` | NEW in Gemini, controls diversity |
| `frequency_penalty` | N/A | **Not available in Gemini** |
| `presence_penalty` | N/A | **Not available in Gemini** |
| `n` (num completions) | `candidate_count` | Multiple candidates |
| `stop` | `stop_sequences` | Stop generation tokens |

### Notes

- **Missing Parameters:**
  - Gemini does NOT support `frequency_penalty` or `presence_penalty`
  - Use higher `top_k` (e.g., 60-80) to reduce repetition

- **New Parameters:**
  - `top_k`: Limits vocabulary to top K tokens (default: 40)
  - Useful for more controlled generation

- **Output Length:**
  - OpenAI: `max_tokens` (input + output)
  - Gemini: `max_output_tokens` (output only)

---

## 6. Error Handling

### Before (OpenAI)

```python
import openai
from openai.error import (
    RateLimitError,
    APIError,
    InvalidRequestError,
    AuthenticationError
)

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )
    return response.choices[0].message.content

except RateLimitError:
    print("Rate limit exceeded. Retry with backoff.")
    raise

except AuthenticationError:
    print("Invalid API key.")
    raise

except InvalidRequestError as e:
    print(f"Invalid request: {e}")
    raise

except APIError as e:
    print(f"API error: {e}")
    raise
```

### After (Vertex AI / Gemini)

```python
from vertexai.generative_models import GenerativeModel
from google.api_core import exceptions as google_exceptions
from google.api_core import retry

model = GenerativeModel("gemini-1.5-pro")

try:
    response = model.generate_content("Hello")
    return response.text

except google_exceptions.ResourceExhausted:
    # Rate limit / quota exceeded
    print("Quota exceeded. Retry with backoff.")
    raise

except google_exceptions.PermissionDenied:
    # Authentication / IAM issue
    print("Permission denied. Check IAM roles.")
    raise

except google_exceptions.InvalidArgument as e:
    # Invalid request parameters
    print(f"Invalid argument: {e}")
    raise

except google_exceptions.DeadlineExceeded:
    # Timeout
    print("Request timeout. Consider shorter prompts.")
    raise

except google_exceptions.GoogleAPICallError as e:
    # General API error
    print(f"API error: {e}")
    raise
```

### With Automatic Retry

```python
from google.api_core import retry

# Configure retry policy
retry_policy = retry.Retry(
    initial=1.0,           # Initial delay (seconds)
    maximum=60.0,          # Max delay (seconds)
    multiplier=2.0,        # Exponential backoff
    predicate=retry.if_exception_type(
        google_exceptions.ResourceExhausted,
        google_exceptions.ServiceUnavailable,
        google_exceptions.DeadlineExceeded
    )
)

# Apply retry to generate_content
response = model.generate_content(
    "Hello",
    retry=retry_policy
)
```

### Error Mapping Table

| OpenAI Exception | Gemini Exception | Meaning |
|-----------------|------------------|---------|
| `RateLimitError` | `ResourceExhausted` | Quota exceeded |
| `AuthenticationError` | `PermissionDenied` | Auth failure |
| `InvalidRequestError` | `InvalidArgument` | Bad parameters |
| `APIError` | `GoogleAPICallError` | General API error |
| `Timeout` | `DeadlineExceeded` | Request timeout |
| `ServiceUnavailableError` | `ServiceUnavailable` | Service down |

### Notes

- **Import Statements:**
  - OpenAI: `from openai.error import ...`
  - Gemini: `from google.api_core import exceptions`

- **Retry Logic:**
  - OpenAI: Implement manually
  - Gemini: Built-in retry decorators available

- **Quota Management:**
  - OpenAI: Rate limits per API key
  - Gemini: Quotas per project per region

---

## 7. Abstraction Layer Implementation

### Complete Abstraction Layer

```python
"""
models/ai_provider.py
Unified AI provider interface supporting OpenAI and Gemini
"""

import os
from typing import Optional, Iterator, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    OPENAI = "openai"
    GEMINI = "gemini"

class AIModelClient:
    """
    Unified interface for AI model calls.
    Routes to OpenAI or Gemini based on AI_PROVIDER environment variable.
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = AIProvider(provider or os.getenv("AI_PROVIDER", "openai"))
        logger.info(f"Initializing AI client with provider: {self.provider.value}")

        if self.provider == AIProvider.OPENAI:
            self._init_openai()
        elif self.provider == AIProvider.GEMINI:
            self._init_gemini()

    def _init_openai(self):
        """Initialize OpenAI client."""
        import openai
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = "gpt-3.5-turbo"
        logger.info("OpenAI client initialized")

    def _init_gemini(self):
        """Initialize Vertex AI / Gemini client."""
        import vertexai
        from vertexai.generative_models import GenerativeModel

        project = os.getenv("VERTEX_AI_PROJECT", "mindmend-production")
        location = os.getenv("VERTEX_AI_LOCATION", "australia-southeast1")

        vertexai.init(project=project, location=location)
        self.client = GenerativeModel("gemini-1.5-pro")
        self.model_name = "gemini-1.5-pro"
        logger.info(f"Gemini client initialized (project={project}, location={location})")

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
        stream: bool = False,
        **kwargs
    ) -> str | Iterator[str]:
        """
        Generate text using configured provider.

        Args:
            prompt: User input
            system_prompt: System instructions
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum output tokens
            stream: Whether to stream response
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text or stream iterator
        """

        try:
            if self.provider == AIProvider.OPENAI:
                return self._generate_openai(
                    prompt, system_prompt, temperature, max_tokens, stream, **kwargs
                )
            elif self.provider == AIProvider.GEMINI:
                return self._generate_gemini(
                    prompt, system_prompt, temperature, max_tokens, stream, **kwargs
                )
        except Exception as e:
            logger.error(f"AI generation failed: {e}", exc_info=True)
            raise

    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        stream: bool,
        **kwargs
    ) -> str | Iterator[str]:
        """OpenAI implementation."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model_name),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=kwargs.get("top_p", 1.0),
            stream=stream
        )

        if stream:
            def stream_generator():
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            return stream_generator()
        else:
            return response.choices[0].message.content

    def _generate_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        stream: bool,
        **kwargs
    ) -> str | Iterator[str]:
        """Gemini implementation."""
        from vertexai.generative_models import GenerationConfig, GenerativeModel

        # If system prompt provided, use it as system instruction
        if system_prompt and not hasattr(self.client, '_system_instruction'):
            # Recreate model with system instruction
            self.client = GenerativeModel(
                self.model_name,
                system_instruction=system_prompt
            )

        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            top_p=kwargs.get("top_p", 0.9),
            top_k=kwargs.get("top_k", 40),
        )

        response = self.client.generate_content(
            prompt,
            generation_config=generation_config,
            stream=stream
        )

        if stream:
            def stream_generator():
                for chunk in response:
                    yield chunk.text
            return stream_generator()
        else:
            return response.text

# Convenience function
def get_ai_client(provider: Optional[str] = None) -> AIModelClient:
    """Get AI client instance."""
    return AIModelClient(provider)
```

### Usage in Application

```python
# Before: Direct OpenAI usage
import openai
response = openai.ChatCompletion.create(...)

# After: Using abstraction
from models.ai_provider import get_ai_client

client = get_ai_client()  # Uses AI_PROVIDER env var
response = client.generate_text(
    prompt="I feel anxious",
    system_prompt="You are a therapist",
    temperature=0.7,
    stream=False
)
```

---

## 8. Flask Route Migration

### Before (OpenAI)

```python
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/api/therapy-session', methods=['POST'])
def therapy_session():
    """Main therapy chat endpoint."""
    data = request.get_json()
    message = data.get('message')
    session_id = data.get('session_id')

    if not message:
        return jsonify({"error": "Message required"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an empathetic therapist specializing in CBT."
                },
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        ai_response = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        return jsonify({
            "response": ai_response,
            "session_id": session_id,
            "tokens_used": tokens_used
        })

    except openai.error.RateLimitError:
        return jsonify({"error": "Rate limit exceeded"}), 429

    except Exception as e:
        app.logger.error(f"Therapy session error: {e}")
        return jsonify({"error": "Internal server error"}), 500
```

### After (Gemini with Abstraction)

```python
from flask import Flask, request, jsonify
from models.ai_provider import get_ai_client
from google.api_core import exceptions as google_exceptions

app = Flask(__name__)

@app.route('/api/therapy-session', methods=['POST'])
def therapy_session():
    """Main therapy chat endpoint."""
    data = request.get_json()
    message = data.get('message')
    session_id = data.get('session_id')

    if not message:
        return jsonify({"error": "Message required"}), 400

    try:
        # Get AI client (provider determined by AI_PROVIDER env var)
        ai_client = get_ai_client()

        # Generate response
        ai_response = ai_client.generate_text(
            prompt=message,
            system_prompt="You are an empathetic therapist specializing in CBT.",
            temperature=0.7,
            max_tokens=1500,
            stream=False
        )

        return jsonify({
            "response": ai_response,
            "session_id": session_id,
            "provider": ai_client.provider.value
        })

    except google_exceptions.ResourceExhausted:
        return jsonify({"error": "Rate limit exceeded"}), 429

    except google_exceptions.PermissionDenied:
        app.logger.error("Vertex AI permission denied. Check IAM roles.")
        return jsonify({"error": "Configuration error"}), 500

    except Exception as e:
        app.logger.error(f"Therapy session error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
```

### Streaming Response Endpoint

```python
from flask import Flask, Response, stream_with_context
from models.ai_provider import get_ai_client

@app.route('/api/therapy-session-stream', methods=['POST'])
def therapy_session_stream():
    """Streaming therapy chat endpoint."""
    data = request.get_json()
    message = data.get('message')

    if not message:
        return jsonify({"error": "Message required"}), 400

    def generate():
        """Stream generator for SSE."""
        try:
            ai_client = get_ai_client()

            # Get streaming response
            stream = ai_client.generate_text(
                prompt=message,
                system_prompt="You are an empathetic therapist.",
                temperature=0.7,
                stream=True
            )

            # Yield each chunk as SSE
            for chunk in stream:
                yield f"data: {chunk}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            app.logger.error(f"Streaming error: {e}", exc_info=True)
            yield f"data: {{'error': 'Stream failed'}}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream"
    )
```

### Notes

- **Abstraction Benefits:**
  - Single code path for both providers
  - Toggle via environment variable
  - No code changes required to switch

- **Error Handling:**
  - Update exception types for Gemini
  - Log provider name for debugging

- **Streaming:**
  - Both providers support SSE streaming
  - Same Flask Response pattern works for both

---

## 9. Async Operations

### Before (OpenAI with asyncio)

```python
import asyncio
import openai

async def generate_multiple_responses(prompts: list[str]) -> list[str]:
    """Generate responses for multiple prompts concurrently."""

    async def generate_one(prompt: str) -> str:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    tasks = [generate_one(p) for p in prompts]
    responses = await asyncio.gather(*tasks)
    return responses

# Usage
prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
responses = asyncio.run(generate_multiple_responses(prompts))
```

### After (Gemini with asyncio)

```python
import asyncio
from vertexai.generative_models import GenerativeModel

async def generate_multiple_responses(prompts: list[str]) -> list[str]:
    """Generate responses for multiple prompts concurrently."""

    model = GenerativeModel("gemini-1.5-pro")

    async def generate_one(prompt: str) -> str:
        # Gemini SDK doesn't have native async, use thread executor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            model.generate_content,
            prompt
        )
        return response.text

    tasks = [generate_one(p) for p in prompts]
    responses = await asyncio.gather(*tasks)
    return responses

# Usage
prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
responses = asyncio.run(generate_multiple_responses(prompts))
```

### Notes

- **Async Support:**
  - OpenAI: Native async with `acreate()` methods
  - Gemini: No native async, use `run_in_executor()`

- **Concurrency:**
  - Both support concurrent requests
  - Respect rate limits when batching

---

## 10. Cost & Token Management

### Before (OpenAI)

```python
import openai

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)

# Access usage information
tokens_used = response.usage.total_tokens
prompt_tokens = response.usage.prompt_tokens
completion_tokens = response.usage.completion_tokens

# Calculate cost (gpt-3.5-turbo pricing)
cost = (prompt_tokens * 0.0015 / 1000) + (completion_tokens * 0.002 / 1000)
print(f"Cost: ${cost:.6f}")
```

### After (Gemini)

```python
from vertexai.generative_models import GenerativeModel

model = GenerativeModel("gemini-1.5-pro")
response = model.generate_content("Hello")

# Gemini usage metadata
usage_metadata = response.usage_metadata
prompt_tokens = usage_metadata.prompt_token_count
completion_tokens = usage_metadata.candidates_token_count
total_tokens = usage_metadata.total_token_count

# Calculate cost (gemini-1.5-pro pricing - australia-southeast1)
# Input: $0.00125 / 1K tokens
# Output: $0.005 / 1K tokens
cost = (prompt_tokens * 0.00125 / 1000) + (completion_tokens * 0.005 / 1000)
print(f"Cost: ${cost:.6f}")
```

### Token Management Table

| Provider | Input ($/1K) | Output ($/1K) | Max Tokens |
|----------|-------------|---------------|------------|
| GPT-3.5 Turbo | $0.0015 | $0.002 | 4K / 16K |
| GPT-4 | $0.03 | $0.06 | 8K / 128K |
| Gemini 1.5 Flash | $0.000125 | $0.000375 | 1M |
| Gemini 1.5 Pro | $0.00125 | $0.005 | 2M |

### Notes

- **Cost Tracking:**
  - Both provide token usage metadata
  - Calculate costs using current pricing

- **Token Limits:**
  - Gemini supports much larger contexts (1M-2M tokens)
  - OpenAI: 4K-128K depending on model

- **Cost Optimization:**
  - Use Gemini Flash for simple tasks (10x cheaper)
  - Use Gemini Pro for complex reasoning
  - Implement response caching where possible

---

## Migration Checklist

Use this checklist when migrating each AI-powered endpoint:

- [ ] Replace OpenAI imports with abstraction layer
- [ ] Update message format (system prompt handling)
- [ ] Adjust parameter names (`max_tokens` → `max_output_tokens`)
- [ ] Update error handling (OpenAI exceptions → Google exceptions)
- [ ] Test streaming responses if applicable
- [ ] Verify token usage tracking
- [ ] Update logging and monitoring
- [ ] Add feature flag support (`AI_PROVIDER` env var)
- [ ] Write unit tests for both providers
- [ ] Document any provider-specific behavior

---

## Testing Strategy

### Unit Test Template

```python
import pytest
from models.ai_provider import AIModelClient, AIProvider

@pytest.fixture
def openai_client():
    return AIModelClient(provider="openai")

@pytest.fixture
def gemini_client():
    return AIModelClient(provider="gemini")

@pytest.mark.parametrize("client_fixture", ["openai_client", "gemini_client"])
def test_generate_text(client_fixture, request):
    """Test text generation for both providers."""
    client = request.getfixturevalue(client_fixture)

    response = client.generate_text(
        prompt="Hello",
        system_prompt="You are helpful.",
        temperature=0.7,
        max_tokens=100
    )

    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.parametrize("client_fixture", ["openai_client", "gemini_client"])
def test_streaming(client_fixture, request):
    """Test streaming for both providers."""
    client = request.getfixturevalue(client_fixture)

    stream = client.generate_text(
        prompt="Count to 5",
        stream=True
    )

    chunks = list(stream)
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)
```

---

## Common Pitfalls

### 1. System Prompt Handling

**Problem:** Gemini doesn't have explicit system role in messages array.

**Solution:**
- Use `system_instruction` parameter when creating model
- Or prepend system prompt to user message
- Don't pass system prompt as separate message

### 2. Token Counting

**Problem:** Different token counting methods.

**Solution:**
- OpenAI: `response.usage.total_tokens`
- Gemini: `response.usage_metadata.total_token_count`
- Update all token tracking code

### 3. Streaming Chunks

**Problem:** Chunk format differs between providers.

**Solution:**
- OpenAI: Delta chunks (incremental)
- Gemini: Full text chunks
- Handle accordingly in UI

### 4. Error Types

**Problem:** Different exception hierarchies.

**Solution:**
- Use abstraction layer to normalize errors
- Or handle both exception types explicitly

### 5. Rate Limits

**Problem:** Different rate limit structures.

**Solution:**
- OpenAI: Per-key limits
- Gemini: Per-project per-region quotas
- Implement retry with exponential backoff for both

---

## Next Steps

After reviewing these examples:

1. **Start Migration:**
   - Create abstraction layer (`models/ai_provider.py`)
   - Add feature flag configuration
   - Update one route at a time

2. **Test Thoroughly:**
   - Unit tests for abstraction layer
   - Integration tests for each route
   - Golden prompt evaluation

3. **Monitor Performance:**
   - Compare latency between providers
   - Track token usage and costs
   - Monitor error rates

4. **Optimize:**
   - Choose appropriate model (Pro vs Flash)
   - Tune sampling parameters
   - Implement caching where possible

---

**Status:** Ready for implementation
**Last Updated:** 2025-10-10
**Version:** 1.0
