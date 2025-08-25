# YC Email Extractor - Chrome Extension

A **fully self-contained** Chrome extension that extracts founder and company emails from Y Combinator company pages with **perfect filtering logic**.

## 🎯 **Key Features**

- 🔍 **Perfect Filtering**: Complete JavaScript implementation matching the robust Python logic
- 📧 **Smart Email Extraction**: Finds founder and contact emails from company pages  
- 🎨 **Clean YC-Themed UI**: Orange and white design matching Y Combinator's brand
- 📋 **Easy Copy**: One-click copy of all results to clipboard
- 🚀 **No Dependencies**: Pure JavaScript - no Python server required!
- ⚡ **All Filters Supported**: Batch, industry, region, team size, status, tags, stages, boolean filters

## 🏗 **Architecture: Pure JavaScript**

This extension is now **100% self-contained**:

1. **Complete Filtering Logic**: JavaScript implementation matching Python `yc_outreach_tool.py` exactly
2. **No External Dependencies**: No Python server, no setup required
3. **Full YC API Support**: Handles all YC URL parameters and edge cases

## 📦 **Installation**

### Simple One-Step Installation
1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer Mode** (toggle in top-right)
3. Click **"Load unpacked"** and select the `yc-email-extractor-extension` folder
4. Pin the extension (puzzle piece icon → pin YC Email Extractor)

**That's it!** No Python setup, no server to run.

## 🚀 **Usage**
1. **Navigate** to any YC companies page with filters:
   ```
   https://www.ycombinator.com/companies?batch=Spring%202025&regions=Austria&regions=France
   ```

2. **Click "Generate Emails"** button that appears on the page

3. **View Results** in the clean modal window

4. **Copy Results** with one click

## ✅ **Perfect Filtering Implementation**

### **All YC Filters Supported**
- ✅ **Batches**: `batch=Summer%202025&batch=Winter%202025`
- ✅ **Industries**: `industry=Consumer&industry=B2B` (checks both `industry` and `industries` fields)
- ✅ **Regions**: `regions=Austria&regions=France` (checks `regions` array AND `all_locations` string)
- ✅ **Team Size**: `team_size=[5,50]` or `team_size=1,000+` (handles ranges and plus notation)
- ✅ **Status**: `status=Active&status=Acquired`
- ✅ **Tags**: Searches both `tags` and `tags_highlighted` arrays
- ✅ **Stages**: `stage=Early&stage=Growth`
- ✅ **Boolean Filters**: `top_company=true&isHiring=true&nonprofit=false`
- ✅ **App/Demo Filters**: `app_video_public=true&demo_day_video_public=true`
- ✅ **Content Filters**: `app_answers=true&question_answers=true`

### **Smart Email Extraction**
- ✅ Removes scripts, styles, nav, footer, header (like BeautifulSoup)
- ✅ Cleans text exactly like Python implementation
- ✅ Uses same regex pattern: `/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g`
- ✅ Filters out same exclusion patterns as Python version

## 🔧 **How It Works**

```
YC Page → Extension Button → JavaScript Filtering → Email Extraction → Clean Results
```

1. **Extension detects** YC companies page
2. **Parses URL filters** using exact Python logic
3. **Fetches & filters companies** from YC OSS API with comprehensive filtering
4. **Extracts emails** from individual company pages
5. **Displays results** in clean YC-themed UI

## 🎨 **UI Design**

**YC Brand Colors:**
- Primary: `#ff6600` (YC Orange)
- Secondary: `#ffffff` (White)  
- Text: `#333333` (Dark Gray)
- Borders: `#e0e0e0` (Light Gray)

**Design Principles:**
- Clean and minimal
- No unnecessary shadows or effects
- Professional typography
- Consistent with YC's brand

## 🛠 **Troubleshooting**

### Button Not Appearing
- Ensure you're on `ycombinator.com/companies` page
- Refresh the page
- Check extension is enabled in `chrome://extensions/`

### Wrong Number of Companies
- Open browser console (F12 → Console) to see filtering debug info
- Verify your URL parameters are correct
- The console logs show exactly what filters are applied and sample companies

### Extension Not Working
- Reload the extension in `chrome://extensions/`
- Check browser console for any JavaScript errors
- Ensure you're using a modern Chrome version

## 📁 **File Structure**

```
yc-email-extractor-extension/
├── manifest.json          # Extension config
├── content.js            # Injects button on YC pages  
├── background.js         # Complete filtering & extraction logic (400+ lines!)
├── popup.html           # Clean results display
├── popup.js             # Results interaction
├── styles.css           # YC-themed styling
└── README.md           # This file
```

## 🔄 **Development Workflow**

### Making Changes to Filtering Logic
1. **Edit** `background.js` (contains all the logic)
2. **Reload** extension in `chrome://extensions/`
3. **Test** on YC page

### Making Changes to UI
1. **Edit** extension files (`styles.css`, `popup.html`, etc.)
2. **Reload** extension in `chrome://extensions/`
3. **Test** on YC page

## 🎉 **Benefits of Pure JavaScript Architecture**

- ✅ **Zero Dependencies**: No Python, no server, no setup
- ✅ **Instant Startup**: Works immediately after installation
- ✅ **Perfect Filtering**: Complete implementation of all YC filter types
- ✅ **Easy Distribution**: Single folder, ready to share
- ✅ **Cross-Platform**: Works on any system with Chrome

## 🚀 **Example Usage**

**Test URL:**
```
https://www.ycombinator.com/companies?batch=Spring%202025&regions=Austria&regions=France
```

**Expected Results:**
- Server logs: `Filtered to 3 companies` (not 143!)
- Extension shows: Clean list of Austrian/French companies with emails
- One-click copy: `Company Name - Email Address` format

---

**Perfect filtering + Clean UI = Happy email hunting! 🎯**