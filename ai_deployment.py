"""
AI Model Deployment Infrastructure
=================================
Handles deployment and management of AI models for MindMend
"""

import os
import json
import requests
import docker
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import subprocess
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelStatus(Enum):
    DOWNLOADING = "downloading"
    READY = "ready"
    ERROR = "error"
    UPDATING = "updating"

@dataclass
class AIModelConfig:
    name: str
    type: str  # ollama, huggingface, custom
    model_id: str
    version: str
    size_gb: float
    specialization: str
    therapy_focus: List[str]
    guardrails_config: Dict
    performance_requirements: Dict

class AIModelDeployment:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.models_dir = Path("/opt/mindmend/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Available models for therapy
        self.therapy_models = {
            "llama2-therapy": AIModelConfig(
                name="llama2-therapy",
                type="ollama",
                model_id="llama2:7b",
                version="latest",
                size_gb=3.8,
                specialization="general_therapy",
                therapy_focus=["general", "anxiety", "depression"],
                guardrails_config={
                    "harmful_content_filter": True,
                    "therapy_boundary_enforcement": True,
                    "crisis_intervention_redirect": True,
                    "personal_info_protection": True
                },
                performance_requirements={
                    "max_response_time": 30,
                    "memory_limit": "4GB",
                    "concurrent_sessions": 10
                }
            ),
            "mistral-counseling": AIModelConfig(
                name="mistral-counseling",
                type="ollama", 
                model_id="mistral:7b",
                version="latest",
                size_gb=4.1,
                specialization="counseling",
                therapy_focus=["cbt", "dbt", "mindfulness"],
                guardrails_config={
                    "harmful_content_filter": True,
                    "therapy_boundary_enforcement": True,
                    "crisis_intervention_redirect": True,
                    "personal_info_protection": True
                },
                performance_requirements={
                    "max_response_time": 25,
                    "memory_limit": "4GB",
                    "concurrent_sessions": 8
                }
            ),
            "codellama-research": AIModelConfig(
                name="codellama-research",
                type="ollama",
                model_id="codellama:7b",
                version="latest", 
                size_gb=3.8,
                specialization="research_analysis",
                therapy_focus=["research", "analysis", "documentation"],
                guardrails_config={
                    "harmful_content_filter": True,
                    "research_accuracy_check": True,
                    "citation_validation": True
                },
                performance_requirements={
                    "max_response_time": 45,
                    "memory_limit": "6GB",
                    "concurrent_sessions": 5
                }
            )
        }
        
        self.model_status = {}
        self.performance_metrics = {}
    
    def check_ollama_status(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models from Ollama"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            if response.status_code == 200:
                return response.json().get('models', [])
            return []
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []
    
    def install_therapy_model(self, model_name: str, progress_callback=None) -> bool:
        """Install a therapy-specific AI model"""
        if model_name not in self.therapy_models:
            logger.error(f"Unknown model: {model_name}")
            return False
        
        model_config = self.therapy_models[model_name]
        self.model_status[model_name] = ModelStatus.DOWNLOADING
        
        try:
            logger.info(f"Installing model: {model_name}")
            
            if model_config.type == "ollama":
                return self._install_ollama_model(model_config, progress_callback)
            elif model_config.type == "huggingface":
                return self._install_huggingface_model(model_config, progress_callback)
            elif model_config.type == "custom":
                return self._install_custom_model(model_config, progress_callback)
            
        except Exception as e:
            logger.error(f"Error installing model {model_name}: {e}")
            self.model_status[model_name] = ModelStatus.ERROR
            return False
    
    def _install_ollama_model(self, config: AIModelConfig, progress_callback=None) -> bool:
        """Install Ollama model"""
        try:
            # Use Docker exec to pull model
            container_name = "mindmend_ollama"
            
            try:
                container = self.docker_client.containers.get(container_name)
            except docker.errors.NotFound:
                logger.error(f"Ollama container {container_name} not found")
                return False
            
            # Execute pull command in container
            command = f"ollama pull {config.model_id}"
            result = container.exec_run(command, stream=True)
            
            for line in result.output:
                if progress_callback:
                    progress_callback(line.decode().strip())
                logger.info(f"Ollama pull: {line.decode().strip()}")
            
            # Check if model was installed successfully
            if self._verify_ollama_model_installed(config.model_id):
                self.model_status[config.name] = ModelStatus.READY
                logger.info(f"Successfully installed model: {config.name}")
                return True
            else:
                self.model_status[config.name] = ModelStatus.ERROR
                return False
                
        except Exception as e:
            logger.error(f"Error installing Ollama model: {e}")
            self.model_status[config.name] = ModelStatus.ERROR
            return False
    
    def _verify_ollama_model_installed(self, model_id: str) -> bool:
        """Verify Ollama model is installed"""
        try:
            available_models = self.get_available_models()
            return any(model['name'].startswith(model_id) for model in available_models)
        except:
            return False
    
    def _install_huggingface_model(self, config: AIModelConfig, progress_callback=None) -> bool:
        """Install Hugging Face model"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            model_path = self.models_dir / config.name
            model_path.mkdir(exist_ok=True)
            
            if progress_callback:
                progress_callback(f"Downloading tokenizer for {config.name}")
            
            # Download tokenizer
            tokenizer = AutoTokenizer.from_pretrained(config.model_id)
            tokenizer.save_pretrained(str(model_path))
            
            if progress_callback:
                progress_callback(f"Downloading model for {config.name}")
            
            # Download model
            model = AutoModelForCausalLM.from_pretrained(
                config.model_id,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            model.save_pretrained(str(model_path))
            
            self.model_status[config.name] = ModelStatus.READY
            logger.info(f"Successfully installed Hugging Face model: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error installing Hugging Face model: {e}")
            self.model_status[config.name] = ModelStatus.ERROR
            return False
    
    def _install_custom_model(self, config: AIModelConfig, progress_callback=None) -> bool:
        """Install custom model"""
        # Placeholder for custom model installation
        # This would be implemented based on specific custom model requirements
        logger.info(f"Custom model installation not yet implemented: {config.name}")
        return False
    
    def configure_model_guardrails(self, model_name: str) -> bool:
        """Configure safety guardrails for therapy models"""
        if model_name not in self.therapy_models:
            return False
        
        config = self.therapy_models[model_name]
        guardrails_config = {
            "model_name": model_name,
            "filters": {
                "harmful_content": config.guardrails_config.get("harmful_content_filter", False),
                "therapy_boundaries": config.guardrails_config.get("therapy_boundary_enforcement", False),
                "crisis_intervention": config.guardrails_config.get("crisis_intervention_redirect", False),
                "privacy_protection": config.guardrails_config.get("personal_info_protection", False)
            },
            "response_validation": {
                "max_length": 2000,
                "inappropriate_content_check": True,
                "therapeutic_appropriateness": True
            },
            "emergency_protocols": {
                "crisis_keywords": [
                    "suicide", "kill myself", "end it all", "want to die",
                    "hurt myself", "self harm", "not worth living"
                ],
                "escalation_contacts": [
                    {"service": "Lifeline", "number": "13 11 14", "region": "AU"}
                ]
            }
        }
        
        # Save guardrails configuration
        guardrails_file = self.models_dir / f"{model_name}_guardrails.json"
        with open(guardrails_file, 'w') as f:
            json.dump(guardrails_config, f, indent=2)
        
        logger.info(f"Configured guardrails for model: {model_name}")
        return True
    
    def get_model_performance_metrics(self, model_name: str) -> Dict:
        """Get performance metrics for a model"""
        if model_name not in self.performance_metrics:
            self.performance_metrics[model_name] = {
                "total_requests": 0,
                "average_response_time": 0,
                "error_rate": 0,
                "last_updated": time.time()
            }
        
        return self.performance_metrics[model_name]
    
    def update_model_metrics(self, model_name: str, response_time: float, error: bool = False):
        """Update performance metrics for a model"""
        if model_name not in self.performance_metrics:
            self.performance_metrics[model_name] = {
                "total_requests": 0,
                "average_response_time": 0,
                "error_rate": 0,
                "errors": 0,
                "last_updated": time.time()
            }
        
        metrics = self.performance_metrics[model_name]
        metrics["total_requests"] += 1
        
        # Update average response time
        current_avg = metrics["average_response_time"]
        total_requests = metrics["total_requests"]
        metrics["average_response_time"] = (current_avg * (total_requests - 1) + response_time) / total_requests
        
        # Update error rate
        if error:
            metrics["errors"] = metrics.get("errors", 0) + 1
        
        metrics["error_rate"] = metrics.get("errors", 0) / total_requests * 100
        metrics["last_updated"] = time.time()
    
    def install_all_therapy_models(self, progress_callback=None) -> Dict[str, bool]:
        """Install all therapy models"""
        results = {}
        
        for model_name in self.therapy_models:
            if progress_callback:
                progress_callback(f"Installing {model_name}...")
            
            success = self.install_therapy_model(model_name, progress_callback)
            results[model_name] = success
            
            if success:
                self.configure_model_guardrails(model_name)
        
        return results
    
    def get_deployment_status(self) -> Dict:
        """Get overall deployment status"""
        return {
            "ollama_running": self.check_ollama_status(),
            "models_status": self.model_status,
            "available_models": self.get_available_models(),
            "performance_metrics": self.performance_metrics,
            "models_directory": str(self.models_dir)
        }

# Global deployment manager instance
ai_deployment = AIModelDeployment()