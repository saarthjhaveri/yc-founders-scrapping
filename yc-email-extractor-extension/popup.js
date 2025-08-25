// YC Email Extractor - Popup Script

document.addEventListener('DOMContentLoaded', function() {
    checkCurrentTab();
});

async function checkCurrentTab() {
    try {
        // Get current active tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        const statusElement = document.getElementById('status');
        const statusText = document.getElementById('status-text');
        
        if (tab && tab.url) {
            const url = new URL(tab.url);
            
            // Check if we're on YC companies page
            if (url.hostname === 'www.ycombinator.com' && url.pathname === '/companies') {
                if (url.search) {
                    // On companies page with filters
                    statusElement.className = 'status active';
                    statusText.textContent = '✅ Ready to extract emails from current page';
                } else {
                    // On companies page but no filters
                    statusElement.className = 'status inactive';
                    statusText.textContent = '⚠️ Add some filters to the companies page first';
                }
            } else {
                // Not on YC companies page
                statusElement.className = 'status inactive';
                statusText.textContent = '❌ Navigate to YC companies page to start';
            }
        } else {
            statusElement.className = 'status inactive';
            statusText.textContent = '❌ Unable to detect current page';
        }
    } catch (error) {
        console.error('Error checking current tab:', error);
        const statusElement = document.getElementById('status');
        const statusText = document.getElementById('status-text');
        statusElement.className = 'status inactive';
        statusText.textContent = '❌ Error checking page status';
    }
}
