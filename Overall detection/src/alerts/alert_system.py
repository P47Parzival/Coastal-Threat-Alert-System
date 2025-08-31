"""
Coastal Threat Alert System
Handles alert generation, notification distribution, and emergency response coordination
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import aiohttp
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from src.anomaly_detection.sam2_detector import AnomalyDetection

logger = logging.getLogger(__name__)

Base = declarative_base()

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    STORM_SURGE = "storm_surge"
    COASTAL_EROSION = "coastal_erosion"
    SEA_LEVEL_RISE = "sea_level_rise"
    OIL_SPILL = "oil_spill"
    ILLEGAL_DUMPING = "illegal_dumping"
    ALGAL_BLOOM = "algal_bloom"
    EXTREME_WEATHER = "extreme_weather"
    UNAUTHORIZED_CONSTRUCTION = "unauthorized_construction"
    TSUNAMI_WARNING = "tsunami_warning"
    POLLUTION_EVENT = "pollution_event"

@dataclass
class Alert:
    """Structure for alert information"""
    alert_id: str
    timestamp: datetime
    alert_type: AlertType
    severity: AlertSeverity
    location: Tuple[float, float]  # lat, lon
    title: str
    description: str
    recommended_actions: List[str]
    affected_areas: List[str]
    expires_at: Optional[datetime]
    source_data: Dict[str, Any]
    is_active: bool = True

@dataclass
class NotificationChannel:
    """Structure for notification channels"""
    channel_type: str  # sms, email, push, webhook
    target: str  # phone number, email, device token, URL
    is_active: bool = True
    alert_types: List[AlertType] = None  # None means all types
    min_severity: AlertSeverity = AlertSeverity.LOW

@dataclass
class Stakeholder:
    """Structure for stakeholder information"""
    stakeholder_id: str
    name: str
    organization: str
    role: str  # emergency_manager, fisherman, ngo, government
    contact_info: Dict[str, str]
    notification_channels: List[NotificationChannel]
    geographic_areas: List[Tuple[float, float, float]]  # lat, lon, radius

# Database Models
class AlertDB(Base):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    alert_id = Column(String(100), unique=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    recommended_actions = Column(Text)  # JSON string
    affected_areas = Column(Text)  # JSON string
    expires_at = Column(DateTime)
    source_data = Column(Text)  # JSON string
    is_active = Column(Boolean, default=True)

class NotificationLogDB(Base):
    __tablename__ = 'notification_log'
    
    id = Column(Integer, primary_key=True)
    alert_id = Column(String(100), nullable=False)
    channel_type = Column(String(50), nullable=False)
    target = Column(String(200), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False)  # sent, failed, delivered
    message = Column(Text)
    error_message = Column(Text)

class CoastalAlertSystem:
    """Main alert system for coastal threats"""
    
    def __init__(self):
        # Use SQLite as fallback if no database URL is configured
        try:
            database_url = getattr(settings, 'database_url', None)
            if not database_url:
                database_url = "sqlite:///./coastal_alerts.db"
                logger.warning("No DATABASE_URL configured, using SQLite fallback")
            
            self.engine = create_engine(database_url)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            # Create in-memory SQLite database as last resort
            self.engine = create_engine("sqlite:///:memory:")
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Using in-memory SQLite database")
        
        # Initialize notification services (with fallback for missing credentials)
        try:
            self.twilio_client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        except Exception as e:
            logger.warning(f"Twilio client initialization failed: {e}")
            self.twilio_client = None
        
        # Alert thresholds and rules
        self.alert_rules = self._initialize_alert_rules()
        
        # Stakeholders (in practice, this would be loaded from database)
        self.stakeholders = self._initialize_stakeholders()
        
        # Active alerts cache
        self.active_alerts = {}
    
    def _initialize_alert_rules(self) -> Dict[str, Dict]:
        """Initialize alert generation rules"""
        return {
            'sea_level_rise': {
                'threshold': getattr(settings, 'sea_level_rise_threshold', 0.5),
                'severity_levels': {
                    0.3: AlertSeverity.LOW,
                    0.5: AlertSeverity.MEDIUM,
                    0.8: AlertSeverity.HIGH,
                    1.0: AlertSeverity.CRITICAL
                }
            },
            'wave_height': {
                'threshold': getattr(settings, 'wave_height_threshold', 3.0),
                'severity_levels': {
                    2.0: AlertSeverity.LOW,
                    3.0: AlertSeverity.MEDIUM,
                    4.5: AlertSeverity.HIGH,
                    6.0: AlertSeverity.CRITICAL
                }
            },
            'wind_speed': {
                'threshold': getattr(settings, 'wind_speed_threshold', 25.0),
                'severity_levels': {
                    20.0: AlertSeverity.LOW,
                    25.0: AlertSeverity.MEDIUM,
                    35.0: AlertSeverity.HIGH,
                    50.0: AlertSeverity.CRITICAL
                }
            },
            'pollution': {
                'threshold': getattr(settings, 'pollution_threshold', 100),
                'severity_levels': {
                    80: AlertSeverity.LOW,
                    100: AlertSeverity.MEDIUM,
                    150: AlertSeverity.HIGH,
                    200: AlertSeverity.CRITICAL
                }
            }
        }
    
    def _initialize_stakeholders(self) -> List[Stakeholder]:
        """Initialize stakeholder list (example data)"""
        return [
            Stakeholder(
                stakeholder_id="emergency_dept_001",
                name="Coastal Emergency Department",
                organization="City Government",
                role="emergency_manager",
                contact_info={
                    "email": "emergency@city.gov",
                    "phone": "+1234567890",
                    "office": "+1234567891"
                },
                notification_channels=[
                    NotificationChannel("sms", "+1234567890", True, None, AlertSeverity.MEDIUM),
                    NotificationChannel("email", "emergency@city.gov", True, None, AlertSeverity.LOW)
                ],
                geographic_areas=[
                    (getattr(settings, 'monitoring_area_lat_min', 12.0), getattr(settings, 'monitoring_area_lon_min', 80.0), 10.0)
                ]
            ),
            Stakeholder(
                stakeholder_id="fishermen_union_001",
                name="Local Fishermen Union",
                organization="Fishermen's Association",
                role="fisherman",
                contact_info={
                    "email": "union@fishermen.org",
                    "phone": "+1234567892"
                },
                notification_channels=[
                    NotificationChannel("sms", "+1234567892", True, 
                                      [AlertType.STORM_SURGE, AlertType.EXTREME_WEATHER], 
                                      AlertSeverity.LOW)
                ],
                geographic_areas=[
                    (getattr(settings, 'monitoring_area_lat_min', 12.0), getattr(settings, 'monitoring_area_lon_min', 80.0), 15.0)
                ]
            ),
            Stakeholder(
                stakeholder_id="env_ngo_001",
                name="Coastal Conservation NGO",
                organization="Environmental Watch",
                role="ngo",
                contact_info={
                    "email": "alerts@envwatch.org",
                    "phone": "+1234567893"
                },
                notification_channels=[
                    NotificationChannel("email", "alerts@envwatch.org", True,
                                      [AlertType.OIL_SPILL, AlertType.POLLUTION_EVENT, 
                                       AlertType.ILLEGAL_DUMPING], AlertSeverity.LOW)
                ],
                geographic_areas=[
                    (getattr(settings, 'monitoring_area_lat_max', 13.0), getattr(settings, 'monitoring_area_lon_max', 81.0), 20.0)
                ]
            )
        ]
    
    async def process_sensor_data(self, sensor_data: Dict[str, Any]) -> List[Alert]:
        """Process sensor data and generate alerts if thresholds are exceeded"""
        alerts = []
        
        try:
            measurement_type = sensor_data.get('measurement_type')
            value = sensor_data.get('value', 0)
            location = (sensor_data.get('latitude', 0), sensor_data.get('longitude', 0))
            timestamp = datetime.fromisoformat(sensor_data.get('timestamp', datetime.now().isoformat()))
            
            # Check alert rules
            if measurement_type in self.alert_rules:
                rule = self.alert_rules[measurement_type]
                
                if value >= rule['threshold']:
                    # Determine severity
                    severity = AlertSeverity.LOW
                    for threshold, sev in rule['severity_levels'].items():
                        if value >= threshold:
                            severity = sev
                    
                    # Generate alert
                    alert = await self._generate_environmental_alert(
                        measurement_type, value, location, timestamp, severity, sensor_data
                    )
                    
                    if alert:
                        alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error processing sensor data: {e}")
            return []
    
    async def process_anomaly_detection(self, anomaly: AnomalyDetection) -> Optional[Alert]:
        """Process anomaly detection and generate alert"""
        try:
            # Map anomaly types to alert types
            anomaly_to_alert_map = {
                'oil_spill': AlertType.OIL_SPILL,
                'illegal_dumping': AlertType.ILLEGAL_DUMPING,
                'algal_bloom': AlertType.ALGAL_BLOOM,
                'unauthorized_construction': AlertType.UNAUTHORIZED_CONSTRUCTION,
                'pollution_event': AlertType.POLLUTION_EVENT
            }
            
            alert_type = anomaly_to_alert_map.get(anomaly.anomaly_type, AlertType.POLLUTION_EVENT)
            
            # Map severity
            severity_map = {
                'low': AlertSeverity.LOW,
                'medium': AlertSeverity.MEDIUM,
                'high': AlertSeverity.HIGH,
                'critical': AlertSeverity.CRITICAL
            }
            
            severity = severity_map.get(anomaly.severity, AlertSeverity.MEDIUM)
            
            # Generate alert
            alert_id = f"ANOM_{anomaly.timestamp.strftime('%Y%m%d_%H%M%S')}_{anomaly.anomaly_type}"
            
            alert = Alert(
                alert_id=alert_id,
                timestamp=anomaly.timestamp,
                alert_type=alert_type,
                severity=severity,
                location=anomaly.location,
                title=f"{anomaly.anomaly_type.replace('_', ' ').title()} Detected",
                description=anomaly.description,
                recommended_actions=self._get_recommended_actions(alert_type, severity),
                affected_areas=self._calculate_affected_areas(anomaly.location, alert_type),
                expires_at=datetime.now() + timedelta(hours=24),
                source_data={
                    'detection_confidence': anomaly.confidence,
                    'bounding_box': anomaly.bounding_box,
                    'anomaly_type': anomaly.anomaly_type
                }
            )
            
            # Store and distribute alert
            await self._store_alert(alert)
            await self._distribute_alert(alert)
            
            return alert
            
        except Exception as e:
            logger.error(f"Error processing anomaly detection: {e}")
            return None
    
    async def _generate_environmental_alert(self, 
                                          measurement_type: str,
                                          value: float,
                                          location: Tuple[float, float],
                                          timestamp: datetime,
                                          severity: AlertSeverity,
                                          source_data: Dict) -> Optional[Alert]:
        """Generate environmental alert based on sensor measurements"""
        
        # Map measurement types to alert types
        measurement_to_alert_map = {
            'sea_level_rise': AlertType.SEA_LEVEL_RISE,
            'wave_height': AlertType.STORM_SURGE,
            'wind_speed': AlertType.EXTREME_WEATHER,
            'pollution': AlertType.POLLUTION_EVENT
        }
        
        alert_type = measurement_to_alert_map.get(measurement_type, AlertType.POLLUTION_EVENT)
        
        alert_id = f"ENV_{timestamp.strftime('%Y%m%d_%H%M%S')}_{measurement_type}"
        
        # Generate appropriate title and description
        titles = {
            'sea_level_rise': f"Sea Level Rise Alert - {value:.2f}m above normal",
            'wave_height': f"High Wave Alert - {value:.2f}m waves detected",
            'wind_speed': f"High Wind Alert - {value:.1f} m/s winds",
            'pollution': f"Pollution Alert - Index {value:.0f}"
        }
        
        descriptions = {
            'sea_level_rise': f"Sea level has risen to {value:.2f}m above normal levels at coordinates {location[0]:.4f}, {location[1]:.4f}. This may indicate storm surge or long-term sea level rise.",
            'wave_height': f"Wave heights of {value:.2f}m have been detected at coordinates {location[0]:.4f}, {location[1]:.4f}. This poses risks to coastal areas and marine activities.",
            'wind_speed': f"Wind speeds of {value:.1f} m/s have been recorded at coordinates {location[0]:.4f}, {location[1]:.4f}. This may affect marine operations and coastal safety.",
            'pollution': f"Pollution levels have reached index {value:.0f} at coordinates {location[0]:.4f}, {location[1]:.4f}. This may pose health and environmental risks."
        }
        
        alert = Alert(
            alert_id=alert_id,
            timestamp=timestamp,
            alert_type=alert_type,
            severity=severity,
            location=location,
            title=titles.get(measurement_type, f"Environmental Alert - {measurement_type}"),
            description=descriptions.get(measurement_type, f"Abnormal {measurement_type} detected: {value}"),
            recommended_actions=self._get_recommended_actions(alert_type, severity),
            affected_areas=self._calculate_affected_areas(location, alert_type),
            expires_at=datetime.now() + timedelta(hours=12),
            source_data=source_data
        )
        
        # Store and distribute alert
        await self._store_alert(alert)
        await self._distribute_alert(alert)
        
        return alert
    
    def _get_recommended_actions(self, alert_type: AlertType, severity: AlertSeverity) -> List[str]:
        """Get recommended actions based on alert type and severity"""
        
        actions = {
            AlertType.STORM_SURGE: {
                AlertSeverity.LOW: [
                    "Monitor coastal conditions",
                    "Secure loose items near waterfront",
                    "Check emergency supplies"
                ],
                AlertSeverity.MEDIUM: [
                    "Avoid low-lying coastal areas",
                    "Secure boats and marine equipment",
                    "Prepare for possible evacuation"
                ],
                AlertSeverity.HIGH: [
                    "Evacuate low-lying areas immediately",
                    "Seek higher ground",
                    "Avoid driving through flooded areas"
                ],
                AlertSeverity.CRITICAL: [
                    "IMMEDIATE EVACUATION REQUIRED",
                    "Move to designated emergency shelters",
                    "Follow official emergency instructions"
                ]
            },
            AlertType.OIL_SPILL: {
                AlertSeverity.LOW: [
                    "Report spill to authorities",
                    "Avoid affected water areas",
                    "Do not touch contaminated materials"
                ],
                AlertSeverity.MEDIUM: [
                    "Evacuate immediate spill area",
                    "Close water intakes",
                    "Deploy containment measures"
                ],
                AlertSeverity.HIGH: [
                    "Activate emergency response teams",
                    "Establish exclusion zones",
                    "Begin wildlife protection measures"
                ],
                AlertSeverity.CRITICAL: [
                    "Full emergency response activation",
                    "Evacuate coastal communities",
                    "Implement marine traffic restrictions"
                ]
            },
            AlertType.ILLEGAL_DUMPING: [
                "Report to environmental authorities",
                "Document with photos/video",
                "Avoid direct contact with materials",
                "Secure area if safe to do so"
            ]
        }
        
        if alert_type in actions:
            if isinstance(actions[alert_type], dict):
                return actions[alert_type].get(severity, ["Monitor situation closely"])
            else:
                return actions[alert_type]
        
        return ["Monitor situation and follow official guidance"]
    
    def _calculate_affected_areas(self, location: Tuple[float, float], alert_type: AlertType) -> List[str]:
        """Calculate potentially affected areas based on location and alert type"""
        
        # This would typically use GIS data and detailed geographic information
        # For now, we'll use simple distance-based calculations
        
        lat, lon = location
        
        # Example area calculations (would be much more sophisticated in practice)
        if alert_type in [AlertType.STORM_SURGE, AlertType.TSUNAMI_WARNING]:
            radius = 5.0  # km
        elif alert_type in [AlertType.OIL_SPILL, AlertType.POLLUTION_EVENT]:
            radius = 2.0  # km
        else:
            radius = 1.0  # km
        
        # Generate area descriptions
        areas = [
            f"Coastal area within {radius}km of {lat:.3f}, {lon:.3f}",
            "Nearby fishing communities",
            "Marine protected areas in vicinity"
        ]
        
        return areas
    
    async def _store_alert(self, alert: Alert):
        """Store alert in database"""
        session = self.Session()
        try:
            db_alert = AlertDB(
                alert_id=alert.alert_id,
                timestamp=alert.timestamp,
                alert_type=alert.alert_type.value,
                severity=alert.severity.value,
                latitude=alert.location[0],
                longitude=alert.location[1],
                title=alert.title,
                description=alert.description,
                recommended_actions=json.dumps(alert.recommended_actions),
                affected_areas=json.dumps(alert.affected_areas),
                expires_at=alert.expires_at,
                source_data=json.dumps(alert.source_data),
                is_active=alert.is_active
            )
            
            session.add(db_alert)
            session.commit()
            
            # Add to active alerts cache
            self.active_alerts[alert.alert_id] = alert
            
            logger.info(f"Alert stored: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error storing alert: {e}")
            session.rollback()
        finally:
            session.close()
    
    async def _distribute_alert(self, alert: Alert):
        """Distribute alert to relevant stakeholders"""
        try:
            # Find relevant stakeholders
            relevant_stakeholders = self._find_relevant_stakeholders(alert)
            
            # Send notifications
            for stakeholder in relevant_stakeholders:
                await self._send_notifications(alert, stakeholder)
            
            logger.info(f"Alert distributed to {len(relevant_stakeholders)} stakeholders")
            
        except Exception as e:
            logger.error(f"Error distributing alert: {e}")
    
    def _find_relevant_stakeholders(self, alert: Alert) -> List[Stakeholder]:
        """Find stakeholders who should receive this alert"""
        relevant = []
        
        for stakeholder in self.stakeholders:
            # Check geographic relevance
            is_in_area = False
            for area_lat, area_lon, radius in stakeholder.geographic_areas:
                distance = self._calculate_distance(alert.location, (area_lat, area_lon))
                if distance <= radius:
                    is_in_area = True
                    break
            
            if not is_in_area:
                continue
            
            # Check notification channels for alert type and severity filters
            has_relevant_channel = False
            for channel in stakeholder.notification_channels:
                if not channel.is_active:
                    continue
                
                # Check alert type filter
                if channel.alert_types and alert.alert_type not in channel.alert_types:
                    continue
                
                # Check severity filter
                severity_order = [AlertSeverity.LOW, AlertSeverity.MEDIUM, AlertSeverity.HIGH, AlertSeverity.CRITICAL]
                if severity_order.index(alert.severity) < severity_order.index(channel.min_severity):
                    continue
                
                has_relevant_channel = True
                break
            
            if has_relevant_channel:
                relevant.append(stakeholder)
        
        return relevant
    
    def _calculate_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """Calculate distance between two geographic points (simplified)"""
        from math import sqrt
        
        lat_diff = loc1[0] - loc2[0]
        lon_diff = loc1[1] - loc2[1]
        
        # Simplified distance calculation (not accounting for Earth's curvature)
        # For production, use proper geospatial libraries
        distance = sqrt(lat_diff**2 + lon_diff**2) * 111  # Rough km conversion
        
        return distance
    
    async def _send_notifications(self, alert: Alert, stakeholder: Stakeholder):
        """Send notifications to a stakeholder through their preferred channels"""
        
        for channel in stakeholder.notification_channels:
            if not channel.is_active:
                continue
            
            # Check filters
            if channel.alert_types and alert.alert_type not in channel.alert_types:
                continue
            
            severity_order = [AlertSeverity.LOW, AlertSeverity.MEDIUM, AlertSeverity.HIGH, AlertSeverity.CRITICAL]
            if severity_order.index(alert.severity) < severity_order.index(channel.min_severity):
                continue
            
            # Send notification based on channel type
            try:
                if channel.channel_type == "sms":
                    await self._send_sms(alert, channel.target, stakeholder)
                elif channel.channel_type == "email":
                    await self._send_email(alert, channel.target, stakeholder)
                elif channel.channel_type == "webhook":
                    await self._send_webhook(alert, channel.target, stakeholder)
                
            except Exception as e:
                logger.error(f"Error sending {channel.channel_type} notification: {e}")
                await self._log_notification(alert.alert_id, channel.channel_type, 
                                           channel.target, "failed", "", str(e))
    
    async def _send_sms(self, alert: Alert, phone_number: str, stakeholder: Stakeholder):
        """Send SMS notification"""
        try:
            if not self.twilio_client:
                logger.warning("Twilio client not configured, skipping SMS")
                await self._log_notification(alert.alert_id, "sms", phone_number, 
                                           "skipped", "Twilio not configured", "")
                return
            
            message = self._format_sms_message(alert, stakeholder)
            
            # Send via Twilio
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=getattr(settings, 'twilio_phone_number', '+1234567890'),
                to=phone_number
            )
            
            await self._log_notification(alert.alert_id, "sms", phone_number, 
                                       "sent", message, "")
            
            logger.info(f"SMS sent to {phone_number} for alert {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            await self._log_notification(alert.alert_id, "sms", phone_number, 
                                       "failed", "", str(e))
    
    async def _send_email(self, alert: Alert, email_address: str, stakeholder: Stakeholder):
        """Send email notification"""
        try:
            # Check if email credentials are configured
            email_user = getattr(settings, 'email_user', None)
            email_password = getattr(settings, 'email_password', None)
            
            if not email_user or not email_password:
                logger.warning("Email credentials not configured, skipping email")
                await self._log_notification(alert.alert_id, "email", email_address, 
                                           "skipped", "Email not configured", "")
                return
            
            subject, body = self._format_email_message(alert, stakeholder)
            
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = email_address
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            smtp_server = getattr(settings, 'smtp_server', 'smtp.gmail.com')
            smtp_port = getattr(settings, 'smtp_port', 587)
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            text = msg.as_string()
            server.sendmail(email_user, email_address, text)
            server.quit()
            
            await self._log_notification(alert.alert_id, "email", email_address, 
                                       "sent", body, "")
            
            logger.info(f"Email sent to {email_address} for alert {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            await self._log_notification(alert.alert_id, "email", email_address, 
                                       "failed", "", str(e))
    
    async def _send_webhook(self, alert: Alert, webhook_url: str, stakeholder: Stakeholder):
        """Send webhook notification"""
        try:
            payload = {
                'alert_id': alert.alert_id,
                'timestamp': alert.timestamp.isoformat(),
                'alert_type': alert.alert_type.value,
                'severity': alert.severity.value,
                'location': alert.location,
                'title': alert.title,
                'description': alert.description,
                'recommended_actions': alert.recommended_actions,
                'stakeholder_id': stakeholder.stakeholder_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        await self._log_notification(alert.alert_id, "webhook", webhook_url, 
                                                   "sent", json.dumps(payload), "")
                        logger.info(f"Webhook sent to {webhook_url} for alert {alert.alert_id}")
                    else:
                        error_msg = f"HTTP {response.status}: {await response.text()}"
                        await self._log_notification(alert.alert_id, "webhook", webhook_url, 
                                                   "failed", "", error_msg)
            
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
            await self._log_notification(alert.alert_id, "webhook", webhook_url, 
                                       "failed", "", str(e))
    
    def _format_sms_message(self, alert: Alert, stakeholder: Stakeholder) -> str:
        """Format SMS message for alert"""
        severity_emoji = {
            AlertSeverity.LOW: "🟡",
            AlertSeverity.MEDIUM: "🟠", 
            AlertSeverity.HIGH: "🔴",
            AlertSeverity.CRITICAL: "🚨"
        }
        
        message = f"{severity_emoji.get(alert.severity, '⚠️')} COASTAL ALERT\n"
        message += f"{alert.title}\n"
        message += f"Location: {alert.location[0]:.3f}, {alert.location[1]:.3f}\n"
        message += f"Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M')}\n"
        
        if alert.recommended_actions:
            message += f"Action: {alert.recommended_actions[0]}\n"
        
        message += f"Alert ID: {alert.alert_id}"
        
        return message[:160]  # SMS length limit
    
    def _format_email_message(self, alert: Alert, stakeholder: Stakeholder) -> Tuple[str, str]:
        """Format email message for alert"""
        
        subject = f"Coastal Alert: {alert.title} ({alert.severity.value.upper()})"
        
        html_body = f"""
        <html>
        <body>
            <h2 style="color: {'red' if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL] else 'orange'}">
                Coastal Threat Alert
            </h2>
            
            <table border="1" cellpadding="5" cellspacing="0">
                <tr><td><strong>Alert ID:</strong></td><td>{alert.alert_id}</td></tr>
                <tr><td><strong>Type:</strong></td><td>{alert.alert_type.value.replace('_', ' ').title()}</td></tr>
                <tr><td><strong>Severity:</strong></td><td>{alert.severity.value.upper()}</td></tr>
                <tr><td><strong>Time:</strong></td><td>{alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</td></tr>
                <tr><td><strong>Location:</strong></td><td>{alert.location[0]:.4f}, {alert.location[1]:.4f}</td></tr>
            </table>
            
            <h3>Description</h3>
            <p>{alert.description}</p>
            
            <h3>Recommended Actions</h3>
            <ul>
        """
        
        for action in alert.recommended_actions:
            html_body += f"<li>{action}</li>"
        
        html_body += """
            </ul>
            
            <h3>Affected Areas</h3>
            <ul>
        """
        
        for area in alert.affected_areas:
            html_body += f"<li>{area}</li>"
        
        html_body += f"""
            </ul>
            
            <p><strong>This alert expires at:</strong> {alert.expires_at.strftime('%Y-%m-%d %H:%M:%S UTC') if alert.expires_at else 'No expiration'}</p>
            
            <hr>
            <p><small>
                This alert was sent to {stakeholder.name} ({stakeholder.organization}) 
                as part of the Coastal Threat Alert System.
            </small></p>
        </body>
        </html>
        """
        
        return subject, html_body
    
    async def _log_notification(self, alert_id: str, channel_type: str, target: str, 
                              status: str, message: str, error_message: str):
        """Log notification attempt"""
        session = self.Session()
        try:
            log_entry = NotificationLogDB(
                alert_id=alert_id,
                channel_type=channel_type,
                target=target,
                timestamp=datetime.now(),
                status=status,
                message=message,
                error_message=error_message
            )
            
            session.add(log_entry)
            session.commit()
            
        except Exception as e:
            logger.error(f"Error logging notification: {e}")
            session.rollback()
        finally:
            session.close()
    
    async def get_active_alerts(self, location: Optional[Tuple[float, float]] = None, 
                              radius: float = 10.0) -> List[Alert]:
        """Get currently active alerts, optionally filtered by location"""
        session = self.Session()
        try:
            query = session.query(AlertDB).filter(AlertDB.is_active == True)
            
            if alert.expires_at:
                query = query.filter(AlertDB.expires_at > datetime.now())
            
            alerts = query.all()
            
            result = []
            for db_alert in alerts:
                alert = Alert(
                    alert_id=db_alert.alert_id,
                    timestamp=db_alert.timestamp,
                    alert_type=AlertType(db_alert.alert_type),
                    severity=AlertSeverity(db_alert.severity),
                    location=(db_alert.latitude, db_alert.longitude),
                    title=db_alert.title,
                    description=db_alert.description,
                    recommended_actions=json.loads(db_alert.recommended_actions),
                    affected_areas=json.loads(db_alert.affected_areas),
                    expires_at=db_alert.expires_at,
                    source_data=json.loads(db_alert.source_data),
                    is_active=db_alert.is_active
                )
                
                # Filter by location if specified
                if location:
                    distance = self._calculate_distance(location, alert.location)
                    if distance <= radius:
                        result.append(alert)
                else:
                    result.append(alert)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
        finally:
            session.close()
    
    async def deactivate_alert(self, alert_id: str) -> bool:
        """Deactivate an alert"""
        session = self.Session()
        try:
            alert = session.query(AlertDB).filter(AlertDB.alert_id == alert_id).first()
            if alert:
                alert.is_active = False
                session.commit()
                
                # Remove from cache
                if alert_id in self.active_alerts:
                    del self.active_alerts[alert_id]
                
                logger.info(f"Alert deactivated: {alert_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deactivating alert: {e}")
            session.rollback()
            return False
        finally:
            session.close()

if __name__ == "__main__":
    # Test the alert system
    async def main():
        alert_system = CoastalAlertSystem()
        
        # Test sensor data processing
        test_sensor_data = {
            'measurement_type': 'wave_height',
            'value': 4.5,
            'latitude': 12.5,
            'longitude': 80.5,
            'timestamp': datetime.now().isoformat()
        }
        
        alerts = await alert_system.process_sensor_data(test_sensor_data)
        print(f"Generated {len(alerts)} alerts")
    
    asyncio.run(main())

