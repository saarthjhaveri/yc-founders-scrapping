#!/usr/bin/env python3
"""
Gmail API Setup Script
This script helps you set up Gmail API credentials for sending emails
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scope for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def setup_gmail_credentials():
    """
    Set up Gmail API credentials
    """
    creds = None
    
    # Check if we already have valid credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("✅ Refreshed existing credentials")
            except Exception as e:
                print(f"❌ Error refreshing credentials: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists('credentials.json'):
                print("❌ credentials.json not found!")
                print("\n📋 To set up Gmail API:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project or select existing one")
                print("3. Enable Gmail API")
                print("4. Go to 'Credentials' → 'Create Credentials' → 'OAuth 2.0 Client IDs'")
                print("5. Choose 'Desktop application'")
                print("6. Download the JSON file and save it as 'credentials.json' in this folder")
                print("\n💡 Then run this script again!")
                return False
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                print("✅ Successfully authenticated with Gmail API")
            except Exception as e:
                print(f"❌ Error during authentication: {e}")
                return False
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            print("✅ Credentials saved to token.json")
    
    # Test the credentials by building the service (we only need send permission)
    try:
        service = build('gmail', 'v1', credentials=creds)
        print(f"✅ Gmail API setup successful!")
        print(f"   Gmail send service initialized")
        print(f"   Ready to send emails!")
        return True
    except Exception as e:
        print(f"❌ Error testing Gmail API: {e}")
        return False

if __name__ == "__main__":
    print("Gmail API Setup for Cold Email Sender")
    print("=" * 50)
    
    if setup_gmail_credentials():
        print("\n🎉 Gmail API is ready!")
        print("You can now use 3_send_cold_emails.py to send emails")
    else:
        print("\n❌ Gmail API setup failed")
        print("Please follow the instructions above and try again")
