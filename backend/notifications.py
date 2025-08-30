# backend/notifications.py
from dotenv import load_dotenv
load_dotenv()
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from routes_aoi import generate_thumbnail 

# Get your SendGrid API Key from your environment variables
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDER_EMAIL = "dhruvmali999@gmail.com" # Must be a verified sender in SendGrid

def send_change_alert_email(user_email: str, aoi_name: str, change_details: dict):
    if not SENDGRID_API_KEY:
        print("ERROR: SendGrid API Key not configured. Cannot send email.")
        return

    for key in ["before_image_params", "after_image_params"]:
        params = change_details[key]
        params["vis_params"] = {"bands": ["B4", "B3", "B2"], "min": 0.0, "max": 3000}  #since data is not divided by 10000
    
    # Generate fresh URLs using the params stored in change_details
    before_url = generate_thumbnail(change_details["before_image_params"])
    after_url = generate_thumbnail(change_details["after_image_params"])

    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=user_email,
        subject=f"Change Detected in your Area of Interest: {aoi_name}",
        html_content=f"""
        <h2>Alert: Significant Change Detected!</h2>
        <p>Our system has detected a significant change in your monitored Area of Interest (AOI): <strong>{aoi_name}</strong>.</p>
        <h3>Details:</h3>
        <ul>
            <li><strong>Type of Change Analyzed:</strong> Deforestation (NDVI Drop)</li>
            <li><strong>Area of Change:</strong> {change_details['area_of_change']:.2f} square meters.</li>
        </ul>
        <p>Please log in to the dashboard to review the changes.</p>
        <h3>Visual Comparison:</h3>
        <table style="width:100%;">
        <tr>
            <td style="text-align:center;"><strong>Before</strong></td>
            <td style="text-align:center;"><strong>After</strong></td>
        </tr>
        <tr>
            <td><img src="{before_url}" alt="Before Image" style="width:100%;"></td>
            <td><img src="{after_url}" alt="After Image" style="width:100%;"></td>
        </tr>
        </table>
        """
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Successfully sent alert email to {user_email}, Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_flood_alert_email(user_email: str, location_name: str, flood_analysis: dict):
    """
    Send flood alert email to user
    """
    if not SENDGRID_API_KEY:
        print("ERROR: SendGrid API Key not configured. Cannot send flood alert email.")
        return

    # Determine alert level and urgency
    risk_level = flood_analysis.get('floodRisk', 'UNKNOWN')
    time_to_flood = flood_analysis.get('timeToFlood', 'Unknown')
    risk_score = flood_analysis.get('riskScore', 0)
    
    # Set subject based on risk level
    if risk_level == 'CRITICAL':
        subject = f"🚨 CRITICAL FLOOD ALERT - Immediate Action Required"
        urgency_color = "#dc2626"  # Red
    elif risk_level == 'HIGH':
        subject = f"⚠️ HIGH FLOOD RISK Alert - Take Action Soon"
        urgency_color = "#ea580c"  # Orange
    else:
        subject = f"🌊 Flood Risk Alert - {location_name}"
        urgency_color = "#ca8a04"  # Yellow
    
    # Create HTML content
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: {urgency_color}; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">🌊 Flood Risk Alert</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px;">{location_name}</p>
        </div>
        
        <div style="background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0;">
            <h2 style="color: {urgency_color}; margin-top: 0;">Risk Assessment</h2>
            
            <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid {urgency_color};">
                <h3 style="margin: 0 0 10px 0; color: {urgency_color};">Risk Level: {risk_level}</h3>
                <p style="margin: 0; font-size: 18px; font-weight: bold;">Time to Potential Flood: {time_to_flood}</p>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0;">
                <div style="background: white; padding: 15px; border-radius: 8px; text-align: center;">
                    <h4 style="margin: 0 0 10px 0; color: #374151;">Risk Score</h4>
                    <p style="margin: 0; font-size: 24px; font-weight: bold; color: {urgency_color};">{risk_score:.0f}/100</p>
                </div>
                <div style="background: white; padding: 15px; border-radius: 8px; text-align: center;">
                    <h4 style="margin: 0 0 10px 0; color: #374151;">Confidence</h4>
                    <p style="margin: 0; font-size: 24px; font-weight: bold; color: #059669;">{flood_analysis.get('confidence', 0) * 100:.0f}%</p>
                </div>
            </div>
            
            <h3 style="color: #374151;">Environmental Factors</h3>
            <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div>
                        <strong>Precipitation:</strong> {flood_analysis.get('precipitation', 0):.1f} mm
                    </div>
                    <div>
                        <strong>Soil Moisture:</strong> {flood_analysis.get('soilMoisture', 0):.2f} m³/m³
                    </div>
                    <div>
                        <strong>Water Level:</strong> {flood_analysis.get('waterLevel', 0):.2f}
                    </div>
                    <div>
                        <strong>Drainage Capacity:</strong> {flood_analysis.get('drainageCapacity', 0):.2f}
                    </div>
                </div>
            </div>
            
            <h3 style="color: #374151;">Immediate Actions Required</h3>
            <div style="background: #fef3c7; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Monitor local weather updates and flood warnings</li>
                    <li>Prepare emergency supplies and evacuation plan</li>
                    <li>Move to higher ground if necessary</li>
                    <li>Stay informed through official channels</li>
                    <li>Follow local emergency management instructions</li>
                </ul>
            </div>
            
            <div style="background: #dbeafe; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #3b82f6;">
                <p style="margin: 0; font-size: 14px; color: #1e40af;">
                    <strong>Analysis Date:</strong> {flood_analysis.get('analysisDate', 'Unknown')}<br>
                    <strong>Detection Method:</strong> {flood_analysis.get('detectionMethod', 'Unknown')}
                </p>
            </div>
        </div>
        
        <div style="background: #f1f5f9; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; border: 1px solid #e2e8f0;">
            <p style="margin: 0; color: #64748b; font-size: 14px;">
                This alert was generated automatically by our flood monitoring system.<br>
                Please take appropriate action based on your local conditions.
            </p>
        </div>
    </div>
    """
    
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=user_email,
        subject=subject,
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✅ Successfully sent flood alert email to {user_email}, Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error sending flood alert email: {e}")