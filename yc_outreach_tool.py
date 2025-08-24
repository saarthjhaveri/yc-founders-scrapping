#!/usr/bin/env python3
"""
Ultimate YC Outreach Tool - All-in-One Solution
Fetches companies, extracts emails, and sends personalized cold emails
"""

import requests
import pandas as pd
from urllib.parse import urlparse, parse_qs, unquote
import re
import json
import time
import sys
import os
import base64
from datetime import datetime
from bs4 import BeautifulSoup
import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText

# Default email template
DEFAULT_EMAIL_TEMPLATE = """Subject: this is a 30 second email

Hi {founder_name},

I'm Saarth, we're building a tool that auto-handles customer requests(refund, queries) from all channels(intercom, email, discord) so your team doesn't have to.

Here's how we do it: 
→ reads refund requests from all of your channels (email, intercom, discord, custom)
→ checks them against your policy & their payment history to find anything shady, 
→ if valid → auto-refunds via Stripe/Shopify or ask for an approval
→ sends the customer a reply instantly + tracks it for you

refunds and customer queries(known bugs, latest updates) go from taking days → minutes. You go from spending 50% of your time dealing with customers to ~10%.

Will you be up for a quick 10 min chat to see if this is helpful for you? Please book a slot here: https://calendly.com/saarth62/30min 

Cheers,
Saarth"""

def get_user_options():
    """Get user preferences for the outreach campaign"""
    print("🚀 YC Ultimate Outreach Tool")
    print("=" * 50)
    
    # Mode selection
    print("\n📋 What would you like to do?")
    print("1. Fetch companies and emails only (no sending)")
    print("2. Fetch companies, emails, AND send cold emails")
    
    while True:
        mode = input("\nEnter your choice (1 or 2): ").strip()
        if mode in ['1', '2']:
            break
        print("❌ Please enter 1 or 2")
    
    send_emails = (mode == '2')
    
    # Email customization if sending emails
    email_subject = None
    email_body = None
    
    if send_emails:
        print(f"\n📧 Email Customization:")
        print("Press Enter to use default template, or customize:")
        
        # Subject
        custom_subject = input(f"\nEmail Subject (default: 'this is a 30 second email'): ").strip()
        if custom_subject:
            email_subject = custom_subject
        else:
            email_subject = "this is a 30 second email"
        
        # Body
        print(f"\nEmail Body Options:")
        print("1. Use default template")
        print("2. Enter custom email body")
        
        while True:
            body_choice = input("Choose (1 or 2): ").strip()
            if body_choice in ['1', '2']:
                break
            print("❌ Please enter 1 or 2")
        
        if body_choice == '2':
            print(f"\nEnter your email body (use {{founder_name}} for personalization):")
            print("Type 'END' on a new line when finished:")
            
            lines = []
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            
            email_body = '\n'.join(lines)
        else:
            # Extract body from default template
            email_body = DEFAULT_EMAIL_TEMPLATE.split('\n\n', 1)[1]  # Remove subject line
    
    return send_emails, email_subject, email_body

def load_sheets_config():
    """Load Google Sheets configuration"""
    if not os.path.exists('sheets_config.json'):
        print("❌ Google Sheets not configured. Please run setup_sheets_api.py first!")
        return None
    
    with open('sheets_config.json', 'r') as f:
        return json.load(f)

def connect_to_sheets():
    """Connect to Google Sheets"""
    if not os.path.exists('sheets_token.json'):
        print("❌ Google Sheets not authenticated. Please run setup_sheets_api.py first!")
        return None, None
    
    try:
        creds = Credentials.from_authorized_user_file('sheets_token.json')
        gc = gspread.authorize(creds)
        
        config = load_sheets_config()
        if not config:
            return None, None
        
        spreadsheet = gc.open_by_key(config['spreadsheet_id'])
        worksheet = spreadsheet.worksheet(config['worksheet_name'])
        
        print(f"✅ Connected to Google Sheets: {config['spreadsheet_url']}")
        return worksheet, config
    except Exception as e:
        print(f"❌ Error connecting to Google Sheets: {e}")
        return None, None

def setup_gmail_service():
    """Set up Gmail API service"""
    if not os.path.exists('token.json'):
        print("❌ Gmail API not set up. Please run setup_gmail_api.py first!")
        return None
    
    try:
        creds = Credentials.from_authorized_user_file('token.json')
        
        # Refresh credentials if needed
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        service = build('gmail', 'v1', credentials=creds)
        print(f"✅ Gmail API connected and ready to send emails")
        return service
    except Exception as e:
        print(f"❌ Error setting up Gmail service: {e}")
        return None

def extract_founder_name(company_name, email):
    """Extract founder name from email or use company name/generic greeting"""
    email_prefix = email.split('@')[0].lower()
    
    # Common generic email prefixes
    generic_prefixes = [
        'founders', 'founder', 'team', 'hello', 'hi', 'contact', 'info', 
        'support', 'admin', 'sales', 'business', 'general', 'mail',
        'office', 'help', 'service', 'inquiries', 'partnerships'
    ]
    
    # Check if email prefix is generic
    is_generic = any(generic in email_prefix for generic in generic_prefixes)
    
    if not is_generic:
        # Clean up the email prefix for potential name
        clean_prefix = re.sub(r'[._-]', ' ', email_prefix)
        clean_prefix = re.sub(r'\d+', '', clean_prefix)  # Remove numbers
        clean_prefix = clean_prefix.strip()
        
        # If it looks like a real name (has letters and reasonable length)
        if len(clean_prefix) >= 2 and clean_prefix.replace(' ', '').isalpha():
            return clean_prefix.title()
    
    # For generic emails, try to use company name if it's short and clean
    if company_name:
        # Clean company name
        clean_company = re.sub(r'[^a-zA-Z\s]', '', company_name).strip()
        
        # If company name is short (1-2 words), use it with "team"
        company_words = clean_company.split()
        if len(company_words) <= 2 and len(clean_company) <= 20:
            return f"{clean_company} team"
    
    # Default to generic greeting
    return "there"

def create_email_message(to_email, founder_name, company_name, subject, body):
    """Create the cold email message"""
    # Personalize the body
    personalized_body = body.format(founder_name=founder_name)
    
    # Create message
    message = MIMEText(personalized_body)
    message['to'] = to_email
    message['subject'] = subject
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_email(service, email_message):
    """Send email using Gmail API"""
    try:
        message = service.users().messages().send(userId='me', body=email_message).execute()
        return True, message['id']
    except Exception as e:
        return False, str(e)

def load_master_database(worksheet):
    """Load existing companies from Google Sheets master database"""
    try:
        records = worksheet.get_all_records()
        
        if not records:
            print("📊 Master database is empty - starting fresh")
            return pd.DataFrame()
        
        df = pd.DataFrame(records)
        print(f"📊 Loaded {len(df)} companies from master database")
        
        # Show some stats
        companies_with_emails = df[df['founder_emails'] != '']
        print(f"   Companies with emails: {len(companies_with_emails)}")
        print(f"   Companies needing emails: {len(df) - len(companies_with_emails)}")
        
        return df
    except Exception as e:
        print(f"❌ Error loading master database: {e}")
        return pd.DataFrame()

def parse_yc_url_filters(url):
    """Parse YC companies URL to extract filters"""
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    
    def get_param(key, as_list=True):
        values = params.get(key, [])
        if not values:
            return [] if as_list else None
        decoded_values = [unquote(v) for v in values]
        return decoded_values if as_list else decoded_values[0]
    
    def get_bool_param(key):
        value = get_param(key, as_list=False)
        if value is None:
            return None
        return value.lower() in ['true', '1', 'yes']
    
    filters = {
        'batches': get_param('batch'),
        'industries': get_param('industry'),
        'regions': get_param('region'),
        'statuses': get_param('status'),
        'tags': get_param('tags'),
        'stages': get_param('stage'),
        'team_sizes': [],
        'top_company': get_bool_param('top_company'),
        'nonprofit': get_bool_param('nonprofit'),
        'is_hiring': get_bool_param('isHiring'),
        'app_video_public': get_bool_param('app_video_public'),
        'demo_day_video_public': get_bool_param('demo_day_video_public'),
        'app_answers': get_bool_param('app_answers'),
        'question_answers': get_bool_param('question_answers'),
    }
    
    # Handle team_size filter
    if 'team_size' in params:
        team_size_raw = params['team_size'][0]
        try:
            if team_size_raw.startswith('[') and team_size_raw.endswith(']'):
                filters['team_sizes'] = json.loads(unquote(team_size_raw))
            else:
                filters['team_sizes'] = [unquote(team_size_raw)]
        except:
            filters['team_sizes'] = []
    
    # Clean up empty filters
    cleaned_filters = {k: v for k, v in filters.items() if v is not None and v != []}
    
    print(f"Parsed filters from URL:")
    for key, value in cleaned_filters.items():
        print(f"  {key}: {value}")
    
    return cleaned_filters

def fetch_yc_companies(filters):
    """Fetch companies from YC API and filter them"""
    api_url = "https://yc-oss.github.io/api/companies/all.json"
    
    print(f"Fetching companies from YC API...")
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        all_companies = response.json()
        print(f"✅ Fetched {len(all_companies)} total companies from YC API")
        
        # Apply filters
        filtered_companies = []
        for company in all_companies:
            # Check batch filter
            if 'batches' in filters:
                company_batch = company.get('batch', '')
                if not any(batch.lower() in company_batch.lower() for batch in filters['batches']):
                    continue
            
            # Check industry filter
            if 'industries' in filters:
                company_industry = company.get('industry', '')
                if not any(industry.lower() in company_industry.lower() for industry in filters['industries']):
                    continue
            
            # Add other filter checks as needed...
            filtered_companies.append(company)
        
        print(f"✅ Filtered to {len(filtered_companies)} companies matching criteria")
        return filtered_companies
        
    except Exception as e:
        print(f"❌ Error fetching companies: {e}")
        return []

def extract_emails_from_page(company_url, company_name):
    """Extract emails from YC company page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print(f"  🌐 Fetching emails for: {company_name}")
        response = requests.get(company_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        text = soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Extract emails using regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        found_emails = list(set(re.findall(email_pattern, text)))
        
        if found_emails:
            print(f"  ✅ Found emails: {found_emails}")
        else:
            print(f"  ❌ No emails found")
        
        return found_emails
        
    except Exception as e:
        print(f"  ❌ Error fetching emails for {company_name}: {e}")
        return []

def merge_companies_with_master(new_companies, master_df):
    """Merge new companies with existing master database"""
    print(f"\n🔄 Merging {len(new_companies)} new companies with master database...")
    
    # Convert new companies to DataFrame
    new_data = []
    current_time = datetime.now().isoformat()
    
    for company in new_companies:
        new_data.append({
            'name': company.get('name', ''),
            'yc_url': company.get('url', ''),
            'batch': company.get('batch', ''),
            'status': company.get('status', ''),
            'industry': company.get('industry', ''),
            'website': company.get('website', ''),
            'location': company.get('all_locations', ''),
            'description': company.get('one_liner', ''),
            'team_size': company.get('team_size', ''),
            'slug': company.get('slug', ''),
            'first_seen': current_time,
            'last_updated': current_time,
            'email_fetched': False,
            'founder_emails': ''
        })
    
    new_df = pd.DataFrame(new_data)
    
    if master_df.empty:
        print("  📊 Master database is empty - adding all companies")
        return new_df
    
    # Merge based on slug (unique identifier)
    existing_slugs = set(master_df['slug'].tolist())
    truly_new_companies = new_df[~new_df['slug'].isin(existing_slugs)]
    
    print(f"  📊 Found {len(truly_new_companies)} truly new companies")
    print(f"  📊 Skipping {len(new_df) - len(truly_new_companies)} existing companies")
    
    # Combine master + new companies
    if not truly_new_companies.empty:
        merged_df = pd.concat([master_df, truly_new_companies], ignore_index=True)
    else:
        merged_df = master_df.copy()
    
    return merged_df

def update_master_database(worksheet, df):
    """Update Google Sheets with the merged data"""
    print(f"\n💾 Updating master database with {len(df)} companies...")
    
    try:
        # Clear existing data and update with new data
        worksheet.clear()
        
        # Prepare data for upload (headers + data)
        headers = ['name', 'yc_url', 'batch', 'status', 'industry', 'website', 
                  'location', 'description', 'team_size', 'slug',
                  'first_seen', 'last_updated', 'email_fetched', 'founder_emails']
        
        # Convert DataFrame to list of lists
        data_to_upload = [headers]
        for _, row in df.iterrows():
            data_to_upload.append([str(row[col]) for col in headers])
        
        # Upload all data at once
        worksheet.update(range_name='A1', values=data_to_upload)
        
        # Format headers
        worksheet.format('A1:N1', {'textFormat': {'bold': True}})
        
        print(f"✅ Master database updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating master database: {e}")

def send_cold_emails_to_companies(companies_df, email_subject, email_body):
    """Send cold emails to companies with emails"""
    # Setup Gmail service
    service = setup_gmail_service()
    if not service:
        return 0, 0
    
    # Filter companies that have emails
    companies_with_emails = companies_df[
        (companies_df['founder_emails'] != '') & 
        (companies_df['founder_emails'].notna())
    ].copy()
    
    if len(companies_with_emails) == 0:
        print("❌ No companies with emails found for sending!")
        return 0, 0
    
    print(f"\n📧 Found {len(companies_with_emails)} companies with emails")
    
    # Show preview
    print(f"\n📧 EMAIL PREVIEW:")
    print("=" * 60)
    sample_company = companies_with_emails.iloc[0]
    sample_emails = sample_company['founder_emails'].split(';')
    sample_email = sample_emails[0].strip()
    sample_founder = extract_founder_name(sample_company['name'], sample_email)
    
    preview_message = create_email_message(sample_email, sample_founder, sample_company['name'], email_subject, email_body)
    preview_body = base64.urlsafe_b64decode(preview_message['raw']).decode()
    print(preview_body)
    print("=" * 60)
    
    # Calculate total emails
    total_emails = sum(len(row['founder_emails'].split(';')) for _, row in companies_with_emails.iterrows())
    
    print(f"\n📊 CAMPAIGN SUMMARY:")
    print(f"   Companies to email: {len(companies_with_emails)}")
    print(f"   Total emails to send: {total_emails}")
    print(f"   Rate: 1 email every 5 seconds (to avoid spam limits)")
    print(f"   Estimated time: {total_emails * 5 / 60:.1f} minutes")
    
    confirm = input(f"\nSend {total_emails} cold emails? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Email sending cancelled.")
        return 0, 0
    
    # Send emails
    sent_count = 0
    failed_count = 0
    
    print(f"\n🚀 Starting email campaign...")
    
    for index, row in companies_with_emails.iterrows():
        company_name = row['name']
        emails_str = row['founder_emails']
        
        # Split multiple emails
        emails = [email.strip() for email in emails_str.split(';') if email.strip()]
        
        print(f"\n[{sent_count + failed_count + 1}] {company_name}")
        
        for email in emails:
            if not email or '@' not in email:
                continue
            
            founder_name = extract_founder_name(company_name, email)
            
            print(f"  📧 Sending to {email} (Hi {founder_name})")
            
            # Create and send email
            email_message = create_email_message(email, founder_name, company_name, email_subject, email_body)
            success, result = send_email(service, email_message)
            
            if success:
                print(f"     ✅ Sent successfully (ID: {result})")
                sent_count += 1
            else:
                print(f"     ❌ Failed: {result}")
                failed_count += 1
            
            # Rate limiting - 5 seconds between emails
            time.sleep(5)
        
        # Progress tracking
        if (sent_count + failed_count) % 10 == 0:
            print(f"  📊 Progress: {sent_count + failed_count}/{total_emails} emails processed")
    
    return sent_count, failed_count

def main():
    """Main function - Ultimate YC Outreach Tool"""
    
    # Get user options
    send_emails, email_subject, email_body = get_user_options()
    
    # Get YC URL
    if len(sys.argv) > 1:
        yc_url = sys.argv[1]
    else:
        yc_url = input(f"\nEnter YC companies URL (or press Enter for default): ").strip()
        if not yc_url:
            yc_url = "https://www.ycombinator.com/companies?batch=Summer%202025&batch=Spring%202025&industry=Consumer"
    
    print(f"\n🎯 Target URL: {yc_url}")
    
    # Connect to Google Sheets
    worksheet, config = connect_to_sheets()
    if not worksheet:
        return
    
    # Load existing master database
    master_df = load_master_database(worksheet)
    
    # Parse URL filters and fetch new companies
    filters = parse_yc_url_filters(yc_url)
    new_companies = fetch_yc_companies(filters)
    
    if not new_companies:
        print("❌ No companies found matching filters")
        return
    
    # Merge with master database
    merged_df = merge_companies_with_master(new_companies, master_df)
    
    # Find companies that need email extraction
    companies_needing_emails = merged_df[
        (merged_df['email_fetched'] == False) | 
        (merged_df['founder_emails'] == '')
    ].copy()
    
    print(f"\n📧 Found {len(companies_needing_emails)} companies needing email extraction")
    
    if len(companies_needing_emails) > 0:
        # Process emails for companies that need them
        print(f"\n🔍 Starting email extraction...")
        
        processed_count = 0
        for index, row in companies_needing_emails.iterrows():
            company_name = row['name']
            company_url = row['yc_url']
            
            print(f"\n[{processed_count + 1}/{len(companies_needing_emails)}] {company_name}")
            
            # Extract emails
            emails = extract_emails_from_page(company_url, company_name)
            
            # Update the merged DataFrame
            merged_df.loc[merged_df['slug'] == row['slug'], 'founder_emails'] = '; '.join(emails)
            merged_df.loc[merged_df['slug'] == row['slug'], 'email_fetched'] = True
            merged_df.loc[merged_df['slug'] == row['slug'], 'last_updated'] = datetime.now().isoformat()
            
            processed_count += 1
            
            # Save progress every 10 companies
            if processed_count % 10 == 0:
                print(f"  💾 Saving progress... ({processed_count}/{len(companies_needing_emails)})")
                update_master_database(worksheet, merged_df)
            
            # Rate limiting
            time.sleep(1)
    
    # Final save
    update_master_database(worksheet, merged_df)
    
    # Get companies from current session for emailing
    session_companies = merged_df[merged_df['slug'].isin([c.get('slug') for c in new_companies])].copy()
    
    # Summary of data collection
    companies_with_emails = session_companies[session_companies['founder_emails'] != '']
    print(f"\n🎉 DATA COLLECTION COMPLETED!")
    print(f"   Total companies in master database: {len(merged_df)}")
    print(f"   Companies processed this session: {len(session_companies)}")
    print(f"   Companies with emails (this session): {len(companies_with_emails)}")
    print(f"   Master database: {config['spreadsheet_url']}")
    
    # Show sample results
    if len(companies_with_emails) > 0:
        print(f"\n📧 Sample companies with emails:")
        sample_with_emails = companies_with_emails.head(5)
        for _, row in sample_with_emails.iterrows():
            if row['founder_emails']:
                print(f"   • {row['name']}: {row['founder_emails']}")
    
    # Send emails if requested
    if send_emails and len(companies_with_emails) > 0:
        print(f"\n" + "="*70)
        print(f"📨 STARTING COLD EMAIL CAMPAIGN")
        print(f"="*70)
        
        sent_count, failed_count = send_cold_emails_to_companies(companies_with_emails, email_subject, email_body)
        
        # Final summary
        print(f"\n🎉 ULTIMATE OUTREACH CAMPAIGN COMPLETED!")
        print(f"   Companies processed: {len(session_companies)}")
        print(f"   Emails found: {len(companies_with_emails)}")
        print(f"   Emails sent: {sent_count}")
        print(f"   Emails failed: {failed_count}")
        if sent_count + failed_count > 0:
            print(f"   Success rate: {sent_count/(sent_count+failed_count)*100:.1f}%")
        print(f"   Master database: {config['spreadsheet_url']}")
    
    elif send_emails and len(companies_with_emails) == 0:
        print(f"\n❌ No companies with emails found for sending!")
    
    else:
        print(f"\n✅ Data collection completed. Run again with option 2 to send emails!")

if __name__ == "__main__":
    main()
