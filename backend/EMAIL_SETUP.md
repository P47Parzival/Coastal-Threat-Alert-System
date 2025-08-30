# Email Configuration for Flood Detection System

## Overview
The flood detection system can send email alerts when high or critical flood risks are detected. Currently, it uses SendGrid as the email service provider.

## Setup Instructions

### 1. SendGrid Account Setup
1. Go to [SendGrid](https://sendgrid.com/) and create a free account
2. Verify your sender email address
3. Generate an API key

### 2. Environment Variables
Create a `.env` file in the backend directory with:

```bash
# Email Configuration
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDER_EMAIL=your_verified_sender_email@example.com

# Other configurations...
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=satellite_monitoring
```

### 3. Email Fallback
If SendGrid is not configured:
- Email alerts will be logged to the console instead
- The system will continue to work normally
- You'll see console messages like:
  ```
  📧 FLOOD ALERT (Console Log): user@example.com
     Location: Mumbai
     Risk Level: HIGH
     Time to Flood: 12-48 hours
  ```

## Current Status
- ✅ Database operations working
- ✅ Flood risk calculation improved
- ✅ Email fallback implemented
- ⚠️ SendGrid needs API key configuration

## Testing
1. Start the backend server
2. Test flood detection without email: `/flood/test-detect`
3. Test with authentication: `/flood/detect` (requires login)
4. Check console for email fallback messages

## Troubleshooting
- **HTTP 401 Unauthorized**: SendGrid API key is invalid or expired
- **Email not sending**: Check console for fallback messages
- **System not working**: Ensure MongoDB is running and backend is started
