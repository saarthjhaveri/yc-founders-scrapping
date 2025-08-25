#!/usr/bin/env python3
"""
YC Extension Server - Local API for Chrome Extension
Wraps the yc_outreach_tool.py logic in a simple Flask server
"""

from flask import Flask, request, jsonify
import sys
import os

# Import our existing logic
from yc_outreach_tool import (
    parse_yc_url_filters,
    fetch_yc_companies, 
    extract_emails_from_page
)

app = Flask(__name__)

# Manual CORS handler for Chrome extensions
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'YC Extension Server is running'
    })

@app.route('/extract', methods=['POST'])
def extract_emails():
    """
    Extract emails from YC companies URL
    Expects: {"url": "https://www.ycombinator.com/companies?..."}
    Returns: {"success": true, "companies": [{"name": "...", "emails": [...]}]}
    """
    try:
        # Get URL from request
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing URL in request body'
            }), 400
        
        yc_url = data['url']
        print(f"🔍 Processing URL: {yc_url}")
        
        # Step 1: Parse URL filters (using our perfect Python logic)
        filters = parse_yc_url_filters(yc_url)
        print(f"📋 Parsed filters: {filters}")
        
        # Step 2: Fetch companies (using our perfect Python logic)
        companies = fetch_yc_companies(filters)
        print(f"🏢 Found {len(companies)} companies")
        
        if not companies:
            return jsonify({
                'success': True,
                'companies': [],
                'message': 'No companies found matching filters'
            })
        
        # Step 3: Extract emails from each company
        results = []
        
        for i, company in enumerate(companies):
            print(f"📧 Processing {i+1}/{len(companies)}: {company.get('name', 'Unknown')}")
            
            try:
                # Extract emails using our perfect Python logic
                emails = extract_emails_from_page(
                    company.get('url', ''), 
                    company.get('name', 'Unknown')
                )
                
                results.append({
                    'name': company.get('name', 'Unknown'),
                    'url': company.get('url', ''),
                    'emails': emails,
                    'batch': company.get('batch', ''),
                    'industry': company.get('industry', '')
                })
                
            except Exception as e:
                print(f"❌ Error processing {company.get('name', 'Unknown')}: {e}")
                results.append({
                    'name': company.get('name', 'Unknown'),
                    'url': company.get('url', ''),
                    'emails': [],
                    'batch': company.get('batch', ''),
                    'industry': company.get('industry', '')
                })
        
        # Filter results to only include companies with emails
        companies_with_emails = [r for r in results if r['emails']]
        
        print(f"✅ Completed! Found emails for {len(companies_with_emails)}/{len(results)} companies")
        
        return jsonify({
            'success': True,
            'companies': results,
            'summary': {
                'total_companies': len(results),
                'companies_with_emails': len(companies_with_emails),
                'success_rate': f"{len(companies_with_emails)/len(results)*100:.1f}%" if results else "0%"
            }
        })
        
    except Exception as e:
        print(f"❌ Server error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/extract', methods=['OPTIONS'])
def extract_options():
    """Handle preflight requests for /extract endpoint"""
    return jsonify({'status': 'ok'})

@app.route('/filters', methods=['POST'])
def parse_filters_only():
    """
    Parse YC URL filters without extracting emails
    Expects: {"url": "https://www.ycombinator.com/companies?..."}
    Returns: {"success": true, "filters": {...}, "company_count": 123}
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing URL in request body'
            }), 400
        
        yc_url = data['url']
        
        # Parse filters and get company count
        filters = parse_yc_url_filters(yc_url)
        companies = fetch_yc_companies(filters)
        
        return jsonify({
            'success': True,
            'filters': filters,
            'company_count': len(companies),
            'companies': [{'name': c.get('name'), 'batch': c.get('batch'), 'industry': c.get('industry')} for c in companies[:10]]  # First 10 for preview
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 YC Extension Server Starting...")
    print("📡 Server will run on: http://localhost:5001")
    print("🔗 Chrome extension will connect to this server")
    print("⚠️  Keep this running while using the extension")
    print("-" * 50)
    
    # Run server on port 5001 (5000 is used by macOS AirPlay)
    app.run(
        host='localhost',
        port=5001,
        debug=True,
        use_reloader=False  # Avoid double startup in debug mode
    )
