# Environment Setup Guide for Member Portal

## Quick Start

1. Copy `.env.example` to `.env` in the **parent directory** (PT-TRACKER-WEBSITE-main folder):
```bash
cd ..
cp member-website/.env.example .env
```

**Important:** The member portal uses the same `.env` file as the trainer website, located in the parent directory.

2. Edit `.env` and configure the required settings below.

## Required Configuration

### 1. Database Connection

The member portal **must** connect to the same database as the trainer website.

**For Local Development (SQLite):**
```env
DATABASE_URL=sqlite:///gym_tracker.db
```

**For Production (PostgreSQL):**
```env
DATABASE_URL=postgresql://username:password@host:port/database_name
```

**Render PostgreSQL Example:**
```env
DATABASE_URL=postgresql://user:pass@dpg-abc123.oregon-postgres.render.com/mydb
```

**Aiven PostgreSQL Example:**
```env
DATABASE_URL=postgresql://user:pass@db-name.aivencloud.com:12345/defaultdb?sslmode=require
```

### 2. Secret Key

Generate a secure random string for session encryption:

```bash
# Generate random secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

Then set it in `.env`:
```env
SECRET_KEY=your-generated-secret-key-here
```

### 3. Email Configuration

Choose **ONE** email provider for sending OTP codes to members.

#### Option A: Gmail SMTP (Easiest for testing)

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Configure in `.env`:

```env
EMAIL_PROVIDER=smtp
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
```

#### Option B: Brevo API (Recommended for production)

1. Sign up at https://www.brevo.com (free tier: 300 emails/day)
2. Create an API key in Settings > SMTP & API
3. Verify your sender email
4. Configure in `.env`:

```env
EMAIL_PROVIDER=brevo_api
BREVO_API_KEY=xkeysib-xxx
BREVO_SENDER_EMAIL=noreply@yourdomain.com
BREVO_SENDER_NAME=Your Gym Name
```

#### Option C: Mailgun API

1. Sign up at https://www.mailgun.com
2. Add and verify your domain
3. Get your API key from Settings
4. Configure in `.env`:

```env
EMAIL_PROVIDER=mailgun_api
MAILGUN_API_KEY=xxx
MAILGUN_DOMAIN=mg.yourdomain.com
MAILGUN_FROM_EMAIL=noreply@yourdomain.com
```

## Optional Configuration

### Branding

```env
GYM_NAME=Your Gym Name
APP_DEVELOPER=Your Name
```

### Security Settings

```env
# How many failed login attempts before lockout
LOGIN_MAX_ATTEMPTS=5

# How long to lock account after failed attempts (minutes)
LOGIN_LOCKOUT_MINUTES=15

# How long OTP codes are valid (minutes)
PASSWORD_RESET_OTP_MINUTES=10

# Maximum OTP verification attempts
PASSWORD_RESET_MAX_ATTEMPTS=5
```

### Deployment

```env
# Application environment
FLASK_ENV=production

# Port number (5001 for member portal, 5000 for trainer)
PORT=5001

# Enable HTTPS-only cookies in production
SESSION_COOKIE_SECURE=true
REMEMBER_COOKIE_SECURE=true

# Logging level
LOG_LEVEL=WARNING
```

## Verifying Configuration

After setting up `.env`, test the member portal:

```bash
cd member-website
python app.py
```

Visit `http://localhost:5001` and you should see the login portal.

## Troubleshooting

### "Cannot connect to database"
- Verify `DATABASE_URL` is correct
- For PostgreSQL, ensure `?sslmode=require` is in the URL
- Check database is accessible from your network

### "OTP email not received"
- Check spam/junk folder
- Verify email credentials in `.env`
- Check email provider logs (Gmail: https://myaccount.google.com/security)
- For Brevo/Mailgun: check dashboard for email logs

### "Import errors"
- Ensure you're running from the `member-website` directory
- Make sure `.env` is in the **parent directory**, not inside member-website

### "Secret key error in production"
- Never use the default secret key in production
- Generate a new random secret key as shown above

## Production Deployment

When deploying to Vercel, Render, or similar:

1. Set environment variables in the hosting platform's dashboard
2. Use the PostgreSQL `DATABASE_URL` (both trainer and member sites must use the same database)
3. Ensure `EMAIL_PROVIDER` and corresponding email credentials are set
4. Set `FLASK_ENV=production`
5. Set `SESSION_COOKIE_SECURE=true` and `REMEMBER_COOKIE_SECURE=true`

## Security Checklist

- [ ] Changed `SECRET_KEY` from default
- [ ] Using strong database password
- [ ] Email credentials are not hardcoded in files
- [ ] `.env` file is in `.gitignore` (never commit it)
- [ ] `SESSION_COOKIE_SECURE=true` in production
- [ ] Using HTTPS in production
- [ ] Database uses SSL connection in production
