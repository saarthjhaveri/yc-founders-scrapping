# YC Ultimate Outreach Tool - Usage Examples

## 🚀 Quick Start Examples

### Example 1: Data Collection Only
```bash
python yc_outreach_tool.py

# Interactive prompts:
📋 What would you like to do?
1. Fetch companies and emails only (no sending)
2. Fetch companies, emails, AND send cold emails

Enter your choice (1 or 2): 1

Enter YC companies URL (or press Enter for default): 
# Press Enter for default or paste: https://www.ycombinator.com/companies?batch=Winter%202025&industry=B2B

# Result: Companies fetched, emails extracted, database updated
```

### Example 2: Full Outreach Campaign
```bash
python yc_outreach_tool.py

# Interactive prompts:
📋 What would you like to do?
Enter your choice (1 or 2): 2

Email Subject (default: 'this is a 30 second email'): Quick chat about automating customer support?

Email Body Options:
1. Use default template
2. Enter custom email body
Choose (1 or 2): 2

Enter your email body (use {founder_name} for personalization):
Hi {founder_name},

I noticed your company is building something interesting in the B2B space. 

We've built a tool that automates customer support requests (refunds, queries) across all channels so your team can focus on building instead of answering the same questions repeatedly.

Would you be interested in a quick 10-minute chat to see if this could help your team?

Best,
Saarth
END

# Result: Data collected + personalized emails sent to all founders
```

## 🎯 Specific Use Cases

### Target Recent YC Batches
```bash
python yc_outreach_tool.py "https://www.ycombinator.com/companies?batch=Summer%202025&batch=Spring%202025"
```

### Industry-Specific Outreach
```bash
# B2B Companies
python yc_outreach_tool.py "https://www.ycombinator.com/companies?industry=B2B"

# Healthcare Companies
python yc_outreach_tool.py "https://www.ycombinator.com/companies?industry=Healthcare"

# Consumer + Fintech
python yc_outreach_tool.py "https://www.ycombinator.com/companies?industry=Consumer&industry=Fintech"
```

### Geographic Targeting
```bash
# San Francisco Bay Area
python yc_outreach_tool.py "https://www.ycombinator.com/companies?region=San%20Francisco"

# Multiple Regions
python yc_outreach_tool.py "https://www.ycombinator.com/companies?region=San%20Francisco&region=New%20York"
```

### Company Size Targeting
```bash
# Early stage companies (small teams)
python yc_outreach_tool.py "https://www.ycombinator.com/companies?team_size=%5B%221%22%2C%2210%22%5D"

# Growing companies
python yc_outreach_tool.py "https://www.ycombinator.com/companies?team_size=%5B%2211%22%2C%22100%22%5D"
```

### Hiring Companies
```bash
# Companies currently hiring
python yc_outreach_tool.py "https://www.ycombinator.com/companies?isHiring=true"
```

## 📊 Expected Results

### First Run (New Database)
```
🎉 DATA COLLECTION COMPLETED!
   Total companies in master database: 47
   Companies processed this session: 47
   Companies with emails (this session): 31
   Master database: https://docs.google.com/spreadsheets/d/your-sheet-id

📧 Sample companies with emails:
   • Waffle: founders@waffle.ai
   • Rid: founders@rid.me
   • Pingo AI: founders@mypingoai.com
```

### Second Run (Incremental Update)
```
📊 Loaded 47 companies from master database
   Companies with emails: 31
   Companies needing emails: 16

🔄 Merging 23 new companies with master database...
  📊 Found 12 truly new companies
  📊 Skipping 11 existing companies

🎉 DATA COLLECTION COMPLETED!
   Total companies in master database: 59
   Companies processed this session: 23
   Companies with emails (this session): 8
```

### Full Campaign Results
```
🎉 ULTIMATE OUTREACH CAMPAIGN COMPLETED!
   Companies processed: 23
   Emails found: 8
   Emails sent: 15
   Emails failed: 1
   Success rate: 93.8%
   Master database: https://docs.google.com/spreadsheets/d/your-sheet-id
```

## 🔄 Workflow Patterns

### Weekly Outreach Routine
```bash
# Monday: Collect new companies
python yc_outreach_tool.py  # Option 1 (data only)

# Wednesday: Send emails to new companies  
python yc_outreach_tool.py  # Option 2 (send emails)

# Friday: Target different industry/batch
python yc_outreach_tool.py "https://www.ycombinator.com/companies?industry=Healthcare"
```

### Campaign-Specific Targeting
```bash
# Campaign 1: Early-stage B2B in SF
python yc_outreach_tool.py "https://www.ycombinator.com/companies?industry=B2B&region=San%20Francisco&team_size=%5B%221%22%2C%2210%22%5D"

# Campaign 2: Growing Consumer companies
python yc_outreach_tool.py "https://www.ycombinator.com/companies?industry=Consumer&team_size=%5B%2211%22%2C%22100%22%5D"

# Campaign 3: Hiring companies (any industry)
python yc_outreach_tool.py "https://www.ycombinator.com/companies?isHiring=true"
```

## 💡 Pro Tips

### 1. Start with Data Collection
Always run Option 1 first to build your database, then use Option 2 for targeted campaigns.

### 2. Use Specific Filters
More specific filters = more relevant prospects = higher response rates.

### 3. Personalize Your Message
Use the custom email body option to tailor your message to specific industries or company stages.

### 4. Monitor Your Database
Check your Google Sheets regularly to see your growing prospect database.

### 5. Respect Rate Limits
The tool includes built-in delays - don't try to bypass them.

## 🚨 Important Notes

- **Email Sending**: Only works if you've completed Gmail API setup
- **Duplicate Prevention**: Companies are never processed twice (based on YC slug)
- **Data Persistence**: Everything is stored in Google Sheets - no local files to lose
- **Rate Limiting**: Built-in delays respect YC and Gmail servers
- **Error Handling**: Failed operations are logged and don't stop the entire process

## 🎯 Success Metrics

Track these metrics in your Google Sheets:
- **Total Companies**: Growing database size
- **Email Discovery Rate**: % of companies with emails found
- **Email Send Success**: % of emails successfully delivered
- **Response Rate**: Track manually or via email analytics

Happy outreaching! 🚀
