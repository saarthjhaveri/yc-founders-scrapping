# YC Ultimate Outreach Tool 🚀

The complete all-in-one solution for YC founder outreach. Fetch companies, extract emails, and send personalized cold emails - all in one powerful script with Google Sheets integration.

## ✨ Features

- **🎯 All-in-One Solution**: One script does everything - no more juggling multiple files
- **📊 Google Sheets Integration**: Centralized master database with zero duplicate work
- **🔄 Smart Mode Selection**: Choose to just collect data OR collect + send emails
- **📧 Custom Email Templates**: Personalize subject lines and email bodies
- **🧠 Intelligent Greeting**: Smart founder name extraction from emails
- **⚡ Incremental Processing**: Only process new companies, skip existing ones
- **🎯 Advanced Filtering**: Support ALL YC filter parameters
- **📈 Progress Tracking**: Automatic saving and resumption
- **🛡️ Rate Limiting**: Respectful to servers with built-in delays

## 🚀 Quick Start

### 1. Setup (One Time)
```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup Google Sheets (master database)
python setup_sheets_api.py

# Setup Gmail (for sending emails)
python setup_gmail_api.py
```

### 2. Run the Ultimate Tool
```bash
# Interactive mode with options
python yc_outreach_tool.py

# Or provide URL directly
python yc_outreach_tool.py "https://www.ycombinator.com/companies?batch=Winter%202025&industry=B2B"
```

## 🎯 How It Works

### Interactive Mode Selection
When you run the tool, you'll be asked:

```
🚀 YC Ultimate Outreach Tool
==================================================

📋 What would you like to do?
1. Fetch companies and emails only (no sending)
2. Fetch companies, emails, AND send cold emails

Enter your choice (1 or 2): 
```

### Option 1: Data Collection Only
- ✅ Fetches companies from YC API
- ✅ Checks master database for duplicates
- ✅ Extracts emails from new companies
- ✅ Updates Google Sheets database
- ✅ Shows summary and statistics

### Option 2: Full Outreach Campaign
Everything from Option 1, PLUS:
- ✅ Custom email subject and body
- ✅ Email preview before sending
- ✅ Personalized greetings (Hi John, Hi Waffle team, etc.)
- ✅ Rate-limited sending (5 seconds between emails)
- ✅ Real-time progress tracking
- ✅ Complete campaign statistics

## 📧 Email Customization

### Subject Line
```
Email Subject (default: 'this is a 30 second email'): Your Custom Subject
```

### Email Body Options
```
Email Body Options:
1. Use default template
2. Enter custom email body

Choose (1 or 2): 2

Enter your email body (use {founder_name} for personalization):
Hi {founder_name},

Your custom message here...

Type 'END' on a new line when finished:
END
```

### Smart Personalization
The tool automatically personalizes greetings:
- `john.smith@company.com` → "Hi John Smith"
- `founders@waffle.ai` → "Hi Waffle team"
- `hello@company.com` → "Hi Company team"
- Generic fallback → "Hi there"

## 🏗️ Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│   YC OSS API        │───▶│  Google Sheets       │───▶│  Gmail API      │
│  (All Companies)    │    │  Master Database     │    │  (Cold Emails)  │
└─────────────────────┘    └──────────────────────┘    └─────────────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │  Smart Duplicate     │
                           │  Prevention          │
                           └──────────────────────┘
```

## 📊 Example Workflow

### First Run (Winter 2025 B2B Companies)
```bash
python yc_outreach_tool.py

# Choose option 1 (data collection only)
# Enter URL: https://www.ycombinator.com/companies?batch=Winter%202025&industry=B2B

Result:
✅ 45 companies processed
✅ 28 emails found
✅ Master database updated
```

### Second Run (Add Summer 2025 B2B Companies)
```bash
python yc_outreach_tool.py

# Choose option 2 (collect + send emails)
# Enter URL: https://www.ycombinator.com/companies?batch=Winter%202025&batch=Summer%202025&industry=B2B

Result:
✅ Only 23 NEW Summer 2025 companies processed (Winter 2025 skipped!)
✅ 15 new emails found
✅ 43 total companies with emails
✅ Sent 87 personalized cold emails
✅ 94% success rate
```

## 🎯 Supported YC Filters

The tool supports **ALL** YC company filters:

| Filter | Description | Example |
|--------|-------------|---------|
| `batch` | Company batches | Summer 2025, Winter 2024 |
| `industry` | Industries | Consumer, B2B, Healthcare |
| `region` | Geographic regions | San Francisco, New York |
| `team_size` | Team size ranges | ["5","1,000+"] |
| `status` | Company status | Active, Inactive |
| `stage` | Company stage | Early, Growth |
| `top_company` | Top company flag | true/false |
| `nonprofit` | Nonprofit flag | true/false |
| `isHiring` | Currently hiring | true/false |
| `app_video_public` | Has public application video | true/false |
| `demo_day_video_public` | Has public demo day video | true/false |
| `app_answers` | Has application answers | true/false |
| `question_answers` | Has bonus question answers | true/false |
| `tags` | Company tags | Various tags |

## 📁 File Structure

```
ycFounderScraping/
├── yc_outreach_tool.py           # 🌟 MAIN SCRIPT - Does everything!
├── setup_sheets_api.py           # Google Sheets setup
├── setup_gmail_api.py            # Gmail API setup
├── requirements.txt              # Dependencies
├── credentials.json              # Google OAuth credentials (you create)
├── sheets_token.json             # Sheets API token (auto-generated)
├── token.json                    # Gmail API token (auto-generated)
├── sheets_config.json            # Sheets configuration (auto-generated)
└── README.md                     # This file
```

## 🎉 Benefits Over Traditional Approaches

### Before (Multiple Scripts)
```
Step 1: python fetch_companies.py
Step 2: python extract_emails.py  
Step 3: python send_emails.py
❌ Manual coordination
❌ Risk of data loss
❌ Duplicate work
❌ Complex workflow
```

### After (Ultimate Tool)
```
Step 1: python yc_outreach_tool.py
✅ Everything automated
✅ Zero duplicate work
✅ Bulletproof data storage
✅ One simple command
```

### Key Advantages
- ⚡ **10x faster** after first run (smart duplicate prevention)
- 🎯 **Zero configuration** needed between runs
- 📊 **Centralized database** accessible anywhere
- 🔄 **Incremental growth** of your prospect database
- 🛡️ **Bulletproof** with automatic backups
- 🚀 **Production ready** for serious outreach campaigns

## 📈 Example Results

```
🎉 ULTIMATE OUTREACH CAMPAIGN COMPLETED!
   Companies processed: 34
   Emails found: 22
   Emails sent: 45
   Emails failed: 2
   Success rate: 95.7%
   Master database: https://docs.google.com/spreadsheets/d/your-sheet-id
```

## 🔧 Setup Details

### Google Cloud Console Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google Sheets API** and **Google Drive API**
4. Enable **Gmail API**
5. Create OAuth 2.0 credentials (Desktop application)
6. Download `credentials.json`
7. Add your email as test user in OAuth consent screen

### API Endpoints
- **Google Sheets API**: https://console.developers.google.com/apis/api/sheets.googleapis.com
- **Google Drive API**: https://console.developers.google.com/apis/api/drive.googleapis.com
- **Gmail API**: https://console.developers.google.com/apis/api/gmail.googleapis.com

## 🚨 Rate Limits & Best Practices

- **YC API**: 1 second delay between company page requests
- **Gmail API**: 5 seconds delay between email sends
- **Google Sheets**: Batch updates every 10 operations
- **Respectful scraping**: User-Agent headers and reasonable timeouts

## 🎯 Pro Tips

### Maximize Email Discovery
```bash
# Target recent batches for higher email availability
python yc_outreach_tool.py "https://www.ycombinator.com/companies?batch=Summer%202025&batch=Spring%202025"
```

### Industry-Specific Campaigns
```bash
# Focus on specific industries for targeted outreach
python yc_outreach_tool.py "https://www.ycombinator.com/companies?industry=B2B&industry=Enterprise"
```

### Geographic Targeting
```bash
# Target specific regions
python yc_outreach_tool.py "https://www.ycombinator.com/companies?region=San%20Francisco&region=New%20York"
```

## 🎉 Ready to Scale Your Outreach!

Your YC founder outreach is now **enterprise-grade** with:

- ✅ **One-command operation** - no more complex workflows
- ✅ **Smart duplicate prevention** - never waste time on the same company twice
- ✅ **Centralized database** - access your data from anywhere
- ✅ **Custom email campaigns** - personalized outreach at scale
- ✅ **Professional rate limiting** - respectful and sustainable
- ✅ **Complete automation** - from discovery to delivery

**Happy networking!** 🚀📧

---

*Built with ❤️ for efficient YC founder outreach*