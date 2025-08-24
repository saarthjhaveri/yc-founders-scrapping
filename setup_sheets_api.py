#!/usr/bin/env python3
"""
Google Sheets API Setup for YC Companies Master Database
Sets up authentication and creates the master spreadsheet
"""

import gspread
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import json

# Scopes needed for Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

def setup_sheets_api():
    """
    Sets up Google Sheets API credentials.
    Uses the same OAuth flow as Gmail API but with Sheets permissions.
    """
    creds = None
    
    # Check if we have existing sheets credentials
    if os.path.exists('sheets_token.json'):
        creds = UserCredentials.from_authorized_user_file('sheets_token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("❌ credentials.json not found!")
                print("\n📋 To set up Google Sheets API:")
                print("1. Go to: https://console.cloud.google.com/")
                print("2. Select your project (or create a new one)")
                print("3. Enable Google Sheets API and Google Drive API")
                print("4. Go to 'Credentials' → 'Create Credentials' → 'OAuth 2.0 Client ID'")
                print("5. Choose 'Desktop application'")
                print("6. Download the JSON file and save as 'credentials.json'")
                print("7. Make sure to add your email as a test user in OAuth consent screen")
                return False
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('sheets_token.json', 'w') as token:
            token.write(creds.to_json())
            print("✅ Sheets credentials saved to sheets_token.json")
    
    # Test the credentials by creating a gspread client
    try:
        gc = gspread.authorize(creds)
        print(f"✅ Google Sheets API setup successful!")
        print(f"   Ready to create and manage spreadsheets!")
        
        # Test by listing existing spreadsheets (optional)
        try:
            sheets = gc.openall()
            print(f"   Found {len(sheets)} existing spreadsheets in your account")
        except Exception as e:
            print(f"   Note: Could not list spreadsheets ({e})")
        
        return True
    except Exception as e:
        print(f"❌ Error testing Google Sheets API: {e}")
        return False

def create_master_spreadsheet():
    """
    Create the master YC companies spreadsheet
    """
    if not os.path.exists('sheets_token.json'):
        print("❌ Sheets API not set up. Please run setup first!")
        return None
    
    try:
        # Authorize and create client
        creds = UserCredentials.from_authorized_user_file('sheets_token.json', SCOPES)
        gc = gspread.authorize(creds)
        
        # Create new spreadsheet
        spreadsheet_name = "YC Companies Master Database"
        
        print(f"Creating spreadsheet: {spreadsheet_name}")
        spreadsheet = gc.create(spreadsheet_name)
        
        # Get the first worksheet
        worksheet = spreadsheet.sheet1
        worksheet.update_title("Companies")
        
        # Set up headers
        headers = [
            'name', 'yc_url', 'batch', 'status', 'industry', 'website', 
            'location', 'description', 'team_size', 'slug',
            'first_seen', 'last_updated', 'email_fetched', 'founder_emails'
        ]
        
        # Update headers in first row
        worksheet.update('A1:N1', [headers])
        
        # Format headers (bold)
        worksheet.format('A1:N1', {'textFormat': {'bold': True}})
        
        # Get spreadsheet URL and ID
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
        
        print(f"✅ Master spreadsheet created successfully!")
        print(f"   Spreadsheet ID: {spreadsheet.id}")
        print(f"   URL: {spreadsheet_url}")
        
        # Save spreadsheet ID for future use
        config = {
            'spreadsheet_id': spreadsheet.id,
            'spreadsheet_url': spreadsheet_url,
            'worksheet_name': 'Companies'
        }
        
        with open('sheets_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"   Configuration saved to sheets_config.json")
        print(f"\n🎉 Master database is ready!")
        print(f"   You can view it at: {spreadsheet_url}")
        
        return spreadsheet
        
    except Exception as e:
        print(f"❌ Error creating spreadsheet: {e}")
        return None

if __name__ == "__main__":
    print("Google Sheets API Setup for YC Companies Database")
    print("=" * 60)
    
    # First set up API access
    if setup_sheets_api():
        print(f"\n📊 Setting up master database...")
        
        # Check if we already have a spreadsheet configured
        if os.path.exists('sheets_config.json'):
            with open('sheets_config.json', 'r') as f:
                config = json.load(f)
            
            print(f"✅ Master database already exists!")
            print(f"   Spreadsheet ID: {config['spreadsheet_id']}")
            print(f"   URL: {config['spreadsheet_url']}")
            
            # Ask if user wants to create a new one
            create_new = input(f"\nCreate a new master database? (y/n): ").strip().lower()
            if create_new == 'y':
                create_master_spreadsheet()
        else:
            # Create new spreadsheet
            create_master_spreadsheet()
    else:
        print(f"\n💥 Failed to set up Google Sheets API")
        print(f"   Please check the instructions above and try again")
