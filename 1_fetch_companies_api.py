#!/usr/bin/env python3
"""
YC Company Fetcher using YC OSS API - Clean and Fast
Fetches companies from https://yc-oss.github.io/api/companies/all.json
and filters based on URL parameters
"""

import requests
import pandas as pd
from urllib.parse import urlparse, parse_qs, unquote
import re
import json

def parse_team_size_filter(team_size_param):
    """
    Parse team size filter which comes as JSON array like ["5","1,000+"]
    """
    try:
        if team_size_param.startswith('[') and team_size_param.endswith(']'):
            # It's a JSON array
            team_sizes = json.loads(unquote(team_size_param))
            return team_sizes
        else:
            # Single value
            return [unquote(team_size_param)]
    except:
        return []

def parse_yc_url_filters(url):
    """
    Parse YC companies URL to extract ALL possible filters
    
    Supports all YC filter parameters:
    - batch: Company batch (e.g., "Summer 2025")
    - industry: Industry category (e.g., "Consumer")
    - region: Geographic region
    - status: Company status (Active, Inactive, etc.)
    - team_size: Team size range (e.g., ["5","1,000+"])
    - top_company: Top company flag
    - nonprofit: Nonprofit flag
    - isHiring: Currently hiring flag
    - app_video_public: Has public application video
    - demo_day_video_public: Has public demo day video
    - app_answers: Has application answers
    - question_answers: Has bonus question answers
    - tags: Company tags
    - stage: Company stage (Early, Growth, etc.)
    
    Example URL: https://www.ycombinator.com/companies?app_video_public=true&batch=Summer%202025&team_size=%5B%225%22%2C%221%2C000%2B%22%5D
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    
    # Helper function to get first value or list of values
    def get_param(key, as_list=True):
        values = params.get(key, [])
        if not values:
            return [] if as_list else None
        # URL decode values
        decoded_values = [unquote(v) for v in values]
        return decoded_values if as_list else decoded_values[0]
    
    # Helper function to get boolean parameter
    def get_bool_param(key):
        value = get_param(key, as_list=False)
        if value is None:
            return None
        return value.lower() in ['true', '1', 'yes']
    
    # Extract all possible filters
    filters = {
        # Basic filters
        'batches': get_param('batch'),
        'industries': get_param('industry'),
        'regions': get_param('region'),
        'statuses': get_param('status'),
        'tags': get_param('tags'),
        'stages': get_param('stage'),
        
        # Team size (special handling for JSON array)
        'team_sizes': [],
        
        # Boolean filters
        'top_company': get_bool_param('top_company'),
        'nonprofit': get_bool_param('nonprofit'),
        'is_hiring': get_bool_param('isHiring'),
        'app_video_public': get_bool_param('app_video_public'),
        'demo_day_video_public': get_bool_param('demo_day_video_public'),
        'app_answers': get_bool_param('app_answers'),
        'question_answers': get_bool_param('question_answers'),
    }
    
    # Special handling for team_size
    if 'team_size' in params:
        team_size_raw = params['team_size'][0]
        filters['team_sizes'] = parse_team_size_filter(team_size_raw)
    
    # Clean up empty filters
    cleaned_filters = {}
    for key, value in filters.items():
        if value is not None and value != []:
            cleaned_filters[key] = value
    
    print(f"Parsed filters from URL:")
    for key, value in cleaned_filters.items():
        print(f"  {key}: {value}")
    
    return cleaned_filters

def fetch_all_yc_companies():
    """
    Fetch all YC companies from the OSS API
    """
    api_url = "https://yc-oss.github.io/api/companies/all.json"
    
    print(f"Fetching all YC companies from: {api_url}")
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        companies = response.json()
        print(f"✅ Successfully fetched {len(companies)} companies from YC OSS API")
        
        return companies
        
    except requests.RequestException as e:
        print(f"❌ Error fetching companies: {e}")
        return None
    except Exception as e:
        print(f"❌ Error parsing JSON: {e}")
        return None

def parse_team_size_range(team_size_str):
    """
    Parse team size string to get numeric range for comparison
    Returns (min_size, max_size) tuple
    """
    if not team_size_str:
        return (0, 0)
    
    # Handle special cases
    if '1,000+' in team_size_str or '1000+' in team_size_str:
        return (1000, float('inf'))
    
    # Extract numbers from string
    numbers = re.findall(r'\d+', str(team_size_str).replace(',', ''))
    if not numbers:
        return (0, 0)
    
    if len(numbers) == 1:
        num = int(numbers[0])
        return (num, num)
    else:
        return (int(numbers[0]), int(numbers[1]))

def matches_team_size_filter(company_team_size, filter_team_sizes):
    """
    Check if company team size matches any of the filter team size ranges
    """
    if not filter_team_sizes:
        return True
    
    company_size = company_team_size or 0
    
    for filter_size in filter_team_sizes:
        min_size, max_size = parse_team_size_range(filter_size)
        
        if min_size <= company_size <= max_size:
            return True
        
        # Special handling for ranges like "5" meaning "5 or more"
        if filter_size == "5" and company_size >= 5:
            return True
    
    return False

def filter_companies(companies, filters):
    """
    Filter companies based on ALL provided filters
    """
    filtered_companies = []
    total_companies = len(companies)
    
    print(f"Filtering {total_companies} companies...")
    
    for i, company in enumerate(companies):
        # Progress indicator for large datasets
        if i % 1000 == 0 and i > 0:
            print(f"  Processed {i}/{total_companies} companies...")
        
        # Check batch filter
        if 'batches' in filters:
            company_batch = company.get('batch', '')
            if not any(batch.lower() in company_batch.lower() for batch in filters['batches']):
                continue
        
        # Check industry filter
        if 'industries' in filters:
            company_industry = company.get('industry', '')
            company_industries = company.get('industries', [])
            
            # Check main industry field
            industry_match = any(industry.lower() in company_industry.lower() for industry in filters['industries'])
            
            # Check industries array
            if not industry_match and company_industries:
                industry_match = any(
                    any(filter_industry.lower() in comp_industry.lower() 
                        for comp_industry in company_industries)
                    for filter_industry in filters['industries']
                )
            
            if not industry_match:
                continue
        
        # Check region filter
        if 'regions' in filters:
            company_regions = company.get('regions', [])
            company_locations = company.get('all_locations', '')
            
            region_match = any(
                any(filter_region.lower() in comp_region.lower() 
                    for comp_region in company_regions)
                for filter_region in filters['regions']
            )
            
            # Also check locations string
            if not region_match:
                region_match = any(
                    filter_region.lower() in company_locations.lower()
                    for filter_region in filters['regions']
                )
            
            if not region_match:
                continue
        
        # Check status filter
        if 'statuses' in filters:
            company_status = company.get('status', '')
            if not any(status.lower() in company_status.lower() for status in filters['statuses']):
                continue
        
        # Check tags filter
        if 'tags' in filters:
            company_tags = company.get('tags', [])
            tags_match = any(
                any(filter_tag.lower() in comp_tag.lower() 
                    for comp_tag in company_tags)
                for filter_tag in filters['tags']
            )
            if not tags_match:
                continue
        
        # Check stage filter
        if 'stages' in filters:
            company_stage = company.get('stage', '')
            if not any(stage.lower() in company_stage.lower() for stage in filters['stages']):
                continue
        
        # Check team size filter
        if 'team_sizes' in filters:
            company_team_size = company.get('team_size', 0)
            if not matches_team_size_filter(company_team_size, filters['team_sizes']):
                continue
        
        # Check boolean filters
        boolean_filters = [
            ('top_company', 'top_company'),
            ('nonprofit', 'nonprofit'),
            ('is_hiring', 'isHiring'),
            ('app_video_public', 'app_video_public'),
            ('demo_day_video_public', 'demo_day_video_public'),
            ('app_answers', 'app_answers'),
            ('question_answers', 'question_answers'),
        ]
        
        skip_company = False
        for filter_key, company_key in boolean_filters:
            if filter_key in filters:
                filter_value = filters[filter_key]
                company_value = company.get(company_key, False)
                
                # Convert to boolean if needed
                if isinstance(company_value, str):
                    company_value = company_value.lower() in ['true', '1', 'yes']
                
                if filter_value != company_value:
                    skip_company = True
                    break
        
        if skip_company:
            continue
        
        # If we reach here, company matches all filters
        filtered_companies.append(company)
    
    print(f"  Filtering complete: {len(filtered_companies)} companies match criteria")
    return filtered_companies

def create_companies_csv(companies, filename='yc_companies.csv'):
    """
    Create CSV file with company data in the format needed for email extraction
    """
    csv_data = []
    
    for company in companies:
        csv_data.append({
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
            'email_fetched': False,
            'founder_emails': '',
            'support_emails': ''
        })
    
    df = pd.DataFrame(csv_data)
    df.to_csv(filename, index=False)
    
    print(f"\n✅ Successfully saved {len(csv_data)} companies to {filename}")
    print("\nFirst 5 companies:")
    print(df[['name', 'batch', 'industry', 'location', 'yc_url']].head())
    
    return df

def fetch_yc_companies_from_url(yc_url):
    """
    Main function to fetch and filter YC companies based on URL
    """
    print("YC Company Fetcher using YC OSS API")
    print("=" * 50)
    print(f"Target URL: {yc_url}")
    
    # Parse filters from URL
    filters = parse_yc_url_filters(yc_url)
    
    # Fetch all companies
    all_companies = fetch_all_yc_companies()
    if not all_companies:
        return None
    
    # Filter companies
    print(f"\nFiltering companies...")
    filtered_companies = filter_companies(all_companies, filters)
    
    print(f"✅ Filtered to {len(filtered_companies)} companies matching criteria")
    
    if not filtered_companies:
        print("❌ No companies match the specified filters")
        return None
    
    # Create CSV
    df = create_companies_csv(filtered_companies)
    
    return df

if __name__ == "__main__":
    import sys
    
    # Check if URL is provided as command line argument
    if len(sys.argv) > 1:
        yc_url = sys.argv[1]
    else:
        # Default URL - you can change this
        yc_url = "https://www.ycombinator.com/companies?batch=Summer%202025&batch=Spring%202025&industry=Consumer"
        print("💡 Tip: You can also provide a YC URL as argument:")
        print("   python 1_fetch_companies_api.py 'https://www.ycombinator.com/companies?batch=...'\n")
    
    companies_df = fetch_yc_companies_from_url(yc_url)
    
    if companies_df is not None:
        print(f"\n🎉 Success! Fetched {len(companies_df)} companies")
        print("Next step: Run 'python 2_fetch_emails.py' to extract emails")
        print("\nSample companies:")
        for _, company in companies_df.head(3).iterrows():
            print(f"  • {company['name']} ({company['batch']}) - {company['yc_url']}")
    else:
        print("\n💥 Failed to fetch companies")
