# YC Founder Cold Email Tool

A complete Python tool to extract founder emails from Y Combinator companies and send personalized cold emails.

## 🚀 Features

- **API-Based Company Fetching**: Uses YC OSS API for fast, reliable company data
- **Smart Filtering**: Supports ALL YC filter parameters (batch, industry, team size, etc.)
- **Regex Email Extraction**: Fast and reliable email detection from YC pages
- **Gmail API Integration**: Send professional cold emails at scale
- **Resumable**: Skip already processed companies and sent emails
- **Progress Tracking**: Save progress automatically

## 📋 Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up Gmail API (for sending emails):**
```bash
python setup_gmail_api.py
```

## 🎯 Usage

### Step 1: Fetch Companies
Get YC companies using any YC companies URL with filters:

```bash
# Use default filters
python 1_fetch_companies_api.py

# Or provide custom YC URL with filters
python 1_fetch_companies_api.py 'https://www.ycombinator.com/companies?batch=Summer%202025&industry=Consumer'
```

**Supported Filters:**
- `batch` - Company batches (e.g., "Summer 2025")
- `industry` - Industries (e.g., "Consumer", "B2B")
- `region` - Geographic regions
- `team_size` - Team size ranges (e.g., ["5","1,000+"])
- `app_video_public` - Has public application video
- `demo_day_video_public` - Has public demo day video
- `isHiring` - Currently hiring
- And many more!

### Step 2: Extract Emails
Use regex to extract all emails from YC company pages:

```bash
# Extract emails for all companies
python 2_fetch_emails.py

# Test email extraction on a single company
python 2_fetch_emails.py https://www.ycombinator.com/companies/approval-ai
```

### Step 3: Send Cold Emails

First, set up Gmail API:
```bash
python setup_gmail_api.py
```

Then send cold emails:
```bash
# Send emails to all founders
python 3_send_cold_emails.py

# Test with a single email address
python 3_send_cold_emails.py your-email@example.com
```

## 📧 Gmail API Setup

To send emails, you need to set up Gmail API:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Go to 'Credentials' → 'Create Credentials' → 'OAuth 2.0 Client IDs'
5. Choose 'Desktop application'
6. Download the JSON file and save it as `credentials.json` in this folder
7. Run `python setup_gmail_api.py` to authenticate

## 📝 Email Template

The cold email includes:
- **Subject**: "this is a 30 second email"
- **Personalized greeting** (extracted from email or company name)
- **Product pitch**: Auto-handling customer requests tool
- **Value proposition**: 50% → 10% time savings on customer support
- **Call to action**: Calendly booking link
- **Professional signature**

## 📊 Output

The final `yc_companies.csv` contains:
- `name`: Company name
- `yc_url`: YC profile URL  
- `batch`: YC batch (e.g., "Summer 2025")
- `status`: Company status
- `industry`: Company industry
- `website`: Company website
- `location`: Company location
- `team_size`: Team size
- `founder_emails`: All extracted emails (semicolon separated)
- `support_emails`: Empty (not used)
- `email_fetched`: Email extraction status
- `email_sent`: Cold email sending status

## ⚡ Rate Limiting

- **Email extraction**: 1 second delay between requests
- **Cold emails**: 5 seconds delay between emails (to avoid spam limits)
- Progress is saved every 10 operations

## 💡 Example Workflow

```bash
# 1. Get Consumer companies from recent batches
python 1_fetch_companies_api.py 'https://www.ycombinator.com/companies?industry=Consumer&batch=Summer%202025'

# 2. Extract emails
python 2_fetch_emails.py

# 3. Set up Gmail API (one-time setup)
python setup_gmail_api.py

# 4. Send cold emails
python 3_send_cold_emails.py
```

## 📈 Example Results

```
Company: Approval AI
Emails Found: hello@getapproval.ai
Cold Email Sent: ✅ Sent to hello@getapproval.ai (Hi there)
```