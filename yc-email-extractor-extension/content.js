// YC Email Extractor - Content Script
// Runs on YC companies pages and injects the extraction UI

console.log('YC Email Extractor: Content script loaded');

// Check if we're on a YC companies page with filters
function isYCCompaniesPage() {
    return window.location.pathname === '/companies' && window.location.search.length > 0;
}

// Create and inject the "Generate Emails" button
function createExtractButton() {
    // Check if button already exists
    if (document.getElementById('yc-email-extractor-btn')) {
        return;
    }

    const button = document.createElement('button');
    button.id = 'yc-email-extractor-btn';
    button.className = 'yc-extract-btn';
    button.innerHTML = '📧 Generate Emails';
    button.title = 'Extract founder emails from current YC companies list';
    
    // Position the button
    button.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        padding: 12px 20px;
        background: linear-gradient(135deg, #ff6b35, #f7931e);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
        transition: all 0.3s ease;
    `;
    
    // Add hover effect
    button.addEventListener('mouseenter', () => {
        button.style.transform = 'translateY(-2px)';
        button.style.boxShadow = '0 6px 20px rgba(255, 107, 53, 0.4)';
    });
    
    button.addEventListener('mouseleave', () => {
        button.style.transform = 'translateY(0)';
        button.style.boxShadow = '0 4px 12px rgba(255, 107, 53, 0.3)';
    });
    
    // Add click handler
    button.addEventListener('click', handleExtractEmails);
    
    // Inject into page
    document.body.appendChild(button);
    console.log('YC Email Extractor: Button injected');
}

// Handle the email extraction process
async function handleExtractEmails() {
    const button = document.getElementById('yc-email-extractor-btn');
    const originalText = button.innerHTML;
    
    try {
        // Show loading state
        button.innerHTML = '⏳ Extracting...';
        button.disabled = true;
        
        // Get current URL
        const currentUrl = window.location.href;
        console.log('YC Email Extractor: Starting extraction for URL:', currentUrl);
        
        // Send message to background script to start extraction
        const response = await chrome.runtime.sendMessage({
            action: 'extractEmails',
            url: currentUrl
        });
        
        if (response.success) {
            showResults(response.data);
        } else {
            showError(response.error || 'Unknown error occurred');
        }
        
    } catch (error) {
        console.error('YC Email Extractor: Error:', error);
        showError('Failed to extract emails. Please try again.');
    } finally {
        // Reset button
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Show results in a modal
function showResults(results) {
    // Remove existing modal if any
    const existingModal = document.getElementById('yc-email-results-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Create modal
    const modal = document.createElement('div');
    modal.id = 'yc-email-results-modal';
    modal.className = 'yc-modal';
    
    // Create results content
    let resultsHtml = '';
    let emailCount = 0;
    
    if (results.length === 0) {
        resultsHtml = '<div class="yc-no-results">No companies found matching the current filters.</div>';
    } else {
        results.forEach(company => {
            if (company.emails && company.emails.length > 0) {
                emailCount++;
                const emailsList = company.emails.join(', ');
                resultsHtml += `
                    <div class="yc-result-item">
                        <strong>${company.name}</strong> - ${emailsList}
                    </div>
                `;
            }
        });
        
        if (emailCount === 0) {
            resultsHtml = '<div class="yc-no-results">No emails found for the companies in this list.</div>';
        }
    }
    
    modal.innerHTML = `
        <div class="yc-modal-content">
            <div class="yc-modal-header">
                <h3>📧 YC Founder Emails</h3>
                <span class="yc-modal-close">&times;</span>
            </div>
            <div class="yc-modal-body">
                <div class="yc-results-summary">
                    Found ${emailCount} companies with emails out of ${results.length} total companies
                </div>
                <div class="yc-results-list">
                    ${resultsHtml}
                </div>
            </div>
            <div class="yc-modal-footer">
                <button class="yc-copy-btn" onclick="copyResults()">📋 Copy All</button>
                <button class="yc-close-btn" onclick="closeModal()">Close</button>
            </div>
        </div>
    `;
    
    // Add event listeners
    modal.querySelector('.yc-modal-close').addEventListener('click', closeModal);
    modal.querySelector('.yc-close-btn').addEventListener('click', closeModal);
    modal.querySelector('.yc-copy-btn').addEventListener('click', () => copyResults(results));
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    document.body.appendChild(modal);
    
    // Show modal with animation
    setTimeout(() => {
        modal.classList.add('yc-modal-show');
    }, 10);
}

// Show error message
function showError(message) {
    // Simple alert for now - could be enhanced with custom modal
    alert('YC Email Extractor Error: ' + message);
}

// Copy results to clipboard
function copyResults(results) {
    const emailResults = results
        .filter(company => company.emails && company.emails.length > 0)
        .map(company => `${company.name} - ${company.emails.join(', ')}`)
        .join('\n');
    
    if (emailResults) {
        navigator.clipboard.writeText(emailResults).then(() => {
            // Show success feedback
            const copyBtn = document.querySelector('.yc-copy-btn');
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '✅ Copied!';
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
            }, 2000);
        }).catch(() => {
            alert('Failed to copy to clipboard');
        });
    }
}

// Close modal
function closeModal() {
    const modal = document.getElementById('yc-email-results-modal');
    if (modal) {
        modal.classList.remove('yc-modal-show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}

// Make functions global for onclick handlers
window.copyResults = copyResults;
window.closeModal = closeModal;

// Initialize when page loads
function init() {
    if (isYCCompaniesPage()) {
        console.log('YC Email Extractor: YC companies page detected');
        createExtractButton();
    }
}

// Run on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Also run on URL changes (for SPA navigation)
let currentUrl = window.location.href;
const observer = new MutationObserver(() => {
    if (window.location.href !== currentUrl) {
        currentUrl = window.location.href;
        console.log('YC Email Extractor: URL changed to', currentUrl);
        
        // Remove existing button
        const existingButton = document.getElementById('yc-email-extractor-btn');
        if (existingButton) {
            existingButton.remove();
        }
        
        // Re-initialize if still on companies page
        setTimeout(init, 1000); // Small delay for page to load
    }
});

observer.observe(document.body, { childList: true, subtree: true });
