import logging
from datetime import datetime
from typing import Dict, List

class BiometricIntegrator:
    def __init__(self):
        self.device_types = {
            "apple_watch": {
                "metrics": ["heart_rate", "hrv", "stress", "activity", "sleep", "blood_oxygen"],
                "sampling_rate": "high",
                "accuracy": "very_high"
            },
            "fitbit": {
                "metrics": ["heart_rate", "steps", "sleep", "stress", "activity"],
                "sampling_rate": "medium",
                "accuracy": "high"
            },
            "garmin": {
                "metrics": ["heart_rate", "hrv", "stress", "activity", "recovery", "blood_oxygen"],
                "sampling_rate": "high",
                "accuracy": "very_high"
            },
            "samsung_health": {
                "metrics": ["heart_rate", "stress", "sleep", "activity", "blood_oxygen"],
                "sampling_rate": "medium",
                "accuracy": "medium"
            },
            "whoop": {
                "metrics": ["heart_rate", "hrv", "strain", "recovery", "sleep"],
                "sampling_rate": "very_high",
                "accuracy": "very_high"
            },
            "oura": {
                "metrics": ["heart_rate", "hrv", "temperature", "sleep", "activity"],
                "sampling_rate": "high",
                "accuracy": "very_high"
            },
            "generic": {
                "metrics": ["heart_rate", "activity"],
                "sampling_rate": "low",
                "accuracy": "medium"
            }
        }
        
        # Enhanced normal ranges for different metrics
        self.normal_ranges = {
            "heart_rate": {
                "rest": {"low": 60, "normal": 80, "high": 100},
                "light_activity": {"low": 85, "normal": 110, "high": 135},
                "moderate_activity": {"low": 110, "normal": 140, "high": 170},
                "intense_activity": {"low": 140, "normal": 165, "high": 190}
            },
            "hrv": {
                "excellent": {"min": 60, "max": 100},
                "good": {"min": 40, "max": 60},
                "fair": {"min": 20, "max": 40},
                "poor": {"min": 0, "max": 20}
            },
            "stress_level": {
                "low": {"min": 0, "max": 0.3},
                "moderate": {"min": 0.3, "max": 0.6},
                "high": {"min": 0.6, "max": 0.8},
                "very_high": {"min": 0.8, "max": 1.0}
            },
            "sleep_quality": {
                "excellent": {"min": 0.8, "max": 1.0},
                "good": {"min": 0.6, "max": 0.8},
                "fair": {"min": 0.4, "max": 0.6},
                "poor": {"min": 0, "max": 0.4}
            },
            "blood_oxygen": {
                "normal": {"min": 95, "max": 100},
                "low_normal": {"min": 90, "max": 95},
                "concerning": {"min": 85, "max": 90},
                "critical": {"min": 0, "max": 85}
            },
            "temperature": {
                "normal": {"min": 97.0, "max": 99.5},
                "low_fever": {"min": 99.5, "max": 101.0},
                "fever": {"min": 101.0, "max": 103.0},
                "high_fever": {"min": 103.0, "max": 106.0}
            }
        }
        
        # Enhanced stress indicators with weights
        self.stress_indicators = {
            "elevated_heart_rate": {"weight": 5, "threshold": 100},
            "very_high_heart_rate": {"weight": 8, "threshold": 120},
            "low_hrv": {"weight": 6, "threshold": 30},
            "very_low_hrv": {"weight": 9, "threshold": 15},
            "poor_sleep": {"weight": 4, "threshold": 0.4},
            "very_poor_sleep": {"weight": 7, "threshold": 0.2},
            "high_stress_score": {"weight": 7, "threshold": 0.7},
            "very_high_stress_score": {"weight": 10, "threshold": 0.9},
            "low_activity": {"weight": 2, "threshold": 1000},
            "very_low_activity": {"weight": 3, "threshold": 500},
            "low_blood_oxygen": {"weight": 8, "threshold": 92},
            "critically_low_oxygen": {"weight": 10, "threshold": 88},
            "elevated_temperature": {"weight": 4, "threshold": 99.5},
            "fever": {"weight": 6, "threshold": 101.0}
        }
    
    def analyze_patterns(self, biometric_data: Dict) -> Dict:
        """Analyze biometric data patterns for therapeutic insights"""
        try:
            analysis = {
                "overall_health_score": 0,
                "stress_indicators": [],
                "patterns": {},
                "alerts": [],
                "therapeutic_insights": [],
                "mental_health_correlations": [],
                "recommendations": [],
                "timestamp": datetime.now().isoformat(),
                "data_quality": self._assess_data_quality(biometric_data)
            }
            
            metrics_analyzed = 0
            total_health_contribution = 0
            
            # Analyze each available metric
            if "heart_rate" in biometric_data:
                hr_analysis = self._analyze_heart_rate(biometric_data["heart_rate"])
                analysis["patterns"]["heart_rate"] = hr_analysis
                total_health_contribution += hr_analysis.get("health_contribution", 0)
                metrics_analyzed += 1
                
                if hr_analysis.get("stress_indicator"):
                    analysis["stress_indicators"].extend(hr_analysis.get("stress_reasons", []))
            
            if "stress_level" in biometric_data:
                stress_analysis = self._analyze_stress_level(biometric_data["stress_level"])
                analysis["patterns"]["stress"] = stress_analysis
                analysis["stress_indicators"].extend(stress_analysis.get("indicators", []))
            
            if "sleep_quality" in biometric_data:
                sleep_analysis = self._analyze_sleep_quality(biometric_data["sleep_quality"])
                analysis["patterns"]["sleep"] = sleep_analysis
                total_health_contribution += sleep_analysis.get("health_contribution", 0)
                metrics_analyzed += 1
                
                if sleep_analysis.get("mental_health_impact"):
                    analysis["mental_health_correlations"].extend(sleep_analysis.get("mental_health_impact", []))
            
            if "hrv" in biometric_data:
                hrv_analysis = self._analyze_hrv(biometric_data["hrv"])
                analysis["patterns"]["hrv"] = hrv_analysis
                total_health_contribution += hrv_analysis.get("health_contribution", 0)
                metrics_analyzed += 1
                
                if hrv_analysis.get("stress_indicator"):
                    analysis["stress_indicators"].extend(hrv_analysis.get("stress_reasons", []))
            
            if "blood_oxygen" in biometric_data:
                oxygen_analysis = self._analyze_blood_oxygen(biometric_data["blood_oxygen"])
                analysis["patterns"]["blood_oxygen"] = oxygen_analysis
                total_health_contribution += oxygen_analysis.get("health_contribution", 0)
                metrics_analyzed += 1
            
            if "temperature" in biometric_data:
                temp_analysis = self._analyze_temperature(biometric_data["temperature"])
                analysis["patterns"]["temperature"] = temp_analysis
                total_health_contribution += temp_analysis.get("health_contribution", 0)
                metrics_analyzed += 1
            
            if "activity_level" in biometric_data:
                activity_analysis = self._analyze_activity_level(biometric_data["activity_level"])
                analysis["patterns"]["activity"] = activity_analysis
                total_health_contribution += activity_analysis.get("health_contribution", 0)
                metrics_analyzed += 1
            
            # Calculate overall health score
            if metrics_analyzed > 0:
                analysis["overall_health_score"] = min(total_health_contribution / metrics_analyzed, 1.0)
            
            # Generate therapeutic insights
            analysis["therapeutic_insights"] = self._generate_therapeutic_insights(analysis["patterns"])
            
            # Generate mental health correlations
            analysis["mental_health_correlations"].extend(
                self._analyze_mental_health_correlations(analysis["patterns"])
            )
            
            # Generate alerts
            analysis["alerts"] = self._generate_alerts(analysis["patterns"], analysis["stress_indicators"])
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_comprehensive_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            logging.error(f"Biometric analysis error: {e}")
            return {
                "error": "Biometric analysis failed", 
                "timestamp": datetime.now().isoformat(),
                "recommendations": ["Please ensure biometric data is properly formatted and try again"]
            }
    
    def _analyze_heart_rate(self, heart_rate: float) -> Dict:
        """Enhanced heart rate analysis"""
        analysis = {
            "value": heart_rate,
            "category": "normal",
            "health_contribution": 0.25,
            "insights": [],
            "stress_indicator": False,
            "stress_reasons": [],
            "mental_health_implications": []
        }
        
        if heart_rate < 50:
            analysis["category"] = "very_low"
            analysis["insights"].append("Very low heart rate - possible bradycardia or excellent fitness")
            analysis["health_contribution"] = 0.15
            analysis["mental_health_implications"].append("May indicate depression or medication effects")
        elif heart_rate < 60:
            analysis["category"] = "low"
            analysis["insights"].append("Low resting heart rate - indicates good cardiovascular fitness")
            analysis["health_contribution"] = 0.3
        elif heart_rate <= 80:
            analysis["category"] = "optimal"
            analysis["insights"].append("Excellent resting heart rate for most adults")
            analysis["health_contribution"] = 0.35
        elif heart_rate <= 100:
            analysis["category"] = "normal_high"
            analysis["insights"].append("Normal but slightly elevated resting heart rate")
            analysis["health_contribution"] = 0.2
        elif heart_rate <= 120:
            analysis["category"] = "elevated"
            analysis["insights"].append("Elevated heart rate - may indicate stress, anxiety, or physical exertion")
            analysis["health_contribution"] = 0.1
            analysis["stress_indicator"] = True
            analysis["stress_reasons"].append("Elevated heart rate detected")
            analysis["mental_health_implications"].append("May correlate with anxiety or panic symptoms")
        else:
            analysis["category"] = "very_high"
            analysis["insights"].append("Very high heart rate - immediate attention may be needed")
            analysis["health_contribution"] = 0.05
            analysis["stress_indicator"] = True
            analysis["stress_reasons"].append("Very high heart rate detected")
            analysis["mental_health_implications"].append("May indicate severe anxiety or panic attack")
        
        return analysis
    
    def _analyze_stress_level(self, stress_level: float) -> Dict:
        """Enhanced stress level analysis"""
        analysis = {
            "value": stress_level,
            "category": "low",
            "indicators": [],
            "recommendations": [],
            "mental_health_correlations": [],
            "intervention_urgency": "low"
        }
        
        if stress_level >= 0.9:
            analysis["category"] = "critical"
            analysis["indicators"].append("Critical stress levels detected")
            analysis["intervention_urgency"] = "immediate"
            analysis["recommendations"].extend([
                "Immediate stress reduction techniques required",
                "Consider professional mental health support",
                "Practice emergency calming techniques"
            ])
            analysis["mental_health_correlations"].append("May indicate acute anxiety or panic disorder")
        elif stress_level >= 0.7:
            analysis["category"] = "very_high"
            analysis["indicators"].append("Very high stress levels detected")
            analysis["intervention_urgency"] = "high"
            analysis["recommendations"].extend([
                "Implement immediate stress management strategies",
                "Practice deep breathing and mindfulness",
                "Consider reducing current stressors"
            ])
            analysis["mental_health_correlations"].append("Correlates with chronic anxiety and depression risk")
        elif stress_level >= 0.5:
            analysis["category"] = "high"
            analysis["indicators"].append("High stress levels detected")
            analysis["intervention_urgency"] = "moderate"
            analysis["recommendations"].extend([
                "Practice regular stress reduction techniques",
                "Monitor stress triggers",
                "Maintain healthy coping strategies"
            ])
            analysis["mental_health_correlations"].append("May contribute to mood disorders if sustained")
        elif stress_level >= 0.3:
            analysis["category"] = "moderate"
            analysis["indicators"].append("Moderate stress levels")
            analysis["recommendations"].append("Monitor stress and use preventive techniques")
            analysis["mental_health_correlations"].append("Normal stress response within healthy range")
        else:
            analysis["category"] = "low"
            analysis["recommendations"].append("Maintain current stress management practices")
            analysis["mental_health_correlations"].append("Low stress supports good mental health")
        
        return analysis
    
    def _analyze_sleep_quality(self, sleep_quality: float) -> Dict:
        """Enhanced sleep quality analysis"""
        analysis = {
            "value": sleep_quality,
            "category": "fair",
            "health_contribution": 0.2,
            "insights": [],
            "mental_health_impact": [],
            "cognitive_impact": []
        }
        
        if sleep_quality >= 0.9:
            analysis["category"] = "exceptional"
            analysis["health_contribution"] = 0.4
            analysis["insights"].append("Exceptional sleep quality supporting optimal mental health")
            analysis["mental_health_impact"].append("Excellent sleep supports emotional regulation")
            analysis["cognitive_impact"].append("Optimal cognitive performance expected")
        elif sleep_quality >= 0.8:
            analysis["category"] = "excellent"
            analysis["health_contribution"] = 0.35
            analysis["insights"].append("Excellent sleep quality supporting mental well-being")
            analysis["mental_health_impact"].append("High-quality sleep promotes emotional stability")
        elif sleep_quality >= 0.6:
            analysis["category"] = "good"
            analysis["health_contribution"] = 0.25
            analysis["insights"].append("Good sleep quality with minor room for improvement")
            analysis["mental_health_impact"].append("Sleep quality generally supports mental health")
        elif sleep_quality >= 0.4:
            analysis["category"] = "fair"
            analysis["insights"].append("Fair sleep quality - improvement recommended")
            analysis["mental_health_impact"].append("Sleep issues may be affecting emotional well-being")
            analysis["cognitive_impact"].append("May experience reduced cognitive performance")
        elif sleep_quality >= 0.2:
            analysis["category"] = "poor"
            analysis["health_contribution"] = 0.1
            analysis["insights"].append("Poor sleep quality significantly impacting health")
            analysis["mental_health_impact"].extend([
                "Poor sleep strongly linked to depression and anxiety",
                "Emotional regulation likely compromised"
            ])
            analysis["cognitive_impact"].append("Significant cognitive impairment likely")
        else:
            analysis["category"] = "very_poor"
            analysis["health_contribution"] = 0.05
            analysis["insights"].append("Very poor sleep quality requiring immediate attention")
            analysis["mental_health_impact"].extend([
                "Severe sleep deprivation major risk factor for mental health crisis",
                "Immediate intervention recommended"
            ])
            analysis["cognitive_impact"].append("Severe cognitive impairment expected")
        
        return analysis
    
    def _analyze_hrv(self, hrv: float) -> Dict:
        """Enhanced HRV analysis"""
        analysis = {
            "value": hrv,
            "category": "normal",
            "health_contribution": 0.2,
            "insights": [],
            "stress_indicator": False,
            "stress_reasons": [],
            "autonomic_balance": "balanced"
        }
        
        if hrv >= 70:
            analysis["category"] = "exceptional"
            analysis["health_contribution"] = 0.4
            analysis["insights"].append("Exceptional HRV indicates superior stress resilience")
            analysis["autonomic_balance"] = "excellent"
        elif hrv >= 50:
            analysis["category"] = "excellent"
            analysis["health_contribution"] = 0.35
            analysis["insights"].append("Excellent HRV indicates very good autonomic balance")
            analysis["autonomic_balance"] = "very_good"
        elif hrv >= 30:
            analysis["category"] = "good"
            analysis["health_contribution"] = 0.25
            analysis["insights"].append("Good HRV levels supporting stress management")
            analysis["autonomic_balance"] = "good"
        elif hrv >= 20:
            analysis["category"] = "fair"
            analysis["insights"].append("Fair HRV - improvement possible with stress management")
            analysis["autonomic_balance"] = "slightly_impaired"
        elif hrv >= 15:
            analysis["category"] = "low"
            analysis["health_contribution"] = 0.1
            analysis["insights"].append("Low HRV may indicate chronic stress or fatigue")
            analysis["stress_indicator"] = True
            analysis["stress_reasons"].append("Low heart rate variability detected")
            analysis["autonomic_balance"] = "impaired"
        else:
            analysis["category"] = "very_low"
            analysis["health_contribution"] = 0.05
            analysis["insights"].append("Very low HRV indicates significant autonomic dysfunction")
            analysis["stress_indicator"] = True
            analysis["stress_reasons"].append("Very low heart rate variability - concerning")
            analysis["autonomic_balance"] = "severely_impaired"
        
        return analysis
    
    def _analyze_blood_oxygen(self, blood_oxygen: float) -> Dict:
        """Analyze blood oxygen saturation"""
        analysis = {
            "value": blood_oxygen,
            "category": "normal",
            "health_contribution": 0.2,
            "insights": [],
            "alerts": []
        }
        
        if blood_oxygen >= 98:
            analysis["category"] = "excellent"
            analysis["health_contribution"] = 0.3
            analysis["insights"].append("Excellent oxygen saturation levels")
        elif blood_oxygen >= 95:
            analysis["category"] = "normal"
            analysis["health_contribution"] = 0.25
            analysis["insights"].append("Normal oxygen saturation levels")
        elif blood_oxygen >= 90:
            analysis["category"] = "low_normal"
            analysis["health_contribution"] = 0.15
            analysis["insights"].append("Low-normal oxygen levels - monitor closely")
            analysis["alerts"].append("Oxygen levels below optimal range")
        elif blood_oxygen >= 85:
            analysis["category"] = "concerning"
            analysis["health_contribution"] = 0.1
            analysis["insights"].append("Concerning oxygen levels - may need medical attention")
            analysis["alerts"].append("Low oxygen saturation detected")
        else:
            analysis["category"] = "critical"
            analysis["health_contribution"] = 0.05
            analysis["insights"].append("Critical oxygen levels - immediate medical attention needed")
            analysis["alerts"].append("Critically low oxygen saturation")
        
        return analysis
    
    def _analyze_temperature(self, temperature: float) -> Dict:
        """Analyze body temperature"""
        analysis = {
            "value": temperature,
            "category": "normal",
            "health_contribution": 0.2,
            "insights": [],
            "fever_status": "none"
        }
        
        if temperature < 97.0:
            analysis["category"] = "low"
            analysis["health_contribution"] = 0.15
            analysis["insights"].append("Below normal body temperature")
            analysis["fever_status"] = "hypothermia_risk"
        elif temperature <= 99.5:
            analysis["category"] = "normal"
            analysis["health_contribution"] = 0.25
            analysis["insights"].append("Normal body temperature")
        elif temperature <= 101.0:
            analysis["category"] = "low_fever"
            analysis["health_contribution"] = 0.2
            analysis["insights"].append("Low-grade fever detected")
            analysis["fever_status"] = "low_grade"
        elif temperature <= 103.0:
            analysis["category"] = "fever"
            analysis["health_contribution"] = 0.1
            analysis["insights"].append("Fever detected - monitor symptoms")
            analysis["fever_status"] = "moderate"
        else:
            analysis["category"] = "high_fever"
            analysis["health_contribution"] = 0.05
            analysis["insights"].append("High fever - medical attention recommended")
            analysis["fever_status"] = "high"
        
        return analysis
    
    def _analyze_activity_level(self, activity_level: int) -> Dict:
        """Analyze physical activity level"""
        analysis = {
            "value": activity_level,
            "category": "moderate",
            "health_contribution": 0.15,
            "insights": [],
            "mental_health_benefits": []
        }
        
        if activity_level >= 12000:
            analysis["category"] = "very_high"
            analysis["health_contribution"] = 0.3
            analysis["insights"].append("Excellent activity levels supporting mental and physical health")
            analysis["mental_health_benefits"].append("High activity supports mood regulation and stress relief")
        elif activity_level >= 8000:
            analysis["category"] = "high"
            analysis["health_contribution"] = 0.25
            analysis["insights"].append("Good activity levels contributing to overall well-being")
            analysis["mental_health_benefits"].append("Regular activity supports mental health")
        elif activity_level >= 5000:
            analysis["category"] = "moderate"
            analysis["health_contribution"] = 0.2
            analysis["insights"].append("Moderate activity levels - room for improvement")
            analysis["mental_health_benefits"].append("Some mental health benefits from current activity")
        elif activity_level >= 2000:
            analysis["category"] = "low"
            analysis["health_contribution"] = 0.1
            analysis["insights"].append("Low activity levels - increased movement recommended")
            analysis["mental_health_benefits"].append("Limited mental health benefits from low activity")
        else:
            analysis["category"] = "very_low"
            analysis["health_contribution"] = 0.05
            analysis["insights"].append("Very low activity levels - significant increase needed")
            analysis["mental_health_benefits"].append("Minimal activity may contribute to mood issues")
        
        return analysis
    
    def _generate_therapeutic_insights(self, patterns: Dict) -> List[str]:
        """Generate enhanced therapeutic insights from biometric patterns"""
        insights = []
        
        # Heart rate insights
        if "heart_rate" in patterns:
            hr_data = patterns["heart_rate"]
            if hr_data.get("stress_indicator"):
                insights.append("Elevated heart rate suggests physiological stress response that may correlate with anxiety")
            elif hr_data["category"] == "optimal":
                insights.append("Excellent heart rate indicates good cardiovascular health supporting emotional regulation")
        
        # Stress level insights
        if "stress" in patterns:
            stress_data = patterns["stress"]
            if stress_data["category"] in ["very_high", "critical"]:
                insights.append("High physiological stress levels may be significantly impacting therapy effectiveness and daily functioning")
            elif stress_data["category"] == "low":
                insights.append("Low stress levels suggest good emotional regulation and receptiveness to therapeutic interventions")
        
        # Sleep insights with mental health correlation
        if "sleep" in patterns:
            sleep_data = patterns["sleep"]
            if sleep_data["category"] in ["poor", "very_poor"]:
                insights.append("Poor sleep quality is strongly linked to depression and anxiety - addressing sleep should be a therapy priority")
            elif sleep_data["category"] in ["excellent", "exceptional"]:
                insights.append("Excellent sleep quality provides a strong foundation for mental health recovery and emotional stability")
        
        # HRV insights
        if "hrv" in patterns:
            hrv_data = patterns["hrv"]
            if hrv_data["category"] in ["low", "very_low"]:
                insights.append("Low heart rate variability indicates reduced stress resilience and may correlate with depression or chronic anxiety")
            elif hrv_data["category"] in ["excellent", "exceptional"]:
                insights.append("High HRV shows excellent autonomic nervous system balance and stress resilience")
        
        # Activity insights
        if "activity" in patterns:
            activity_data = patterns["activity"]
            if activity_data["category"] in ["low", "very_low"]:
                insights.append("Low physical activity levels may be contributing to mood issues - exercise is a powerful therapeutic tool")
            elif activity_data["category"] in ["high", "very_high"]:
                insights.append("High activity levels provide significant mental health benefits through endorphin release and stress reduction")
        
        # Multi-metric correlations
        stress_indicators = sum(1 for pattern in patterns.values() if pattern.get("stress_indicator"))
        if stress_indicators >= 2:
            insights.append("Multiple physiological stress indicators suggest need for comprehensive stress management in therapy")
        
        # Positive correlation insights
        positive_indicators = sum(1 for pattern in patterns.values() 
                                if pattern.get("category") in ["excellent", "exceptional", "optimal"])
        if positive_indicators >= 2:
            insights.append("Multiple positive health indicators suggest good physiological foundation for therapeutic progress")
        
        return insights
    
    def _analyze_mental_health_correlations(self, patterns: Dict) -> List[str]:
        """Analyze correlations between biometric data and mental health"""
        correlations = []
        
        # Sleep-mood correlation
        if "sleep" in patterns:
            sleep_data = patterns["sleep"]
            if sleep_data["category"] in ["poor", "very_poor"]:
                correlations.append("Poor sleep strongly correlates with increased depression and anxiety symptoms")
            elif sleep_data["category"] in ["excellent", "exceptional"]:
                correlations.append("Excellent sleep quality correlates with improved mood stability and reduced anxiety")
        
        # HRV-stress resilience correlation
        if "hrv" in patterns:
            hrv_data = patterns["hrv"]
            if hrv_data["category"] in ["low", "very_low"]:
                correlations.append("Low HRV correlates with reduced ability to cope with psychological stress")
            elif hrv_data["category"] in ["excellent", "exceptional"]:
                correlations.append("High HRV correlates with better emotional regulation and stress management")
        
        # Activity-mood correlation
        if "activity" in patterns:
            activity_data = patterns["activity"]
            if activity_data["category"] in ["low", "very_low"]:
                correlations.append("Low activity levels correlate with increased risk of depression and reduced mood stability")
            elif activity_data["category"] in ["high", "very_high"]:
                correlations.append("High activity levels correlate with improved mood, reduced anxiety, and better stress management")
        
        # Heart rate-anxiety correlation
        if "heart_rate" in patterns:
            hr_data = patterns["heart_rate"]
            if hr_data.get("stress_indicator"):
                correlations.append("Elevated heart rate may correlate with anxiety symptoms and panic responses")
        
        return correlations
    
    def _generate_alerts(self, patterns: Dict, stress_indicators: List[str]) -> List[Dict]:
        """Generate enhanced alerts based on biometric analysis"""
        alerts = []
        
        # Critical heart rate alert
        if "heart_rate" in patterns and patterns["heart_rate"]["value"] > 130:
            alerts.append({
                "level": "critical",
                "type": "cardiovascular",
                "message": "Extremely elevated heart rate detected",
                "action": "Consider immediate medical evaluation or emergency services",
                "mental_health_note": "May indicate severe anxiety or panic attack"
            })
        
        # High stress alert
        if "stress" in patterns and patterns["stress"]["category"] in ["very_high", "critical"]:
            alerts.append({
                "level": "warning",
                "type": "psychological",
                "message": "Very high physiological stress levels detected",
                "action": "Implement immediate stress reduction techniques and consider crisis support",
                "mental_health_note": "High stress levels significantly impact mental health and therapy effectiveness"
            })
        
        # Sleep crisis alert
        if "sleep" in patterns and patterns["sleep"]["category"] == "very_poor":
            alerts.append({
                "level": "warning",
                "type": "sleep",
                "message": "Severe sleep deprivation affecting mental health",
                "action": "Address sleep hygiene immediately - consider sleep medicine consultation",
                "mental_health_note": "Severe sleep issues are major risk factor for mental health crisis"
            })
        
        # HRV concern alert
        if "hrv" in patterns and patterns["hrv"]["category"] == "very_low":
            alerts.append({
                "level": "info",
                "type": "autonomic",
                "message": "Very low heart rate variability indicates autonomic dysfunction",
                "action": "Focus on stress reduction and recovery practices",
                "mental_health_note": "Low HRV correlates with reduced emotional resilience"
            })
        
        # Blood oxygen alert
        if "blood_oxygen" in patterns and patterns["blood_oxygen"]["category"] in ["concerning", "critical"]:
            alerts.append({
                "level": "critical",
                "type": "respiratory",
                "message": "Low blood oxygen saturation detected",
                "action": "Seek immediate medical attention",
                "mental_health_note": "Low oxygen can affect cognitive function and mood"
            })
        
        # Temperature alert
        if "temperature" in patterns and patterns["temperature"]["category"] in ["fever", "high_fever"]:
            alerts.append({
                "level": "warning",
                "type": "temperature",
                "message": f"Fever detected: {patterns['temperature']['value']}°F",
                "action": "Monitor symptoms and consider medical consultation",
                "mental_health_note": "Fever can affect mood and cognitive function"
            })
        
        return alerts
    
    def _generate_comprehensive_recommendations(self, analysis: Dict) -> List[str]:
        """Generate comprehensive recommendations based on full analysis"""
        recommendations = []
        patterns = analysis.get("patterns", {})
        stress_indicators = analysis.get("stress_indicators", [])
        
        # Stress management recommendations
        if len(stress_indicators) >= 2:
            recommendations.extend([
                "Implement comprehensive stress management program including meditation, breathing exercises, and regular therapy",
                "Consider stress-reduction techniques like progressive muscle relaxation and mindfulness",
                "Monitor stress levels throughout the day and identify triggers"
            ])
        elif stress_indicators:
            recommendations.extend([
                "Practice daily stress reduction techniques",
                "Consider mindfulness meditation or yoga",
                "Monitor stress patterns and identify triggers"
            ])
        
        # Sleep recommendations
        if "sleep" in patterns:
            sleep_category = patterns["sleep"]["category"]
            if sleep_category in ["poor", "very_poor"]:
                recommendations.extend([
                    "Prioritize sleep hygiene: consistent bedtime, dark room, no screens before bed",
                    "Consider sleep medicine consultation if sleep issues persist",
                    "Address sleep issues as primary therapy goal due to strong mental health impact"
                ])
            elif sleep_category == "fair":
                recommendations.extend([
                    "Improve sleep consistency and create better bedtime routine",
                    "Limit caffeine and screen time before bed"
                ])
        
        # Heart rate recommendations
        if "heart_rate" in patterns:
            hr_data = patterns["heart_rate"]
            if hr_data.get("stress_indicator"):
                recommendations.extend([
                    "Practice heart rate variability training and coherent breathing",
                    "Consider cardiovascular exercise to improve heart rate recovery",
                    "Learn anxiety management techniques to reduce physiological stress response"
                ])
            elif hr_data["category"] == "optimal":
                recommendations.append("Maintain current cardiovascular health practices")
        
        # HRV recommendations
        if "hrv" in patterns:
            hrv_category = patterns["hrv"]["category"]
            if hrv_category in ["low", "very_low"]:
                recommendations.extend([
                    "Focus on stress resilience building through HRV training",
                    "Practice coherent breathing exercises daily",
                    "Maintain regular sleep patterns and reduce chronic stressors",
                    "Consider HRV biofeedback training"
                ])
            elif hrv_category in ["excellent", "exceptional"]:
                recommendations.append("Continue current practices that support excellent stress resilience")
        
        # Activity recommendations
        if "activity" in patterns:
            activity_category = patterns["activity"]["category"]
            if activity_category in ["low", "very_low"]:
                recommendations.extend([
                    "Gradually increase daily physical activity - even 10 minutes of walking helps mood",
                    "Consider exercise as medicine: aim for 150 minutes moderate activity per week",
                    "Try enjoyable activities like dancing, swimming, or hiking to boost mood naturally"
                ])
            elif activity_category == "moderate":
                recommendations.append("Consider increasing activity level for additional mental health benefits")
        
        # Mental health integration recommendations
        mental_health_correlations = analysis.get("mental_health_correlations", [])
        if mental_health_correlations:
            recommendations.append("Discuss biometric patterns with therapist to integrate physical and mental health approaches")
        
        # Data quality recommendations
        data_quality = analysis.get("data_quality", {})
        if data_quality.get("completeness", 1.0) < 0.7:
            recommendations.append("Consider wearing biometric device more consistently for better health insights")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _assess_data_quality(self, biometric_data: Dict) -> Dict:
        """Assess the quality and completeness of biometric data"""
        total_possible_metrics = 8  # heart_rate, stress_level, sleep_quality, hrv, blood_oxygen, temperature, activity_level, etc.
        available_metrics = len([k for k in biometric_data.keys() if biometric_data[k] is not None])
        
        completeness = available_metrics / total_possible_metrics
        
        quality_assessment = {
            "completeness": completeness,
            "available_metrics": available_metrics,
            "missing_metrics": total_possible_metrics - available_metrics,
            "quality_score": completeness,
            "recommendations": []
        }
        
        if completeness < 0.5:
            quality_assessment["recommendations"].append("Consider using a more comprehensive biometric monitoring device")
        elif completeness < 0.8:
            quality_assessment["recommendations"].append("Additional biometric data would provide more comprehensive insights")
        
        return quality_assessment
    
    def analyze_real_time(self, biometric_data: Dict) -> Dict:
        """Enhanced real-time biometric data analysis during therapy session"""
        real_time_analysis = {
            "current_state": "stable",
            "stress_level": 0,
            "alerts": [],
            "recommendations": [],
            "intervention_needed": False,
            "store_data": False,
            "timestamp": datetime.now().isoformat()
        }
        
        # Quick stress assessment with enhanced scoring
        stress_score = 0
        alert_reasons = []
        
        if "heart_rate" in biometric_data and isinstance(biometric_data["heart_rate"], (int, float)):
            hr = biometric_data["heart_rate"]
            if hr > 120:
                stress_score += 0.6
                alert_reasons.append(f"Very high heart rate: {hr} bpm")
                real_time_analysis["current_state"] = "high_stress"
            elif hr > 100:
                stress_score += 0.3
                alert_reasons.append(f"Elevated heart rate: {hr} bpm")
                real_time_analysis["current_state"] = "elevated"
        
        if "stress_level" in biometric_data and isinstance(biometric_data["stress_level"], (int, float)):
            device_stress = biometric_data["stress_level"]
            stress_score += device_stress * 0.4
            if device_stress > 0.8:
                alert_reasons.append(f"Device stress level very high: {device_stress:.1%}")
        
        if "hrv" in biometric_data and isinstance(biometric_data["hrv"], (int, float)):
            hrv = biometric_data["hrv"]
            if hrv < 20:
                stress_score += 0.3
                alert_reasons.append(f"Low heart rate variability: {hrv}")
        
        if "blood_oxygen" in biometric_data and isinstance(biometric_data["blood_oxygen"], (int, float)):
            oxygen = biometric_data["blood_oxygen"]
            if oxygen < 95:
                stress_score += 0.2
                alert_reasons.append(f"Low blood oxygen: {oxygen}%")
                if oxygen < 90:
                    real_time_analysis["alerts"].append({
                        "level": "critical",
                        "message": "Low blood oxygen detected - consider medical attention"
                    })
        
        real_time_analysis["stress_level"] = min(stress_score, 1.0)
        
        # Generate real-time recommendations with enhanced logic
        if stress_score > 0.8:
            real_time_analysis["current_state"] = "crisis"
            real_time_analysis["intervention_needed"] = True
            real_time_analysis["recommendations"] = [
                "Immediate intervention recommended - pause session",
                "Guide patient through emergency calming techniques",
                "Consider shortening session or providing crisis support",
                "Monitor closely for panic attack symptoms"
            ]
            real_time_analysis["store_data"] = True
        elif stress_score > 0.6:
            real_time_analysis["current_state"] = "high_stress"
            real_time_analysis["recommendations"] = [
                "Take a brief pause in the session",
                "Guide patient through deep breathing exercises",
                "Check in with patient's comfort level and adjust pace",
                "Consider stress reduction techniques"
            ]
            real_time_analysis["store_data"] = True
        elif stress_score > 0.4:
            real_time_analysis["current_state"] = "moderate_stress"
            real_time_analysis["recommendations"] = [
                "Monitor stress levels closely",
                "Be prepared to implement relaxation techniques",
                "Adjust session intensity if needed"
            ]
        elif stress_score < 0.2:
            real_time_analysis["current_state"] = "relaxed"
            real_time_analysis["recommendations"] = [
                "Patient appears physiologically calm",
                "Good opportunity for deeper therapeutic work",
                "Maintain current approach"
            ]
        
        # Add specific alerts for concerning patterns
        if alert_reasons:
            real_time_analysis["alerts"].extend([
                {"level": "warning", "message": reason} for reason in alert_reasons
            ])
        
        return real_time_analysis
    
    def get_recommendations(self, analysis: Dict) -> List[str]:
        """Get personalized recommendations based on comprehensive biometric analysis"""
        return analysis.get("recommendations", [
            "Continue monitoring biometric data for health insights",
            "Maintain regular physical activity",
            "Practice stress management techniques",
            "Ensure adequate sleep quality"
        ])
