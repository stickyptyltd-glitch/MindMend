"""
IoT & Wearable Device Integration Manager
Handles integration with smart devices, wearables, and environmental sensors
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import uuid
from enum import Enum
import random
import math
import numpy as np

class DeviceType(Enum):
    SMARTWATCH = "smartwatch"
    FITNESS_TRACKER = "fitness_tracker"
    SMART_RING = "smart_ring"
    SLEEP_TRACKER = "sleep_tracker"
    SMART_HOME_HUB = "smart_home_hub"
    AIR_QUALITY_SENSOR = "air_quality_sensor"
    LIGHT_SENSOR = "light_sensor"
    NOISE_MONITOR = "noise_monitor"
    TEMPERATURE_SENSOR = "temperature_sensor"
    SMARTPHONE = "smartphone"

class DeviceBrand(Enum):
    APPLE_WATCH = "apple_watch"
    FITBIT = "fitbit"
    GARMIN = "garmin"
    SAMSUNG_GALAXY = "samsung_galaxy"
    OURA_RING = "oura_ring"
    WHOOP = "whoop"
    GOOGLE_PIXEL = "google_pixel"
    AMAZON_ALEXA = "amazon_alexa"
    PHILIPS_HUE = "philips_hue"
    NEST = "nest"

class DataStreamType(Enum):
    HEART_RATE = "heart_rate"
    STEPS = "steps"
    SLEEP_STAGES = "sleep_stages"
    STRESS_LEVEL = "stress_level"
    BLOOD_OXYGEN = "blood_oxygen"
    SKIN_TEMPERATURE = "skin_temperature"
    AMBIENT_LIGHT = "ambient_light"
    AIR_QUALITY = "air_quality"
    NOISE_LEVEL = "noise_level"
    LOCATION = "location"
    SCREEN_TIME = "screen_time"
    APP_USAGE = "app_usage"

class ConnectionStatus(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    SYNCING = "syncing"
    ERROR = "error"
    PAIRING = "pairing"

@dataclass
class WearableDevice:
    device_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    device_type: DeviceType = DeviceType.SMARTWATCH
    brand: DeviceBrand = DeviceBrand.APPLE_WATCH
    model: str = ""
    firmware_version: str = ""
    battery_level: float = 100.0
    connection_status: ConnectionStatus = ConnectionStatus.CONNECTED
    last_sync: datetime = field(default_factory=datetime.now)
    data_streams: List[DataStreamType] = field(default_factory=list)
    permissions_granted: List[str] = field(default_factory=list)
    device_settings: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)

@dataclass
class SensorReading:
    reading_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str = ""
    user_id: str = ""
    data_stream: DataStreamType = DataStreamType.HEART_RATE
    value: float = 0.0
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    quality_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False

@dataclass
class EnvironmentalData:
    reading_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    location: str = "home"
    air_quality_index: float = 50.0
    temperature: float = 22.0  # Celsius
    humidity: float = 45.0  # Percentage
    light_level: float = 300.0  # Lux
    noise_level: float = 40.0  # Decibels
    uv_index: float = 3.0
    pollen_count: float = 20.0
    timestamp: datetime = field(default_factory=datetime.now)
    weather_conditions: str = "clear"

@dataclass
class SleepAnalysis:
    analysis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    device_id: str = ""
    sleep_date: datetime = field(default_factory=lambda: datetime.now().replace(hour=0, minute=0, second=0))
    bedtime: datetime = field(default_factory=datetime.now)
    sleep_onset: datetime = field(default_factory=datetime.now)
    wake_time: datetime = field(default_factory=datetime.now)
    total_sleep_time: float = 7.5  # Hours
    sleep_efficiency: float = 0.85  # Percentage
    deep_sleep_minutes: float = 90.0
    rem_sleep_minutes: float = 120.0
    light_sleep_minutes: float = 240.0
    wake_episodes: int = 2
    sleep_score: float = 82.0
    hrv_during_sleep: float = 45.0
    resting_heart_rate: float = 60.0

@dataclass
class ActivitySummary:
    summary_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    date: datetime = field(default_factory=lambda: datetime.now().replace(hour=0, minute=0, second=0))
    total_steps: int = 8500
    active_minutes: int = 45
    calories_burned: int = 2200
    distance_km: float = 6.8
    flights_climbed: int = 12
    sedentary_minutes: int = 480
    stress_average: float = 0.3
    recovery_score: float = 75.0
    energy_level: float = 0.7

@dataclass
class DigitalBiomarker:
    biomarker_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    biomarker_type: str = "keystroke_dynamics"
    value: float = 0.0
    confidence_score: float = 0.8
    data_source: str = "smartphone"
    collection_method: str = "passive"
    timestamp: datetime = field(default_factory=datetime.now)
    clinical_relevance: str = "depression_screening"
    raw_features: Dict[str, Any] = field(default_factory=dict)

class IoTWearableManager:
    def __init__(self):
        self.connected_devices: Dict[str, WearableDevice] = {}
        self.sensor_readings: Dict[str, List[SensorReading]] = {}
        self.environmental_data: Dict[str, List[EnvironmentalData]] = {}
        self.sleep_analyses: Dict[str, List[SleepAnalysis]] = {}
        self.activity_summaries: Dict[str, List[ActivitySummary]] = {}
        self.digital_biomarkers: Dict[str, List[DigitalBiomarker]] = {}
        self.device_configurations = self._initialize_device_configs()

    def _initialize_device_configs(self) -> Dict[DeviceBrand, Dict[str, Any]]:
        """Initialize device-specific configurations"""
        return {
            DeviceBrand.APPLE_WATCH: {
                "supported_streams": [
                    DataStreamType.HEART_RATE, DataStreamType.STEPS, DataStreamType.SLEEP_STAGES,
                    DataStreamType.BLOOD_OXYGEN, DataStreamType.STRESS_LEVEL
                ],
                "api_endpoint": "https://developer.apple.com/healthkit/",
                "sync_frequency": 300,  # seconds
                "battery_optimization": True,
                "data_retention": 30  # days
            },
            DeviceBrand.FITBIT: {
                "supported_streams": [
                    DataStreamType.HEART_RATE, DataStreamType.STEPS, DataStreamType.SLEEP_STAGES,
                    DataStreamType.STRESS_LEVEL, DataStreamType.SKIN_TEMPERATURE
                ],
                "api_endpoint": "https://dev.fitbit.com/build/reference/web-api/",
                "sync_frequency": 900,  # seconds
                "battery_optimization": True,
                "data_retention": 30
            },
            DeviceBrand.OURA_RING: {
                "supported_streams": [
                    DataStreamType.HEART_RATE, DataStreamType.SLEEP_STAGES,
                    DataStreamType.SKIN_TEMPERATURE, DataStreamType.STRESS_LEVEL
                ],
                "api_endpoint": "https://cloud.ouraring.com/v2/",
                "sync_frequency": 3600,  # seconds (hourly)
                "battery_optimization": True,
                "data_retention": 90
            },
            DeviceBrand.GARMIN: {
                "supported_streams": [
                    DataStreamType.HEART_RATE, DataStreamType.STEPS, DataStreamType.STRESS_LEVEL,
                    DataStreamType.BLOOD_OXYGEN, DataStreamType.SLEEP_STAGES
                ],
                "api_endpoint": "https://developer.garmin.com/connect-iq/",
                "sync_frequency": 600,
                "battery_optimization": True,
                "data_retention": 60
            }
        }

    def register_device(self, user_id: str, device_type: DeviceType, brand: DeviceBrand,
                       model: str, permissions: List[str]) -> WearableDevice:
        """Register a new wearable device for user"""

        # Get supported data streams for this device
        config = self.device_configurations.get(brand, {})
        supported_streams = config.get("supported_streams", [])

        device = WearableDevice(
            user_id=user_id,
            device_type=device_type,
            brand=brand,
            model=model,
            data_streams=supported_streams,
            permissions_granted=permissions,
            device_settings=self._get_default_settings(brand)
        )

        self.connected_devices[device.device_id] = device

        # Initialize data storage for this device
        self.sensor_readings[device.device_id] = []

        # Start data collection simulation
        self._start_data_collection(device)

        return device

    def _get_default_settings(self, brand: DeviceBrand) -> Dict[str, Any]:
        """Get default device settings"""
        return {
            "data_sync_frequency": self.device_configurations.get(brand, {}).get("sync_frequency", 600),
            "battery_optimization": True,
            "privacy_mode": False,
            "high_accuracy_mode": True,
            "notifications_enabled": True,
            "auto_workout_detection": True
        }

    def _start_data_collection(self, device: WearableDevice):
        """Start collecting data from device (simulation)"""
        # In real implementation, this would establish API connections
        # For now, we'll simulate data collection

        # Generate baseline readings for the device
        for stream_type in device.data_streams:
            self._generate_baseline_reading(device, stream_type)

    def _generate_baseline_reading(self, device: WearableDevice, stream_type: DataStreamType):
        """Generate simulated sensor reading"""

        # Generate realistic values based on stream type
        value, unit = self._get_realistic_value(stream_type)

        reading = SensorReading(
            device_id=device.device_id,
            user_id=device.user_id,
            data_stream=stream_type,
            value=value,
            unit=unit,
            quality_score=random.uniform(0.8, 1.0),
            metadata={
                "device_brand": device.brand.value,
                "firmware_version": device.firmware_version,
                "battery_level": device.battery_level
            }
        )

        self.sensor_readings[device.device_id].append(reading)

    def _get_realistic_value(self, stream_type: DataStreamType) -> Tuple[float, str]:
        """Generate realistic values for different data streams"""

        if stream_type == DataStreamType.HEART_RATE:
            return random.uniform(60, 100), "bpm"
        elif stream_type == DataStreamType.STEPS:
            return random.randint(0, 1000), "steps"
        elif stream_type == DataStreamType.BLOOD_OXYGEN:
            return random.uniform(95, 100), "percentage"
        elif stream_type == DataStreamType.STRESS_LEVEL:
            return random.uniform(0, 1), "score"
        elif stream_type == DataStreamType.SKIN_TEMPERATURE:
            return random.uniform(36, 37.5), "celsius"
        elif stream_type == DataStreamType.AMBIENT_LIGHT:
            return random.uniform(0, 1000), "lux"
        elif stream_type == DataStreamType.NOISE_LEVEL:
            return random.uniform(30, 80), "decibels"
        elif stream_type == DataStreamType.AIR_QUALITY:
            return random.uniform(0, 300), "aqi"
        else:
            return random.uniform(0, 100), "units"

    def collect_real_time_data(self, device_id: str) -> List[SensorReading]:
        """Collect real-time data from device"""
        device = self.connected_devices.get(device_id)
        if not device:
            return []

        new_readings = []
        for stream_type in device.data_streams:
            # Simulate real-time data collection
            value, unit = self._get_realistic_value(stream_type)

            # Add some temporal variation based on time of day
            value = self._apply_temporal_variation(value, stream_type)

            reading = SensorReading(
                device_id=device_id,
                user_id=device.user_id,
                data_stream=stream_type,
                value=value,
                unit=unit,
                quality_score=random.uniform(0.85, 1.0),
                metadata={
                    "collection_method": "real_time",
                    "device_status": device.connection_status.value
                }
            )

            new_readings.append(reading)
            self.sensor_readings[device_id].append(reading)

        # Update device last sync
        device.last_sync = datetime.now()

        return new_readings

    def _apply_temporal_variation(self, base_value: float, stream_type: DataStreamType) -> float:
        """Apply time-of-day variations to sensor values"""
        current_hour = datetime.now().hour

        if stream_type == DataStreamType.HEART_RATE:
            # Lower at night, higher during day
            if 22 <= current_hour or current_hour <= 6:
                return base_value * random.uniform(0.8, 0.9)  # Nighttime reduction
            elif 9 <= current_hour <= 17:
                return base_value * random.uniform(1.0, 1.2)  # Daytime increase

        elif stream_type == DataStreamType.STRESS_LEVEL:
            # Higher during work hours
            if 9 <= current_hour <= 17:
                return min(1.0, base_value * random.uniform(1.1, 1.4))
            elif 22 <= current_hour or current_hour <= 6:
                return base_value * random.uniform(0.5, 0.8)

        return base_value

    def analyze_sleep_data(self, user_id: str, date: datetime) -> SleepAnalysis:
        """Analyze sleep data from connected devices"""

        # Get sleep-capable devices for user
        sleep_devices = [
            device for device in self.connected_devices.values()
            if device.user_id == user_id and DataStreamType.SLEEP_STAGES in device.data_streams
        ]

        if not sleep_devices:
            return self._generate_simulated_sleep_analysis(user_id, date)

        # Use primary sleep device (first available)
        primary_device = sleep_devices[0]

        # Generate comprehensive sleep analysis
        sleep_analysis = SleepAnalysis(
            user_id=user_id,
            device_id=primary_device.device_id,
            sleep_date=date
        )

        # Simulate realistic sleep metrics
        sleep_analysis.bedtime = date.replace(hour=22, minute=random.randint(0, 60))
        sleep_analysis.sleep_onset = sleep_analysis.bedtime + timedelta(minutes=random.randint(5, 45))
        sleep_analysis.wake_time = sleep_analysis.bedtime + timedelta(hours=random.uniform(6.5, 9.0))

        total_time_in_bed = (sleep_analysis.wake_time - sleep_analysis.bedtime).total_seconds() / 3600
        sleep_analysis.total_sleep_time = total_time_in_bed * random.uniform(0.85, 0.95)
        sleep_analysis.sleep_efficiency = sleep_analysis.total_sleep_time / total_time_in_bed

        # Sleep stage distribution
        total_sleep_minutes = sleep_analysis.total_sleep_time * 60
        sleep_analysis.deep_sleep_minutes = total_sleep_minutes * random.uniform(0.15, 0.25)
        sleep_analysis.rem_sleep_minutes = total_sleep_minutes * random.uniform(0.20, 0.30)
        sleep_analysis.light_sleep_minutes = total_sleep_minutes - sleep_analysis.deep_sleep_minutes - sleep_analysis.rem_sleep_minutes

        # Calculate sleep score
        sleep_analysis.sleep_score = self._calculate_sleep_score(sleep_analysis)

        # Store analysis
        if user_id not in self.sleep_analyses:
            self.sleep_analyses[user_id] = []
        self.sleep_analyses[user_id].append(sleep_analysis)

        return sleep_analysis

    def _generate_simulated_sleep_analysis(self, user_id: str, date: datetime) -> SleepAnalysis:
        """Generate simulated sleep analysis when no devices available"""
        return SleepAnalysis(
            user_id=user_id,
            device_id="simulated",
            sleep_date=date,
            total_sleep_time=random.uniform(6.5, 8.5),
            sleep_efficiency=random.uniform(0.80, 0.95),
            sleep_score=random.uniform(70, 95)
        )

    def _calculate_sleep_score(self, analysis: SleepAnalysis) -> float:
        """Calculate overall sleep score"""

        # Efficiency score (40% weight)
        efficiency_score = analysis.sleep_efficiency * 100

        # Duration score (30% weight)
        ideal_duration = 8.0
        duration_score = max(0, 100 - abs(analysis.total_sleep_time - ideal_duration) * 10)

        # Deep sleep score (20% weight)
        ideal_deep_percentage = 0.20
        actual_deep_percentage = analysis.deep_sleep_minutes / (analysis.total_sleep_time * 60)
        deep_score = max(0, 100 - abs(actual_deep_percentage - ideal_deep_percentage) * 200)

        # Wake episodes score (10% weight)
        wake_score = max(0, 100 - analysis.wake_episodes * 15)

        total_score = (efficiency_score * 0.4 + duration_score * 0.3 +
                      deep_score * 0.2 + wake_score * 0.1)

        return round(total_score, 1)

    def generate_activity_summary(self, user_id: str, date: datetime) -> ActivitySummary:
        """Generate daily activity summary from wearable data"""

        # Get activity-capable devices
        activity_devices = [
            device for device in self.connected_devices.values()
            if device.user_id == user_id and DataStreamType.STEPS in device.data_streams
        ]

        summary = ActivitySummary(
            user_id=user_id,
            date=date
        )

        if activity_devices:
            # Aggregate data from devices
            device_readings = []
            for device in activity_devices:
                readings = self.sensor_readings.get(device.device_id, [])
                device_readings.extend([r for r in readings if r.timestamp.date() == date.date()])

            # Calculate metrics from readings
            summary = self._calculate_activity_metrics(summary, device_readings)
        else:
            # Generate simulated data
            summary = self._generate_simulated_activity(summary)

        # Store summary
        if user_id not in self.activity_summaries:
            self.activity_summaries[user_id] = []
        self.activity_summaries[user_id].append(summary)

        return summary

    def _calculate_activity_metrics(self, summary: ActivitySummary, readings: List[SensorReading]) -> ActivitySummary:
        """Calculate activity metrics from sensor readings"""

        # Aggregate steps
        step_readings = [r for r in readings if r.data_stream == DataStreamType.STEPS]
        if step_readings:
            summary.total_steps = int(sum(r.value for r in step_readings))

        # Calculate other metrics based on steps and heart rate
        if summary.total_steps > 0:
            summary.distance_km = summary.total_steps * 0.0008  # Average step length
            summary.active_minutes = min(240, summary.total_steps // 100)  # Rough estimation
            summary.calories_burned = 1800 + (summary.total_steps * 0.04)  # Base + activity calories

        # Stress analysis
        stress_readings = [r for r in readings if r.data_stream == DataStreamType.STRESS_LEVEL]
        if stress_readings:
            summary.stress_average = sum(r.value for r in stress_readings) / len(stress_readings)

        return summary

    def _generate_simulated_activity(self, summary: ActivitySummary) -> ActivitySummary:
        """Generate simulated activity data"""
        summary.total_steps = random.randint(3000, 15000)
        summary.active_minutes = random.randint(20, 120)
        summary.calories_burned = random.randint(1800, 3000)
        summary.distance_km = summary.total_steps * 0.0008
        summary.stress_average = random.uniform(0.2, 0.7)
        summary.recovery_score = random.uniform(60, 95)
        summary.energy_level = random.uniform(0.4, 0.9)
        return summary

    def collect_environmental_data(self, user_id: str, location: str = "home") -> EnvironmentalData:
        """Collect environmental data from smart home sensors"""

        # Simulate environmental data collection
        env_data = EnvironmentalData(
            user_id=user_id,
            location=location,
            air_quality_index=random.uniform(20, 150),
            temperature=random.uniform(18, 26),
            humidity=random.uniform(30, 70),
            light_level=random.uniform(50, 800),
            noise_level=random.uniform(25, 65),
            uv_index=random.uniform(0, 8),
            pollen_count=random.uniform(0, 100),
            weather_conditions=random.choice(["clear", "cloudy", "rainy", "sunny"])
        )

        # Store environmental data
        if user_id not in self.environmental_data:
            self.environmental_data[user_id] = []
        self.environmental_data[user_id].append(env_data)

        return env_data

    def extract_digital_biomarkers(self, user_id: str, smartphone_data: Dict[str, Any]) -> List[DigitalBiomarker]:
        """Extract digital biomarkers from smartphone usage patterns"""

        biomarkers = []

        # Keystroke dynamics for depression screening
        if "keystroke_data" in smartphone_data:
            typing_speed = smartphone_data["keystroke_data"].get("words_per_minute", 40)
            dwell_time_variance = smartphone_data["keystroke_data"].get("dwell_time_variance", 0.1)

            # Slower typing and higher variance may indicate depression
            depression_score = max(0, (45 - typing_speed) / 45) + min(1, dwell_time_variance * 5)
            depression_score = min(1.0, depression_score / 2)

            biomarkers.append(DigitalBiomarker(
                user_id=user_id,
                biomarker_type="keystroke_dynamics",
                value=depression_score,
                confidence_score=0.72,
                data_source="smartphone",
                clinical_relevance="depression_screening",
                raw_features={
                    "typing_speed": typing_speed,
                    "dwell_time_variance": dwell_time_variance
                }
            ))

        # Voice pattern analysis
        if "voice_data" in smartphone_data:
            call_frequency = smartphone_data["voice_data"].get("calls_per_day", 5)
            call_duration_avg = smartphone_data["voice_data"].get("avg_call_duration", 3.0)

            # Reduced social communication may indicate isolation
            social_isolation_score = max(0, (5 - call_frequency) / 5) + max(0, (3 - call_duration_avg) / 3)
            social_isolation_score = min(1.0, social_isolation_score / 2)

            biomarkers.append(DigitalBiomarker(
                user_id=user_id,
                biomarker_type="voice_communication_patterns",
                value=social_isolation_score,
                confidence_score=0.68,
                data_source="smartphone",
                clinical_relevance="social_isolation_screening",
                raw_features={
                    "call_frequency": call_frequency,
                    "call_duration": call_duration_avg
                }
            ))

        # Screen time patterns
        if "screen_time" in smartphone_data:
            daily_screen_hours = smartphone_data["screen_time"].get("daily_hours", 6)
            late_night_usage = smartphone_data["screen_time"].get("usage_after_midnight", 0.5)

            # Excessive screen time or late night usage patterns
            digital_wellness_score = 0
            if daily_screen_hours > 8:
                digital_wellness_score += (daily_screen_hours - 8) / 8
            if late_night_usage > 1.0:
                digital_wellness_score += late_night_usage / 3

            digital_wellness_score = min(1.0, digital_wellness_score)

            biomarkers.append(DigitalBiomarker(
                user_id=user_id,
                biomarker_type="screen_time_patterns",
                value=digital_wellness_score,
                confidence_score=0.65,
                data_source="smartphone",
                clinical_relevance="digital_wellness_screening",
                raw_features={
                    "daily_hours": daily_screen_hours,
                    "late_night_usage": late_night_usage
                }
            ))

        # Movement patterns (from accelerometer)
        if "movement_data" in smartphone_data:
            daily_movement_variance = smartphone_data["movement_data"].get("movement_variance", 0.5)
            location_entropy = smartphone_data["movement_data"].get("location_entropy", 2.0)

            # Reduced movement variance may indicate depression or anxiety
            movement_pattern_score = max(0, (0.8 - daily_movement_variance) / 0.8)
            if location_entropy < 1.5:  # Very low location diversity
                movement_pattern_score += 0.3

            movement_pattern_score = min(1.0, movement_pattern_score)

            biomarkers.append(DigitalBiomarker(
                user_id=user_id,
                biomarker_type="movement_patterns",
                value=movement_pattern_score,
                confidence_score=0.58,
                data_source="smartphone",
                clinical_relevance="behavioral_pattern_screening",
                raw_features={
                    "movement_variance": daily_movement_variance,
                    "location_entropy": location_entropy
                }
            ))

        # Store biomarkers
        if user_id not in self.digital_biomarkers:
            self.digital_biomarkers[user_id] = []
        self.digital_biomarkers[user_id].extend(biomarkers)

        return biomarkers

    def analyze_circadian_rhythm(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's circadian rhythm from multiple data sources"""

        # Get recent sleep data
        sleep_data = self.sleep_analyses.get(user_id, [])
        recent_sleep = [s for s in sleep_data if s.sleep_date >= datetime.now() - timedelta(days=7)]

        # Get light exposure data
        light_readings = []
        for device_id, readings in self.sensor_readings.items():
            device = self.connected_devices.get(device_id)
            if device and device.user_id == user_id:
                light_readings.extend([
                    r for r in readings
                    if r.data_stream == DataStreamType.AMBIENT_LIGHT and
                    r.timestamp >= datetime.now() - timedelta(days=7)
                ])

        analysis = {
            "user_id": user_id,
            "analysis_date": datetime.now().isoformat(),
            "sleep_regularity": self._calculate_sleep_regularity(recent_sleep),
            "light_exposure_pattern": self._analyze_light_exposure(light_readings),
            "circadian_misalignment": self._detect_circadian_misalignment(recent_sleep, light_readings),
            "recommendations": self._generate_circadian_recommendations(recent_sleep, light_readings)
        }

        return analysis

    def _calculate_sleep_regularity(self, sleep_data: List[SleepAnalysis]) -> Dict[str, Any]:
        """Calculate sleep regularity metrics"""
        if len(sleep_data) < 3:
            return {"insufficient_data": True}

        bedtimes = [s.bedtime.hour + s.bedtime.minute/60.0 for s in sleep_data]
        wake_times = [s.wake_time.hour + s.wake_time.minute/60.0 for s in sleep_data]

        bedtime_variance = np.var(bedtimes) if len(bedtimes) > 1 else 0
        wake_variance = np.var(wake_times) if len(wake_times) > 1 else 0

        regularity_score = max(0, 1 - (bedtime_variance + wake_variance) / 4)

        return {
            "regularity_score": round(regularity_score, 2),
            "bedtime_variance_hours": round(bedtime_variance, 2),
            "wake_time_variance_hours": round(wake_variance, 2),
            "average_bedtime": f"{int(np.mean(bedtimes))}:{int((np.mean(bedtimes) % 1) * 60):02d}",
            "average_wake_time": f"{int(np.mean(wake_times))}:{int((np.mean(wake_times) % 1) * 60):02d}"
        }

    def _analyze_light_exposure(self, light_readings: List[SensorReading]) -> Dict[str, Any]:
        """Analyze light exposure patterns"""
        if not light_readings:
            return {"insufficient_data": True}

        # Group by time of day
        morning_light = [r.value for r in light_readings if 6 <= r.timestamp.hour <= 10]
        evening_light = [r.value for r in light_readings if 18 <= r.timestamp.hour <= 22]
        night_light = [r.value for r in light_readings if r.timestamp.hour >= 22 or r.timestamp.hour <= 6]

        return {
            "morning_light_avg": round(np.mean(morning_light), 1) if morning_light else 0,
            "evening_light_avg": round(np.mean(evening_light), 1) if evening_light else 0,
            "night_light_avg": round(np.mean(night_light), 1) if night_light else 0,
            "light_contrast_ratio": round(np.mean(morning_light) / max(np.mean(night_light), 1), 2) if morning_light and night_light else 0
        }

    def _detect_circadian_misalignment(self, sleep_data: List[SleepAnalysis], light_readings: List[SensorReading]) -> Dict[str, Any]:
        """Detect circadian rhythm misalignment"""

        misalignment_indicators = []
        severity_score = 0

        # Check for irregular sleep patterns
        if sleep_data:
            sleep_regularity = self._calculate_sleep_regularity(sleep_data)
            if sleep_regularity.get("regularity_score", 1) < 0.7:
                misalignment_indicators.append("irregular_sleep_schedule")
                severity_score += 0.3

        # Check for poor light exposure
        if light_readings:
            light_analysis = self._analyze_light_exposure(light_readings)
            if light_analysis.get("light_contrast_ratio", 0) < 3:
                misalignment_indicators.append("poor_light_contrast")
                severity_score += 0.2

            if light_analysis.get("night_light_avg", 0) > 50:
                misalignment_indicators.append("excessive_night_light")
                severity_score += 0.2

        # Check for social jetlag (difference between weekday and weekend sleep)
        if len(sleep_data) >= 7:
            weekday_sleep = [s for s in sleep_data if s.sleep_date.weekday() < 5]
            weekend_sleep = [s for s in sleep_data if s.sleep_date.weekday() >= 5]

            if weekday_sleep and weekend_sleep:
                weekday_avg = np.mean([s.bedtime.hour for s in weekday_sleep])
                weekend_avg = np.mean([s.bedtime.hour for s in weekend_sleep])

                if abs(weekday_avg - weekend_avg) > 1.5:  # More than 1.5 hour difference
                    misalignment_indicators.append("social_jetlag")
                    severity_score += 0.3

        return {
            "misalignment_detected": len(misalignment_indicators) > 0,
            "severity_score": round(min(1.0, severity_score), 2),
            "indicators": misalignment_indicators,
            "risk_level": "high" if severity_score > 0.6 else "moderate" if severity_score > 0.3 else "low"
        }

    def _generate_circadian_recommendations(self, sleep_data: List[SleepAnalysis], light_readings: List[SensorReading]) -> List[str]:
        """Generate personalized circadian rhythm recommendations"""
        recommendations = []

        # Analyze current patterns
        sleep_regularity = self._calculate_sleep_regularity(sleep_data)
        light_analysis = self._analyze_light_exposure(light_readings)
        misalignment = self._detect_circadian_misalignment(sleep_data, light_readings)

        # Sleep schedule recommendations
        if sleep_regularity.get("regularity_score", 1) < 0.8:
            recommendations.extend([
                "Maintain consistent bedtime and wake time daily",
                "Set sleep schedule reminders on your devices",
                "Avoid sleeping in more than 1 hour on weekends"
            ])

        # Light exposure recommendations
        if light_analysis.get("morning_light_avg", 0) < 200:
            recommendations.append("Get 15-30 minutes of bright light exposure within 1 hour of waking")

        if light_analysis.get("night_light_avg", 0) > 30:
            recommendations.extend([
                "Dim lights 2-3 hours before bedtime",
                "Use blue light filters on devices after sunset",
                "Consider blackout curtains for better sleep environment"
            ])

        # Activity timing recommendations
        recommendations.extend([
            "Avoid caffeine 6 hours before bedtime",
            "Finish eating 3 hours before sleep",
            "Exercise regularly but not within 4 hours of bedtime"
        ])

        return recommendations

    def get_user_device_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive device dashboard for user"""

        user_devices = [d for d in self.connected_devices.values() if d.user_id == user_id]

        dashboard = {
            "user_id": user_id,
            "total_devices": len(user_devices),
            "device_summary": [
                {
                    "device_id": device.device_id,
                    "type": device.device_type.value,
                    "brand": device.brand.value,
                    "model": device.model,
                    "status": device.connection_status.value,
                    "battery_level": device.battery_level,
                    "last_sync": device.last_sync.isoformat(),
                    "data_streams": [stream.value for stream in device.data_streams]
                }
                for device in user_devices
            ],
            "recent_insights": self._generate_recent_insights(user_id),
            "data_quality_score": self._calculate_data_quality(user_id),
            "privacy_settings": self._get_privacy_settings(user_id),
            "sync_status": self._get_sync_status(user_devices)
        }

        return dashboard

    def _generate_recent_insights(self, user_id: str) -> List[str]:
        """Generate recent insights from device data"""
        insights = []

        # Sleep insights
        recent_sleep = self.sleep_analyses.get(user_id, [])
        if recent_sleep:
            avg_score = np.mean([s.sleep_score for s in recent_sleep[-7:]])
            if avg_score > 85:
                insights.append("Your sleep quality has been excellent this week")
            elif avg_score < 70:
                insights.append("Your sleep quality could be improved - consider adjusting your bedtime routine")

        # Activity insights
        recent_activity = self.activity_summaries.get(user_id, [])
        if recent_activity:
            avg_steps = np.mean([a.total_steps for a in recent_activity[-7:]])
            if avg_steps > 10000:
                insights.append("You're consistently hitting your step goals - great job!")
            elif avg_steps < 5000:
                insights.append("Try to increase daily movement - even short walks can help")

        # Environmental insights
        recent_env = self.environmental_data.get(user_id, [])
        if recent_env:
            avg_aqi = np.mean([e.air_quality_index for e in recent_env[-3:]])
            if avg_aqi > 100:
                insights.append("Air quality has been poor - consider indoor activities and air purification")

        return insights

    def _calculate_data_quality(self, user_id: str) -> float:
        """Calculate overall data quality score"""
        quality_factors = []

        # Device connectivity
        user_devices = [d for d in self.connected_devices.values() if d.user_id == user_id]
        if user_devices:
            connected_ratio = len([d for d in user_devices if d.connection_status == ConnectionStatus.CONNECTED]) / len(user_devices)
            quality_factors.append(connected_ratio)

        # Data recency
        all_readings = []
        for device in user_devices:
            all_readings.extend(self.sensor_readings.get(device.device_id, []))

        if all_readings:
            recent_readings = len([r for r in all_readings if r.timestamp >= datetime.now() - timedelta(hours=24)])
            recency_score = min(1.0, recent_readings / 50)  # Expect at least 50 readings per day
            quality_factors.append(recency_score)

        # Reading quality scores
        if all_readings:
            avg_quality = np.mean([r.quality_score for r in all_readings])
            quality_factors.append(avg_quality)

        return round(np.mean(quality_factors) if quality_factors else 0.5, 2)

    def _get_privacy_settings(self, user_id: str) -> Dict[str, Any]:
        """Get user's privacy settings for device data"""
        return {
            "data_sharing_enabled": True,
            "anonymized_research_participation": True,
            "location_tracking": False,
            "third_party_integrations": True,
            "data_retention_days": 90,
            "export_available": True
        }

    def _get_sync_status(self, devices: List[WearableDevice]) -> Dict[str, Any]:
        """Get synchronization status for devices"""
        if not devices:
            return {"status": "no_devices"}

        last_sync_times = [d.last_sync for d in devices]
        oldest_sync = min(last_sync_times)
        newest_sync = max(last_sync_times)

        sync_lag = (datetime.now() - oldest_sync).total_seconds() / 3600  # Hours

        return {
            "overall_status": "good" if sync_lag < 2 else "warning" if sync_lag < 6 else "error",
            "oldest_sync_hours_ago": round(sync_lag, 1),
            "devices_synced_recently": len([d for d in devices if (datetime.now() - d.last_sync).total_seconds() < 3600]),
            "sync_issues": [d.device_id for d in devices if (datetime.now() - d.last_sync).total_seconds() > 6 * 3600]
        }

    def get_platform_statistics(self) -> Dict[str, Any]:
        """Get platform-wide IoT and wearable statistics"""
        total_devices = len(self.connected_devices)
        connected_devices = len([d for d in self.connected_devices.values() if d.connection_status == ConnectionStatus.CONNECTED])

        # Device type distribution
        device_types = {}
        for device in self.connected_devices.values():
            device_type = device.device_type.value
            device_types[device_type] = device_types.get(device_type, 0) + 1

        # Brand distribution
        brand_distribution = {}
        for device in self.connected_devices.values():
            brand = device.brand.value
            brand_distribution[brand] = brand_distribution.get(brand, 0) + 1

        return {
            "total_registered_devices": total_devices,
            "connected_devices": connected_devices,
            "connection_rate": round(connected_devices / total_devices, 2) if total_devices > 0 else 0,
            "device_type_distribution": device_types,
            "brand_distribution": brand_distribution,
            "total_sensor_readings": sum(len(readings) for readings in self.sensor_readings.values()),
            "active_users_with_devices": len(set(d.user_id for d in self.connected_devices.values())),
            "average_devices_per_user": round(total_devices / len(set(d.user_id for d in self.connected_devices.values())), 1) if self.connected_devices else 0,
            "data_quality_average": round(np.mean([self._calculate_data_quality(user_id) for user_id in set(d.user_id for d in self.connected_devices.values())]), 2),
            "environmental_monitoring_locations": len(set(env.location for env_list in self.environmental_data.values() for env in env_list))
        }

# Global instance
iot_wearable_manager = IoTWearableManager()