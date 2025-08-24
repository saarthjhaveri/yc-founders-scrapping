#!/usr/bin/env python3
"""
Step 3: Cold Email Sender
Sends personalized cold emails to YC founders using Gmail API
"""

import pandas as pd
import time
import os
import sys
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import re

def setup_gmail_service():
    """
    Set up Gmail API service
    """
    if not os.path.exists('token.json'):
        print("❌ Gmail API not set up. Please run setup_gmail_api.py first!")
        return None
    
    try:
        creds = Credentials.from_authorized_user_file('token.json')
        
        # Refresh credentials if needed
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        service = build('gmail', 'v1', credentials=creds)
        
        # Service is ready (we only have send permission, not profile read)
        print(f"✅ Gmail API connected and ready to send emails")
        
        return service
    except Exception as e:
        print(f"❌ Error setting up Gmail service: {e}")
        return None

def extract_founder_name(company_name, email):
    """
    Try to extract founder name from email or use company name/generic greeting
    """
    # Try to extract name from email (before @)
    email_prefix = email.split('@')[0].lower()
    
    # Common generic email prefixes that should use company name or generic greeting
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

def create_email_message(to_email, founder_name, company_name):
    """
    Create the cold email message
    """
    subject = "this is a 30 second email"
    
    body = f"""Hi {founder_name},

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

    # Create message
    message = MIMEText(body)
    message['to'] = to_email
    message['subject'] = subject
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_email(service, email_message):
    """
    Send email using Gmail API
    """
    try:
        message = service.users().messages().send(userId='me', body=email_message).execute()
        return True, message['id']
    except Exception as e:
        return False, str(e)

def send_cold_emails():
    """
    Main function to send cold emails to all founders
    """
    # Setup Gmail service
    service = setup_gmail_service()
    if not service:
        return
    
    try:
        # Load companies with emails
        df = pd.read_csv('yc_companies.csv')
        print(f"Loaded {len(df)} companies from CSV")
        
        # Filter companies that have emails and haven't been emailed yet
        companies_with_emails = df[(df['founder_emails'] != '') & (df['founder_emails'].notna())].copy()
        
        # Add email_sent column if it doesn't exist
        if 'email_sent' not in df.columns:
            df['email_sent'] = False
            companies_with_emails['email_sent'] = False
        
        companies_to_email = companies_with_emails[companies_with_emails['email_sent'] == False].copy()
        
        print(f"Found {len(companies_with_emails)} companies with emails")
        print(f"Need to email {len(companies_to_email)} companies")
        
        if len(companies_to_email) == 0:
            print("All companies have already been emailed!")
            return
        
        # Show preview
        print(f"\n📧 EMAIL PREVIEW:")
        print("=" * 60)
        sample_company = companies_to_email.iloc[0]
        sample_emails = sample_company['founder_emails'].split(';')
        sample_email = sample_emails[0].strip()
        sample_founder = extract_founder_name(sample_company['name'], sample_email)
        
        preview_message = create_email_message(sample_email, sample_founder, sample_company['name'])
        preview_body = base64.urlsafe_b64decode(preview_message['raw']).decode()
        print(preview_body)
        print("=" * 60)
        
        # Confirm before sending
        total_emails = sum(len(row['founder_emails'].split(';')) for _, row in companies_to_email.iterrows())
        print(f"\n📊 SUMMARY:")
        print(f"   Companies to email: {len(companies_to_email)}")
        print(f"   Total emails to send: {total_emails}")
        print(f"   Rate: 1 email every 5 seconds (to avoid spam limits)")
        print(f"   Estimated time: {total_emails * 5 / 60:.1f} minutes")
        
        confirm = input(f"\nSend {total_emails} cold emails? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return
        
        # Send emails
        sent_count = 0
        failed_count = 0
        
        for index, row in companies_to_email.iterrows():
            company_name = row['name']
            emails_str = row['founder_emails']
            
            # Split multiple emails
            emails = [email.strip() for email in emails_str.split(';') if email.strip()]
            
            print(f"\n[{sent_count + failed_count + 1}] {company_name}")
            
            company_sent = False
            for email in emails:
                if not email or '@' not in email:
                    continue
                
                founder_name = extract_founder_name(company_name, email)
                
                print(f"  📧 Sending to {email} (Hi {founder_name})")
                
                # Create and send email
                email_message = create_email_message(email, founder_name, company_name)
                success, result = send_email(service, email_message)
                
                if success:
                    print(f"     ✅ Sent successfully (ID: {result})")
                    sent_count += 1
                    company_sent = True
                else:
                    print(f"     ❌ Failed: {result}")
                    failed_count += 1
                
                # Rate limiting - 5 seconds between emails
                time.sleep(5)
            
            # Mark company as emailed if at least one email was sent
            if company_sent:
                df.loc[index, 'email_sent'] = True
            
            # Save progress every 10 companies
            if (sent_count + failed_count) % 10 == 0:
                df.to_csv('yc_companies.csv', index=False)
                print(f"  💾 Progress saved")
        
        # Final save
        df.to_csv('yc_companies.csv', index=False)
        
        # Summary
        print(f"\n✅ COLD EMAIL CAMPAIGN COMPLETED!")
        print(f"   Emails sent: {sent_count}")
        print(f"   Emails failed: {failed_count}")
        print(f"   Success rate: {sent_count/(sent_count+failed_count)*100:.1f}%")
        
    except FileNotFoundError:
        print("❌ yc_companies.csv not found. Please run the previous steps first!")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_single_email(email_address):
    """
    Test sending email to a single address
    """
    service = setup_gmail_service()
    if not service:
        return
    
    founder_name = extract_founder_name("Test Company", email_address)
    
    print(f"🧪 TESTING SINGLE EMAIL")
    print(f"=" * 60)
    print(f"To: {email_address}")
    print(f"Founder name: {founder_name}")
    
    # Create and preview email
    email_message = create_email_message(email_address, founder_name, "Test Company")
    preview_body = base64.urlsafe_b64decode(email_message['raw']).decode()
    print(f"\nEMAIL PREVIEW:")
    print("-" * 40)
    print(preview_body)
    print("-" * 40)
    
    confirm = input(f"\nSend test email to {email_address}? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    success, result = send_email(service, email_message)
    
    if success:
        print(f"✅ Test email sent successfully! (ID: {result})")
    else:
        print(f"❌ Failed to send test email: {result}")

if __name__ == "__main__":
    print("YC Cold Email Sender")
    print("=" * 50)
    print("Sends personalized cold emails to YC founders using Gmail API")
    print()
    
    # Check if any argument is provided for testing
    if len(sys.argv) > 1:
        # Hardcoded test email for verification
        test_email = "saarth@statusai.com"
        print(f"🧪 TEST MODE: Sending test email to {test_email}")
        test_single_email(test_email)
    else:
        print(f"💡 Usage:")
        print(f"   python 3_send_cold_emails.py                    # Send emails to all founders")
        print(f"   python 3_send_cold_emails.py test               # Send test email to saarth@statusai.com")
        print()
        send_cold_emails()
