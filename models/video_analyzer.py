import base64
import json
import logging
import os
from datetime import datetime
from openai import OpenAI

class VideoAnalyzer:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "demo-key"))
        
        # Emotion categories and their indicators
        self.emotion_categories = {
            "happiness": {"indicators": ["smile", "bright eyes", "relaxed features"], "color": "#28a745"},
            "sadness": {"indicators": ["downturned mouth", "droopy eyes", "furrowed brow"], "color": "#6c757d"},
            "anger": {"indicators": ["tense jaw", "narrowed eyes", "tight lips"], "color": "#dc3545"},
            "fear": {"indicators": ["wide eyes", "raised eyebrows", "tense expression"], "color": "#ffc107"},
            "surprise": {"indicators": ["raised eyebrows", "wide eyes", "open mouth"], "color": "#17a2b8"},
            "disgust": {"indicators": ["wrinkled nose", "curled lip", "squinted eyes"], "color": "#6f42c1"},
            "anxiety": {"indicators": ["tense muscles", "fidgeting", "rapid blinking"], "color": "#fd7e14"},
            "stress": {"indicators": ["tight jaw", "tense forehead", "shallow breathing"], "color": "#e83e8c"},
            "neutral": {"indicators": ["relaxed expression", "steady gaze"], "color": "#007bff"}
        }
        
        # Microexpression indicators
        self.microexpressions = {
            "concealed_emotion": {"indicators": ["brief facial changes", "asymmetrical expressions"], "duration": "< 0.5s"},
            "deception": {"indicators": ["incongruent expressions", "delayed responses"], "duration": "< 1s"},
            "suppressed_feelings": {"indicators": ["partial expressions", "quick recoveries"], "duration": "< 0.3s"},
            "emotional_conflict": {"indicators": ["mixed expressions", "rapid changes"], "duration": "< 1s"},
            "masked_distress": {"indicators": ["forced smile", "tight eyes"], "duration": "< 0.5s"}
        }
        
        # Stress indicators
        self.stress_indicators = {
            "physiological": ["increased blinking", "jaw tension", "forehead wrinkles"],
            "behavioral": ["fidgeting", "avoiding eye contact", "repetitive movements"],
            "vocal": ["pitch changes", "speech hesitation", "volume variations"]
        }
    
    def analyze_frame(self, frame_data):
        """Analyze a video frame for emotions and microexpressions"""
        try:
            if not frame_data:
                return {"error": "No frame data provided"}
            
            # Use OpenAI Vision API for facial analysis
            analysis = self._analyze_with_openai_vision(frame_data)
            
            # Combine with rule-based analysis
            enhanced_analysis = self._enhance_analysis(analysis)
            
            # Add stress level calculation
            stress_level = self._calculate_stress_level(enhanced_analysis)
            
            return {
                "emotions": enhanced_analysis.get("emotions", {}),
                "primary_emotion": self._get_primary_emotion(enhanced_analysis.get("emotions", {})),
                "microexpressions": enhanced_analysis.get("microexpressions", {}),
                "facial_landmarks": enhanced_analysis.get("facial_landmarks", {}),
                "eye_contact": enhanced_analysis.get("eye_contact", "unknown"),
                "engagement_level": enhanced_analysis.get("engagement_level", 0.5),
                "stress_level": stress_level,
                "confidence": enhanced_analysis.get("confidence", 0),
                "recommendations": self._generate_recommendations(enhanced_analysis, stress_level),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Video analysis error: {e}")
            return self._fallback_analysis()
    
    def _analyze_with_openai_vision(self, frame_data):
        """Use OpenAI Vision API for comprehensive facial analysis"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert in facial expression analysis and microexpression detection for therapeutic purposes.
                        Analyze the image for:
                        1. Primary emotions (happiness, sadness, anger, fear, surprise, disgust, anxiety, stress, neutral)
                        2. Microexpressions and brief facial changes
                        3. Eye contact and gaze patterns
                        4. Engagement level (0-1 scale)
                        5. Stress indicators
                        6. Overall confidence in analysis
                        
                        Respond in JSON format with emotion scores (0-1), confidence levels, and detailed observations.
                        Be therapeutic and supportive in your analysis."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please analyze this facial expression for therapeutic insights including emotions, microexpressions, stress indicators, and engagement level."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{frame_data}"}
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"OpenAI Vision API error: {e}")
            return self._fallback_analysis()
    
    def _enhance_analysis(self, openai_analysis):
        """Enhance OpenAI analysis with additional processing"""
        enhanced = openai_analysis.copy()
        
        # Ensure emotions is a dictionary with float values
        emotions = enhanced.get("emotions", {})
        if not isinstance(emotions, dict):
            emotions = {"neutral": 0.8}
        
        # Normalize emotion scores
        normalized_emotions = {}
        for emotion, score in emotions.items():
            if isinstance(score, (int, float)):
                normalized_emotions[emotion] = max(0, min(1, float(score)))
            else:
                normalized_emotions[emotion] = 0.5
        
        enhanced["emotions"] = normalized_emotions
        
        # Calculate emotional complexity
        emotion_count = sum(1 for score in normalized_emotions.values() if score > 0.3)
        enhanced["emotional_complexity"] = emotion_count
        
        # Detect emotional inconsistencies
        enhanced["emotional_conflict"] = self._detect_emotional_inconsistency(normalized_emotions)
        
        # Add engagement level if missing
        if "engagement_level" not in enhanced:
            enhanced["engagement_level"] = self._calculate_engagement_level(normalized_emotions)
        
        # Add eye contact assessment if missing
        if "eye_contact" not in enhanced:
            enhanced["eye_contact"] = self._assess_eye_contact(enhanced)
        
        return enhanced
    
    def _get_primary_emotion(self, emotions):
        """Get the primary emotion from emotion scores"""
        if not emotions:
            return "neutral"
        
        primary = max(emotions.keys(), key=lambda k: emotions.get(k, 0))
        return primary if emotions.get(primary, 0) > 0.3 else "neutral"
    
    def _detect_emotional_inconsistency(self, emotions):
        """Detect conflicting emotional expressions"""
        positive_emotions = ["happiness", "surprise"]
        negative_emotions = ["sadness", "anger", "fear", "disgust", "anxiety", "stress"]
        
        positive_score = sum(emotions.get(emotion, 0) for emotion in positive_emotions)
        negative_score = sum(emotions.get(emotion, 0) for emotion in negative_emotions)
        
        # If both positive and negative emotions are high, there's inconsistency
        return positive_score > 0.5 and negative_score > 0.5
    
    def _calculate_stress_level(self, analysis):
        """Calculate overall stress level from analysis"""
        emotions = analysis.get("emotions", {})
        stress_emotions = ["anxiety", "fear", "anger", "stress"]
        
        stress_score = sum(emotions.get(emotion, 0) for emotion in stress_emotions)
        
        # Add baseline stress from sadness and other indicators
        stress_score += emotions.get("sadness", 0) * 0.5
        stress_score += emotions.get("disgust", 0) * 0.3
        
        # Consider microexpressions
        microexpressions = analysis.get("microexpressions", {})
        if isinstance(microexpressions, dict):
            for micro_type, micro_data in microexpressions.items():
                if micro_type in ["suppressed_feelings", "masked_distress"]:
                    stress_score += 0.2
        
        # Consider engagement level (low engagement might indicate stress)
        engagement = analysis.get("engagement_level", 0.5)
        if engagement < 0.3:
            stress_score += 0.2
        
        return min(stress_score, 1.0)
    
    def _calculate_engagement_level(self, emotions):
        """Calculate engagement level from emotions"""
        engaging_emotions = ["happiness", "surprise", "anger"]  # Active emotions
        disengaging_emotions = ["sadness", "fear", "neutral"]   # Passive emotions
        
        engaging_score = sum(emotions.get(emotion, 0) for emotion in engaging_emotions)
        disengaging_score = sum(emotions.get(emotion, 0) for emotion in disengaging_emotions)
        
        # Base engagement is 0.5, adjust based on emotion balance
        engagement = 0.5 + (engaging_score - disengaging_score) * 0.3
        return max(0, min(1, engagement))
    
    def _assess_eye_contact(self, analysis):
        """Assess eye contact quality"""
        # This would normally use facial landmark detection
        # For now, provide a reasonable assessment based on engagement
        engagement = analysis.get("engagement_level", 0.5)
        
        if engagement > 0.7:
            return "excellent"
        elif engagement > 0.5:
            return "good"
        elif engagement > 0.3:
            return "moderate"
        else:
            return "poor"
    
    def _generate_recommendations(self, analysis, stress_level):
        """Generate therapeutic recommendations based on analysis"""
        recommendations = []
        emotions = analysis.get("emotions", {})
        
        # High stress recommendations
        if stress_level > 0.7:
            recommendations.extend([
                "Consider taking a brief pause to practice deep breathing",
                "Notice any physical tension and try to relax those muscles",
                "Ground yourself by focusing on the present moment"
            ])
        elif stress_level > 0.5:
            recommendations.extend([
                "Pay attention to your stress levels during this conversation",
                "Practice mindful breathing if you feel overwhelmed"
            ])
        
        # Specific emotion recommendations
        primary_emotion = self._get_primary_emotion(emotions)
        
        if primary_emotion == "anxiety" and emotions.get("anxiety", 0) > 0.6:
            recommendations.append("Use grounding techniques like the 5-4-3-2-1 method")
        elif primary_emotion == "sadness" and emotions.get("sadness", 0) > 0.6:
            recommendations.append("It's okay to feel sad - allow yourself to experience these emotions")
        elif primary_emotion == "anger" and emotions.get("anger", 0) > 0.6:
            recommendations.append("Take some deep breaths and consider what's behind the anger")
        elif primary_emotion == "fear" and emotions.get("fear", 0) > 0.6:
            recommendations.append("You're in a safe space - try to identify what feels threatening")
        
        # Emotional conflict recommendations
        if analysis.get("emotional_conflict"):
            recommendations.append("I notice mixed emotions - it's normal to feel multiple things at once")
        
        # Engagement recommendations
        engagement = analysis.get("engagement_level", 0.5)
        if engagement < 0.3:
            recommendations.append("Take your time - there's no pressure to engage more than feels comfortable")
        elif engagement > 0.8:
            recommendations.append("I appreciate your openness and engagement in this process")
        
        # Eye contact recommendations
        eye_contact = analysis.get("eye_contact", "unknown")
        if eye_contact == "poor":
            recommendations.append("It's okay if direct eye contact feels difficult right now")
        
        return recommendations[:3]  # Limit to top 3 recommendations
    
    def _fallback_analysis(self):
        """Fallback analysis when AI is unavailable"""
        return {
            "emotions": {"neutral": 0.8, "anxiety": 0.2},
            "primary_emotion": "neutral",
            "microexpressions": {},
            "facial_landmarks": {},
            "eye_contact": "moderate",
            "engagement_level": 0.6,
            "stress_level": 0.3,
            "confidence": 0.3,
            "recommendations": ["Video analysis temporarily unavailable - continue with text-based support"],
            "error": "AI analysis service unavailable"
        }
    
    def analyze_sequence(self, frame_sequence):
        """Analyze a sequence of frames for patterns"""
        try:
            if not frame_sequence:
                return {"error": "No frame sequence provided"}
            
            frame_analyses = []
            for i, frame_data in enumerate(frame_sequence):
                analysis = self.analyze_frame(frame_data)
                analysis["frame_index"] = i
                frame_analyses.append(analysis)
            
            # Analyze patterns across frames
            sequence_analysis = {
                "frame_count": len(frame_analyses),
                "emotional_trajectory": self._analyze_emotional_trajectory(frame_analyses),
                "stress_progression": self._analyze_stress_progression(frame_analyses),
                "engagement_patterns": self._analyze_engagement_patterns(frame_analyses),
                "microexpression_events": self._count_microexpression_events(frame_analyses),
                "overall_assessment": self._generate_sequence_assessment(frame_analyses),
                "timestamp": datetime.now().isoformat()
            }
            
            return sequence_analysis
            
        except Exception as e:
            logging.error(f"Sequence analysis error: {e}")
            return {"error": "Failed to analyze frame sequence"}
    
    def _analyze_emotional_trajectory(self, frame_analyses):
        """Analyze how emotions change over time"""
        emotions_over_time = {}
        
        for analysis in frame_analyses:
            emotions = analysis.get("emotions", {})
            for emotion, score in emotions.items():
                if emotion not in emotions_over_time:
                    emotions_over_time[emotion] = []
                emotions_over_time[emotion].append(score)
        
        trajectory = {}
        for emotion, scores in emotions_over_time.items():
            if scores:
                trajectory[emotion] = {
                    "start": scores[0],
                    "end": scores[-1],
                    "change": scores[-1] - scores[0],
                    "average": sum(scores) / len(scores),
                    "volatility": self._calculate_volatility(scores)
                }
        
        return trajectory
    
    def _analyze_stress_progression(self, frame_analyses):
        """Analyze stress level changes over time"""
        stress_levels = [analysis.get("stress_level", 0) for analysis in frame_analyses]
        
        if not stress_levels:
            return {}
        
        return {
            "initial_stress": stress_levels[0],
            "final_stress": stress_levels[-1],
            "peak_stress": max(stress_levels),
            "average_stress": sum(stress_levels) / len(stress_levels),
            "stress_trend": "increasing" if stress_levels[-1] > stress_levels[0] else "decreasing",
            "stress_variability": self._calculate_volatility(stress_levels)
        }
    
    def _analyze_engagement_patterns(self, frame_analyses):
        """Analyze engagement level patterns"""
        engagement_levels = [analysis.get("engagement_level", 0.5) for analysis in frame_analyses]
        
        return {
            "average_engagement": sum(engagement_levels) / len(engagement_levels),
            "peak_engagement": max(engagement_levels),
            "lowest_engagement": min(engagement_levels),
            "engagement_consistency": 1 - self._calculate_volatility(engagement_levels)
        }
    
    def _count_microexpression_events(self, frame_analyses):
        """Count microexpression events across frames"""
        microexpression_counts = {}
        
        for analysis in frame_analyses:
            microexpressions = analysis.get("microexpressions", {})
            if isinstance(microexpressions, dict):
                for micro_type in microexpressions.keys():
                    microexpression_counts[micro_type] = microexpression_counts.get(micro_type, 0) + 1
        
        return microexpression_counts
    
    def _generate_sequence_assessment(self, frame_analyses):
        """Generate overall assessment for the sequence"""
        if not frame_analyses:
            return "No data available for assessment"
        
        avg_stress = sum(analysis.get("stress_level", 0) for analysis in frame_analyses) / len(frame_analyses)
        avg_engagement = sum(analysis.get("engagement_level", 0.5) for analysis in frame_analyses) / len(frame_analyses)
        
        assessment = []
        
        if avg_stress > 0.7:
            assessment.append("High stress levels detected throughout the session")
        elif avg_stress > 0.5:
            assessment.append("Moderate stress levels observed")
        else:
            assessment.append("Relatively low stress levels maintained")
        
        if avg_engagement > 0.7:
            assessment.append("Strong engagement demonstrated")
        elif avg_engagement > 0.5:
            assessment.append("Moderate engagement levels")
        else:
            assessment.append("Lower engagement levels observed")
        
        return ". ".join(assessment)
    
    def _calculate_volatility(self, values):
        """Calculate volatility (standard deviation) of a list of values"""
        if len(values) < 2:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
