#!/usr/bin/env python3
"""
Step 2: Simple Email Extraction using Regex
Fetches emails from YC company pages using regex and stores them as founder emails
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import sys

def extract_emails_from_text(text):
    """
    Extract all email addresses from text using regex
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return list(set(emails))  # Remove duplicates

def fetch_emails_from_company_page(company_url, company_name):
    """
    Fetch emails from a single YC company page using regex
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print(f"Fetching emails for: {company_name}")
        response = requests.get(company_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get all text from the page
        page_text = soup.get_text()
        
        # Extract all emails from the page
        all_emails = extract_emails_from_text(page_text)
        
        if all_emails:
            print(f"  ✅ Found emails: {all_emails}")
            return all_emails
        else:
            print(f"  ❌ No emails found")
            return []
            
    except requests.RequestException as e:
        print(f"  ❌ Error fetching {company_url}: {e}")
        return []
    except Exception as e:
        print(f"  ❌ Error parsing {company_url}: {e}")
        return []

def test_single_url(company_url):
    """
    Test email extraction on a single URL
    """
    # Extract company name from URL
    company_name = company_url.split('/')[-1].replace('-', ' ').title()
    
    print(f"🧪 TESTING SINGLE URL")
    print(f"=" * 60)
    print(f"Company: {company_name}")
    print(f"URL: {company_url}")
    print("-" * 60)
    
    # Fetch emails
    emails = fetch_emails_from_company_page(company_url, company_name)
    
    print("-" * 60)
    print(f"🎯 RESULTS:")
    print(f"   Total emails found: {len(emails)}")
    print(f"   Emails: {emails}")
    print("=" * 60)

def fetch_all_emails():
    """
    Main function to fetch emails for all companies
    """
    try:
        # Load the companies CSV
        df = pd.read_csv('yc_companies.csv')
        print(f"Loaded {len(df)} companies from yc_companies.csv")
        
        # Filter companies that haven't had emails fetched yet
        companies_to_process = df[df['email_fetched'] == False].copy()
        print(f"Processing {len(companies_to_process)} companies that need email extraction")
        
        if len(companies_to_process) == 0:
            print("All companies already processed!")
            return
        
        # Process each company
        processed_count = 0
        for index, row in companies_to_process.iterrows():
            company_name = row['name']
            company_url = row['yc_url']
            
            print(f"\n[{processed_count + 1}/{len(companies_to_process)}]", end=" ")
            
            # Fetch emails using regex
            emails = fetch_emails_from_company_page(company_url, company_name)
            
            # Update the dataframe - put all emails in founder_emails column
            df.loc[index, 'founder_emails'] = '; '.join(emails)
            df.loc[index, 'support_emails'] = ''  # Keep empty
            df.loc[index, 'email_fetched'] = True
            
            processed_count += 1
            
            # Save progress every 10 companies
            if processed_count % 10 == 0:
                df.to_csv('yc_companies.csv', index=False)
                print(f"  💾 Progress saved after {processed_count} companies")
            
            # Rate limiting to be respectful
            time.sleep(1)  # 1 second delay between requests
        
        # Final save
        df.to_csv('yc_companies.csv', index=False)
        
        # Print summary
        companies_with_emails = df[df['founder_emails'] != '']
        print(f"\n✅ Email extraction completed!")
        print(f"Total companies processed: {len(companies_to_process)}")
        print(f"Companies with emails found: {len(companies_with_emails)}")
        print(f"Success rate: {len(companies_with_emails)/len(df)*100:.1f}%")
        
        # Show some examples
        print("\nSample results:")
        sample_with_emails = companies_with_emails.head(5)
        for _, row in sample_with_emails.iterrows():
            if row['founder_emails']:
                print(f"  📧 {row['name']}: {row['founder_emails']}")
        
    except FileNotFoundError:
        print("❌ yc_companies.csv not found. Please run 1_fetch_companies_api.py first!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("YC Founder Email Scraper - Simple Regex Version")
    print("=" * 60)
    print("This tool uses regex to extract all emails from YC company pages.")
    print("All emails are stored in the founder_emails column.\n")
    
    # Check if URL is provided as command line argument
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        if 'ycombinator.com/companies/' in test_url:
            test_single_url(test_url)
        else:
            print(f"❌ Invalid URL. Please provide a YC company URL like:")
            print(f"   https://www.ycombinator.com/companies/approval-ai")
    else:
        print(f"💡 Usage:")
        print(f"   python 2_fetch_emails_simple.py                                    # Process all companies in CSV")
        print(f"   python 2_fetch_emails_simple.py https://www.ycombinator.com/companies/approval-ai  # Test single URL")
        print()
        fetch_all_emails()
