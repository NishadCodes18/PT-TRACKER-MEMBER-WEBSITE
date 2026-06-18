# Member Portal

A separate web portal for gym members to view their membership details and expiry dates.

## Features

- **Email + OTP Authentication**: Members login using their registered email and trainer name
- **Membership Dashboard**: View personal details, training info, and membership expiry date
- **Secure Access**: OTP-based login with no password required
- **Shared Database**: Syncs with the main trainer website database

## Setup

### Prerequisites

The member portal shares the same database as the trainer website. Make sure the main PT Tracker application is set up first.

### Installation

1. Navigate to the member-website directory:
```bash
cd member-website
```

2. The member portal uses the same dependencies as the main application. Ensure you have installed:
```bash
pip install flask flask-sqlalchemy flask-login flask-wtf werkzeug email-validator pyotp python-dotenv
```

3. The member portal uses the same `.env` file as the main application (located in the parent directory). Make sure it contains:
```
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
# Or use Brevo/Mailgun API for emails
BREVO_API_KEY=your_brevo_key
BREVO_SENDER_EMAIL=your_email
```

### Running the Member Portal

Run the member portal on a different port than the trainer website:

```bash
python app.py
```

By default, it runs on port 5001. You can change this by setting the PORT environment variable:

```bash
PORT=5002 python app.py
```

## Usage

### For Members

1. Go to the member portal URL (e.g., http://localhost:5001)
2. Enter your registered email address
3. Enter your trainer's name
4. You'll receive a 6-digit OTP code via email
5. Enter the code to access your membership dashboard
6. View your membership expiry date and training details

### For Trainers

- Trainers manage member data through the main PT Tracker website
- Members must have an email address registered in the system to use the portal
- The trainer's username is case-insensitive when members enter it

## Database

The member portal creates one additional table:
- `member_otps`: Stores OTP codes for member authentication

This table is automatically created when the app starts.

## Deployment

The member portal can be deployed separately from the main trainer website:

### Option 1: Same Server, Different Ports
- Deploy both apps on the same server using different ports
- Use a reverse proxy (nginx) to route traffic:
  - `/` → Trainer website
  - `/members` → Member portal

### Option 2: Separate Deployments
- Deploy to separate hosting services (e.g., two Vercel projects)
- Both should use the same DATABASE_URL to share data
- Update the trainer website URL in `member_login.html` if needed

### Vercel Deployment

Create a `vercel.json` in the member-website folder:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

## Linking Between Portals

- The member login page includes a link to the trainer portal
- Update the trainer login page to add a link to the member portal if desired
- Both portals share the same styling and branding

## Security Notes

- OTP codes expire after 10 minutes
- Failed OTP attempts are limited (5 attempts max)
- Members can only access their own data
- No password storage for members - OTP authentication only
- All sessions are secured with Flask-Login

## Support

For issues or questions, contact: nishadpatil2008@gmail.com
