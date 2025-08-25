// YC Email Extractor - Background Script
// Complete JavaScript implementation matching Python logic exactly

console.log('YC Email Extractor: Background script loaded');

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extractEmails') {
        handleEmailExtraction(request.url)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ success: false, error: error.message }));
        
        // Return true to indicate we'll send response asynchronously
        return true;
    }
});

// Main email extraction function - fully self-contained
async function handleEmailExtraction(url) {
    try {
        console.log('YC Email Extractor: Starting extraction for URL:', url);
        
        // Step 1: Parse URL filters (exact Python logic)
        const filters = parseYCUrlFilters(url);
        console.log('YC Email Extractor: Parsed filters:', filters);
        
        // Step 2: Fetch companies from YC API (exact Python logic)
        const companies = await fetchYCCompanies(filters);
        console.log('YC Email Extractor: Found companies:', companies.length);
        
        if (companies.length === 0) {
            return { 
                success: true, 
                data: [],
                summary: { total_companies: 0, companies_with_emails: 0 }
            };
        }
        
        // Step 3: Extract emails from ALL companies
        console.log('YC Email Extractor: Processing all', companies.length, 'companies');
        
        const results = [];
        
        for (let i = 0; i < companies.length; i++) {
            const company = companies[i];
            console.log(`YC Email Extractor: Processing ${i + 1}/${companies.length}: ${company.name}`);
            
            try {
                const emails = await extractEmailsFromCompanyPage(company.url);
                results.push({
                    name: company.name,
                    url: company.url,
                    emails: emails,
                    batch: company.batch,
                    industry: company.industry
                });
                
                // Small delay to be respectful
                if (i < companies.length - 1) {
                    await sleep(500);
                }
            } catch (error) {
                console.error('YC Email Extractor: Error processing company:', company.name, error);
                results.push({
                    name: company.name,
                    url: company.url,
                    emails: [],
                    batch: company.batch,
                    industry: company.industry
                });
            }
        }
        
        const companiesWithEmails = results.filter(r => r.emails && r.emails.length > 0);
        
        console.log('YC Email Extractor: Extraction completed');
        console.log(`YC Email Extractor: Found emails for ${companiesWithEmails.length}/${results.length} companies`);
        
        return { 
            success: true, 
            data: results,
            summary: {
                total_companies: results.length,
                companies_with_emails: companiesWithEmails.length,
                success_rate: results.length > 0 ? `${(companiesWithEmails.length/results.length*100).toFixed(1)}%` : "0%"
            }
        };
        
    } catch (error) {
        console.error('YC Email Extractor: Error in handleEmailExtraction:', error);
        return { success: false, error: error.message };
    }
}

// Parse YC URL filters - EXACT match to Python logic
function parseYCUrlFilters(url) {
    const urlObj = new URL(url);
    const params = new URLSearchParams(urlObj.search);
    
    // Helper function to get parameters (matches Python get_param)
    function getParam(key, asList = true) {
        const values = params.getAll(key);
        if (values.length === 0) {
            return asList ? [] : null;
        }
        const decodedValues = values.map(v => decodeURIComponent(v));
        return asList ? decodedValues : decodedValues[0];
    }
    
    // Helper function for boolean parameters (matches Python get_bool_param)
    function getBoolParam(key) {
        const value = getParam(key, false);
        if (value === null) {
            return null;
        }
        return ['true', '1', 'yes'].includes(value.toLowerCase());
    }
    
    const filters = {
        batches: getParam('batch'),
        industries: getParam('industry'),
        regions: getParam('regions').concat(getParam('region')), // Handle both 'regions' and 'region'
        statuses: getParam('status'),
        tags: getParam('tags'),
        stages: getParam('stage'),
        team_sizes: [],
        top_company: getBoolParam('top_company'),
        nonprofit: getBoolParam('nonprofit'),
        is_hiring: getBoolParam('isHiring'),
        app_video_public: getBoolParam('app_video_public'),
        demo_day_video_public: getBoolParam('demo_day_video_public'),
        app_answers: getBoolParam('app_answers'),
        question_answers: getBoolParam('question_answers'),
    };
    
    // Handle team_size filter (matches Python logic exactly)
    if (params.has('team_size')) {
        const teamSizeRaw = params.get('team_size');
        try {
            if (teamSizeRaw.startsWith('[') && teamSizeRaw.endsWith(']')) {
                filters.team_sizes = JSON.parse(decodeURIComponent(teamSizeRaw));
            } else {
                filters.team_sizes = [decodeURIComponent(teamSizeRaw)];
            }
        } catch (e) {
            filters.team_sizes = [];
        }
    }
    
    // Clean up empty filters (matches Python logic)
    const cleanedFilters = {};
    for (const [key, value] of Object.entries(filters)) {
        if (value !== null && value !== undefined && 
            !(Array.isArray(value) && value.length === 0)) {
            cleanedFilters[key] = value;
        }
    }
    
    console.log('YC Email Extractor: Parsed filters from URL:');
    for (const [key, value] of Object.entries(cleanedFilters)) {
        console.log(`  ${key}: ${JSON.stringify(value)}`);
    }
    
    return cleanedFilters;
}

// Fetch companies from YC OSS API - EXACT match to Python logic
async function fetchYCCompanies(filters) {
    const apiUrl = 'https://yc-oss.github.io/api/companies/all.json';
    
    try {
        console.log('YC Email Extractor: Fetching companies from YC API...');
        
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error(`Failed to fetch companies: ${response.status}`);
        }
        
        const allCompanies = await response.json();
        console.log('YC Email Extractor: Fetched', allCompanies.length, 'total companies from YC API');
        
        // Apply filters - EXACT Python logic
        const filteredCompanies = allCompanies.filter(company => {
            // Check batch filter
            if (filters.batches && filters.batches.length > 0) {
                const companyBatch = company.batch || '';
                if (!filters.batches.some(batch => companyBatch.toLowerCase().includes(batch.toLowerCase()))) {
                    return false;
                }
            }
            
            // Check industry filter
            if (filters.industries && filters.industries.length > 0) {
                const companyIndustry = company.industry || '';
                const companyIndustries = company.industries || [];
                
                // Check both industry field and industries array
                const industryMatch = filters.industries.some(filterIndustry => {
                    const filterLower = filterIndustry.toLowerCase();
                    return companyIndustry.toLowerCase().includes(filterLower) ||
                           companyIndustries.some(ind => ind.toLowerCase().includes(filterLower));
                });
                
                if (!industryMatch) {
                    return false;
                }
            }
            
            // Check region filter (improved logic)
            if (filters.regions && filters.regions.length > 0) {
                const companyRegions = company.regions || [];
                const companyLocations = company.all_locations || '';
                
                // Check if company regions match any filter regions
                let regionMatch = companyRegions.some(compRegion => 
                    filters.regions.some(filterRegion => 
                        compRegion.toLowerCase().includes(filterRegion.toLowerCase()) ||
                        filterRegion.toLowerCase().includes(compRegion.toLowerCase())
                    )
                );
                
                // Also check locations string if no region match
                if (!regionMatch) {
                    regionMatch = filters.regions.some(filterRegion => 
                        companyLocations.toLowerCase().includes(filterRegion.toLowerCase())
                    );
                }
                
                if (!regionMatch) {
                    return false;
                }
            }
            
            // Check status filter
            if (filters.statuses && filters.statuses.length > 0) {
                const companyStatus = company.status || '';
                if (!filters.statuses.some(status => companyStatus.toLowerCase().includes(status.toLowerCase()))) {
                    return false;
                }
            }
            
            // Check tags filter
            if (filters.tags && filters.tags.length > 0) {
                const companyTags = company.tags || [];
                const companyTagsHighlighted = company.tags_highlighted || [];
                const allTags = [...companyTags, ...companyTagsHighlighted];
                
                const tagMatch = filters.tags.some(filterTag =>
                    allTags.some(tag => tag.toLowerCase().includes(filterTag.toLowerCase()))
                );
                
                if (!tagMatch) {
                    return false;
                }
            }
            
            // Check stages filter
            if (filters.stages && filters.stages.length > 0) {
                const companyStage = company.stage || '';
                if (!filters.stages.some(stage => companyStage.toLowerCase().includes(stage.toLowerCase()))) {
                    return false;
                }
            }
            
            // Check team_size filter
            if (filters.team_sizes && filters.team_sizes.length > 0) {
                const companyTeamSize = company.team_size;
                if (companyTeamSize === null || companyTeamSize === undefined) {
                    return false;
                }
                
                // Handle team size ranges like ["5", "1,000+"]
                const sizeMatch = filters.team_sizes.some(sizeFilter => {
                    if (sizeFilter.includes('+')) {
                        // Handle "1,000+" format
                        const minSize = parseInt(sizeFilter.replace(/[,+]/g, ''));
                        return companyTeamSize >= minSize;
                    } else if (sizeFilter.includes('-')) {
                        // Handle "5-50" format
                        const [min, max] = sizeFilter.split('-').map(s => parseInt(s.replace(/,/g, '')));
                        return companyTeamSize >= min && companyTeamSize <= max;
                    } else {
                        // Exact match
                        return companyTeamSize === parseInt(sizeFilter.replace(/,/g, ''));
                    }
                });
                
                if (!sizeMatch) {
                    return false;
                }
            }
            
            // Check boolean filters
            if (filters.top_company !== undefined && company.top_company !== filters.top_company) {
                return false;
            }
            
            if (filters.nonprofit !== undefined && company.nonprofit !== filters.nonprofit) {
                return false;
            }
            
            if (filters.is_hiring !== undefined && company.isHiring !== filters.is_hiring) {
                return false;
            }
            
            if (filters.app_video_public !== undefined && company.app_video_public !== filters.app_video_public) {
                return false;
            }
            
            if (filters.demo_day_video_public !== undefined && company.demo_day_video_public !== filters.demo_day_video_public) {
                return false;
            }
            
            if (filters.app_answers !== undefined) {
                const hasAppAnswers = company.app_answers !== null && company.app_answers !== undefined;
                if (hasAppAnswers !== filters.app_answers) {
                    return false;
                }
            }
            
            if (filters.question_answers !== undefined && company.question_answers !== filters.question_answers) {
                return false;
            }
            
            return true;
        });
        
        console.log('YC Email Extractor: Filtered to', filteredCompanies.length, 'companies matching criteria');
        
        // Debug: Show first few filtered companies
        if (filteredCompanies.length > 0) {
            console.log('YC Email Extractor: Sample filtered companies:');
            filteredCompanies.slice(0, 5).forEach(company => {
                console.log(`  - ${company.name} (${company.batch}) - Regions: ${JSON.stringify(company.regions)}, Location: ${company.all_locations}`);
            });
        }
        
        return filteredCompanies.map(company => ({
            name: company.name || 'Unknown',
            url: company.url || '',
            slug: company.slug || '',
            batch: company.batch || '',
            industry: company.industry || ''
        }));
        
    } catch (error) {
        console.error('YC Email Extractor: Error fetching companies:', error);
        throw new Error('Failed to fetch companies from YC API');
    }
}

// Extract emails from a single company's YC page - EXACT match to Python logic
async function extractEmailsFromCompanyPage(companyUrl) {
    if (!companyUrl) {
        return [];
    }
    
    try {
        const response = await fetch(companyUrl);
        if (!response.ok) {
            throw new Error(`Failed to fetch page: ${response.status}`);
        }
        
        const html = await response.text();
        
        // Clean HTML by removing script and style tags (matches Python BeautifulSoup logic)
        let cleanHtml = html
            .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
            .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '')
            .replace(/<nav\b[^<]*(?:(?!<\/nav>)<[^<]*)*<\/nav>/gi, '')
            .replace(/<footer\b[^<]*(?:(?!<\/footer>)<[^<]*)*<\/footer>/gi, '')
            .replace(/<header\b[^<]*(?:(?!<\/header>)<[^<]*)*<\/header>/gi, '');
        
        // Extract text content by removing all HTML tags
        let text = cleanHtml.replace(/<[^>]*>/g, ' ');
        
        // Clean up the text (matches Python logic exactly)
        const lines = text.split('\n').map(line => line.trim()).filter(line => line);
        const chunks = lines.flatMap(line => line.split(/\s{2,}/).map(chunk => chunk.trim())).filter(chunk => chunk);
        text = chunks.join(' ');
        
        // Extract emails using regex (exact Python pattern)
        const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
        const foundEmails = Array.from(new Set((text.match(emailRegex) || [])));
        
        // Filter out common non-founder emails (matches Python exclusions)
        const filteredEmails = foundEmails.filter(email => {
            const lowerEmail = email.toLowerCase();
            const excludePatterns = [
                'noreply@', 'no-reply@', 'support@ycombinator', 'jobs@ycombinator',
                'privacy@', 'legal@', 'abuse@', 'postmaster@', 'webmaster@',
                'admin@ycombinator', 'info@ycombinator'
            ];
            
            return !excludePatterns.some(pattern => lowerEmail.includes(pattern));
        });
        
        return filteredEmails;
        
    } catch (error) {
        console.error('YC Email Extractor: Error extracting emails from', companyUrl, error);
        return [];
    }
}

// Utility function for delays
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}