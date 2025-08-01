/**
 * Appo License System - Web Integration
 * ===================================
 * 
 * JavaScript integration for web applications using the Appo license system.
 * Handles license verification, branding checks, and feature gating.
 * 
 * Author: Appo Security Team
 * License: Proprietary - All Rights Reserved
 */

class AppoLicenseManager {
    constructor(config) {
        this.licenseServerUrl = config.licenseServerUrl || 'https://your-license-server.com';
        this.appIdentifier = config.appIdentifier;
        this.appVersion = config.appVersion || '1.0.0';
        this.licenseKey = config.licenseKey;
        this.brandingElements = config.brandingElements || [];
        
        // License verification cache
        this.verificationCache = null;
        this.cacheExpiry = null;
        this.cacheDuration = 5 * 60 * 1000; // 5 minutes
        
        // Event callbacks
        this.onLicenseValid = config.onLicenseValid || (() => {});
        this.onLicenseInvalid = config.onLicenseInvalid || (() => {});
        this.onBrandingInvalid = config.onBrandingInvalid || (() => {});
        
        this.init();
    }
    
    /**
     * Initialize the license manager
     */
    async init() {
        console.log('🔐 Initializing Appo License Manager...');
        
        // Check if license key is provided
        if (!this.licenseKey) {
            console.warn('⚠️ No license key provided - running in demo mode');
            this.handleDemoMode();
            return;
        }
        
        // Verify license on startup
        await this.verifyLicense();
        
        // Set up periodic verification (every 30 minutes)
        setInterval(() => {
            this.verifyLicense();
        }, 30 * 60 * 1000);
        
        // Check branding integrity
        this.checkBrandingIntegrity();
    }
    
    /**
     * Verify the license key with the server
     */
    async verifyLicense() {
        try {
            // Check cache first
            if (this.verificationCache && this.cacheExpiry && Date.now() < this.cacheExpiry) {
                console.log('📋 Using cached license verification');
                return this.verificationCache;
            }
            
            console.log('🔍 Verifying license key...');
            
            const brandingChecksum = await this.calculateBrandingChecksum();
            
            const response = await fetch(`${this.licenseServerUrl}/verify_key`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    license_key: this.licenseKey,
                    app_identifier: this.appIdentifier,
                    app_version: this.appVersion,
                    branding_checksum: brandingChecksum
                })
            });
            
            const result = await response.json();
            
            if (result.success && result.valid) {
                console.log('✅ License verified successfully');
                console.log(`📊 Tier: ${result.tier} (${result.tier_info.name})`);
                
                // Cache the result
                this.verificationCache = result;
                this.cacheExpiry = Date.now() + this.cacheDuration;
                
                // Check branding validity
                if (!result.branding_valid) {
                    console.warn('⚠️ Invalid branding detected');
                    this.onBrandingInvalid(result);
                    this.showBrandingWarning();
                }
                
                this.onLicenseValid(result);
                return result;
                
            } else {
                console.error('❌ License verification failed:', result.error);
                this.onLicenseInvalid(result);
                this.handleInvalidLicense(result.error);
                return null;
            }
            
        } catch (error) {
            console.error('🚨 License verification error:', error);
            this.handleVerificationError(error);
            return null;
        }
    }
    
    /**
     * Calculate checksum of branding elements for integrity verification
     */
    async calculateBrandingChecksum() {
        try {
            let brandingData = '';
            
            // Check for required branding elements
            const requiredElements = [
                { selector: '.appo-logo', attribute: 'src' },
                { selector: '.appo-branding', attribute: 'textContent' },
                { selector: '[data-appo-brand]', attribute: 'dataset.appoBrand' },
                { selector: '.footer .appo-credit', attribute: 'textContent' }
            ];
            
            for (const element of requiredElements) {
                const domElement = document.querySelector(element.selector);
                if (domElement) {
                    const value = element.attribute === 'textContent' 
                        ? domElement.textContent.trim()
                        : element.attribute.startsWith('dataset.')
                        ? domElement[element.attribute]
                        : domElement.getAttribute(element.attribute);
                    
                    brandingData += value || '';
                }
            }
            
            // Add custom branding elements
            for (const selector of this.brandingElements) {
                const element = document.querySelector(selector);
                if (element) {
                    brandingData += element.textContent.trim() || element.src || '';
                }
            }
            
            // Calculate SHA-256 hash
            const encoder = new TextEncoder();
            const data = encoder.encode(brandingData);
            const hashBuffer = await crypto.subtle.digest('SHA-256', data);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
            
            return hashHex;
            
        } catch (error) {
            console.error('Error calculating branding checksum:', error);
            return 'checksum_error';
        }
    }
    
    /**
     * Check if branding elements are present and valid
     */
    checkBrandingIntegrity() {
        const requiredBranding = [
            '.appo-logo',
            '.appo-branding',
            '[data-appo-brand]'
        ];
        
        let brandingPresent = true;
        const missingElements = [];
        
        for (const selector of requiredBranding) {
            const element = document.querySelector(selector);
            if (!element || element.style.display === 'none' || element.style.visibility === 'hidden') {
                brandingPresent = false;
                missingElements.push(selector);
            }
        }
        
        if (!brandingPresent) {
            console.warn('⚠️ Required branding elements missing:', missingElements);
            this.showBrandingWarning();
        }
        
        return brandingPresent;
    }
    
    /**
     * Check if a feature is available for the current license tier
     */
    isFeatureAvailable(feature) {
        if (!this.verificationCache || !this.verificationCache.tier_info) {
            return false; // Deny access if no valid license
        }
        
        const features = this.verificationCache.tier_info.features || [];
        return features.includes(feature) || features.includes('all_features');
    }
    
    /**
     * Get the maximum number of users allowed
     */
    getMaxUsers() {
        if (!this.verificationCache || !this.verificationCache.tier_info) {
            return 1; // Default to 1 user if no valid license
        }
        
        return this.verificationCache.tier_info.max_users;
    }
    
    /**
     * Get the daily API call limit
     */
    getDailyApiLimit() {
        if (!this.verificationCache || !this.verificationCache.tier_info) {
            return 100; // Default to 100 calls if no valid license
        }
        
        return this.verificationCache.tier_info.api_calls_per_day;
    }
    
    /**
     * Get current license tier information
     */
    getLicenseInfo() {
        return this.verificationCache;
    }
    
    /**
     * Handle demo mode (no license key provided)
     */
    handleDemoMode() {
        console.log('🆓 Running in demo mode with limited features');
        
        // Show demo mode indicator
        const demoIndicator = document.createElement('div');
        demoIndicator.innerHTML = `
            <div style="
                position: fixed; 
                top: 0; 
                left: 0; 
                right: 0; 
                background: #ff9800; 
                color: white; 
                text-align: center; 
                padding: 10px; 
                z-index: 10000;
                font-family: Arial, sans-serif;
                font-size: 14px;
            ">
                🆓 Demo Mode - <a href="#" onclick="window.open('https://appo.com/pricing', '_blank')" style="color: white; text-decoration: underline;">Upgrade to unlock all features</a>
            </div>
        `;
        document.body.appendChild(demoIndicator);
        
        // Simulate FREE tier
        this.verificationCache = {
            valid: true,
            tier: 'FREE',
            tier_info: {
                name: 'Demo',
                max_users: 1,
                features: ['basic_app'],
                api_calls_per_day: 50,
                storage_gb: 0.5
            }
        };
    }
    
    /**
     * Handle invalid license
     */
    handleInvalidLicense(error) {
        console.error('🚨 Invalid license detected:', error);
        
        // Show invalid license screen
        const invalidScreen = document.createElement('div');
        invalidScreen.innerHTML = `
            <div style="
                position: fixed; 
                top: 0; 
                left: 0; 
                right: 0; 
                bottom: 0; 
                background: rgba(0,0,0,0.9); 
                color: white; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                z-index: 20000;
                font-family: Arial, sans-serif;
            ">
                <div style="text-align: center; padding: 40px; background: #333; border-radius: 10px; max-width: 500px;">
                    <h1 style="color: #ff4444; margin-bottom: 20px;">❌ Invalid License</h1>
                    <p style="margin-bottom: 20px;">${error}</p>
                    <p>Please contact support or purchase a valid license to continue using this application.</p>
                    <div style="margin-top: 30px;">
                        <button onclick="location.reload()" style="
                            background: #007bff; 
                            color: white; 
                            border: none; 
                            padding: 10px 20px; 
                            border-radius: 5px; 
                            cursor: pointer;
                            margin-right: 10px;
                        ">Retry</button>
                        <button onclick="window.open('https://appo.com/support', '_blank')" style="
                            background: #28a745; 
                            color: white; 
                            border: none; 
                            padding: 10px 20px; 
                            border-radius: 5px; 
                            cursor: pointer;
                        ">Contact Support</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(invalidScreen);
    }
    
    /**
     * Show branding warning
     */
    showBrandingWarning() {
        // Only show if not already shown
        if (document.querySelector('.appo-branding-warning')) {
            return;
        }
        
        const warning = document.createElement('div');
        warning.className = 'appo-branding-warning';
        warning.innerHTML = `
            <div style="
                position: fixed; 
                bottom: 20px; 
                right: 20px; 
                background: #ff4444; 
                color: white; 
                padding: 15px; 
                border-radius: 5px; 
                z-index: 15000;
                font-family: Arial, sans-serif;
                font-size: 14px;
                max-width: 300px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            ">
                ⚠️ <strong>Unlicensed/Invalid Branding</strong><br>
                Required Appo branding elements are missing or modified.
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none; 
                    border: none; 
                    color: white; 
                    float: right; 
                    cursor: pointer;
                    font-size: 16px;
                ">×</button>
            </div>
        `;
        document.body.appendChild(warning);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (warning.parentElement) {
                warning.remove();
            }
        }, 10000);
    }
    
    /**
     * Handle verification errors (network issues, etc.)
     */
    handleVerificationError(error) {
        console.warn('⚠️ License verification failed due to network or server error');
        
        // In case of network errors, allow app to continue with cached license
        // but show a warning
        if (this.verificationCache) {
            console.log('📋 Using cached license data due to verification error');
            return;
        }
        
        // If no cache available, show error but allow limited functionality
        console.log('🔄 Running with limited functionality due to verification error');
        
        const errorNotice = document.createElement('div');
        errorNotice.innerHTML = `
            <div style="
                position: fixed; 
                top: 20px; 
                right: 20px; 
                background: #ff9800; 
                color: white; 
                padding: 15px; 
                border-radius: 5px; 
                z-index: 15000;
                font-family: Arial, sans-serif;
                font-size: 14px;
                max-width: 300px;
            ">
                ⚠️ Cannot verify license (network error). Running with limited features.
                <button onclick="this.parentElement.remove()" style="
                    background: none; 
                    border: none; 
                    color: white; 
                    float: right; 
                    cursor: pointer;
                ">×</button>
            </div>
        `;
        document.body.appendChild(errorNotice);
    }
}

// =============================================================================
// FEATURE GATING UTILITIES
// =============================================================================

/**
 * Feature gate decorator for functions
 */
function requireFeature(feature) {
    return function(target, propertyName, descriptor) {
        const method = descriptor.value;
        descriptor.value = function(...args) {
            if (window.appoLicense && window.appoLicense.isFeatureAvailable(feature)) {
                return method.apply(this, args);
            } else {
                console.warn(`🚫 Feature '${feature}' not available in current license tier`);
                // Show upgrade prompt
                showUpgradePrompt(feature);
                return null;
            }
        };
        return descriptor;
    };
}

/**
 * Show upgrade prompt for locked features
 */
function showUpgradePrompt(feature) {
    const prompt = document.createElement('div');
    prompt.innerHTML = `
        <div style="
            position: fixed; 
            top: 50%; 
            left: 50%; 
            transform: translate(-50%, -50%); 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            z-index: 25000;
            font-family: Arial, sans-serif;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 400px;
        ">
            <h3 style="color: #333; margin-bottom: 15px;">🔒 Premium Feature</h3>
            <p style="margin-bottom: 20px;">The feature '<strong>${feature}</strong>' requires a premium license.</p>
            <div>
                <button onclick="this.parentElement.parentElement.parentElement.remove()" style="
                    background: #6c757d; 
                    color: white; 
                    border: none; 
                    padding: 10px 20px; 
                    border-radius: 5px; 
                    cursor: pointer;
                    margin-right: 10px;
                ">Close</button>
                <button onclick="window.open('https://appo.com/pricing', '_blank')" style="
                    background: #007bff; 
                    color: white; 
                    border: none; 
                    padding: 10px 20px; 
                    border-radius: 5px; 
                    cursor: pointer;
                ">Upgrade Now</button>
            </div>
        </div>
        <div style="
            position: fixed; 
            top: 0; 
            left: 0; 
            right: 0; 
            bottom: 0; 
            background: rgba(0,0,0,0.5); 
            z-index: 24999;
        " onclick="this.nextElementSibling.querySelector('button').click()"></div>
    `;
    document.body.appendChild(prompt);
}

/**
 * Check if feature is available (utility function)
 */
window.hasFeature = function(feature) {
    return window.appoLicense ? window.appoLicense.isFeatureAvailable(feature) : false;
};

/**
 * Get current license tier (utility function)
 */
window.getLicenseTier = function() {
    return window.appoLicense ? window.appoLicense.getLicenseInfo()?.tier : 'UNKNOWN';
};

// =============================================================================
// BRANDING ENFORCEMENT
// =============================================================================

/**
 * Enforce Appo branding requirements
 */
function enforceBranding() {
    // Add required Appo branding if not present
    if (!document.querySelector('.appo-branding')) {
        const branding = document.createElement('div');
        branding.className = 'appo-branding';
        branding.innerHTML = 'Powered by <a href="https://appo.com" target="_blank">Appo</a>';
        branding.style.cssText = `
            position: fixed; 
            bottom: 10px; 
            left: 10px; 
            font-size: 12px; 
            color: #666; 
            z-index: 1000;
            font-family: Arial, sans-serif;
        `;
        document.body.appendChild(branding);
    }
    
    // Monitor for branding removal attempts
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.removedNodes.forEach(function(node) {
                    if (node.classList && node.classList.contains('appo-branding')) {
                        console.warn('⚠️ Appo branding removal detected');
                        if (window.appoLicense) {
                            window.appoLicense.showBrandingWarning();
                        }
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
}

// Initialize branding enforcement when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enforceBranding);
} else {
    enforceBranding();
}

// =============================================================================
// USAGE EXAMPLE
// =============================================================================

/*
// Initialize the license manager
window.appoLicense = new AppoLicenseManager({
    licenseServerUrl: 'https://your-license-server.com',
    appIdentifier: 'com.appo.mywebapp',
    appVersion: '1.0.0',
    licenseKey: 'APPO-XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX',
    brandingElements: ['.custom-appo-credit'],
    
    onLicenseValid: (result) => {
        console.log('License is valid:', result);
        // Enable full functionality
    },
    
    onLicenseInvalid: (result) => {
        console.log('License is invalid:', result);
        // Restrict functionality
    },
    
    onBrandingInvalid: (result) => {
        console.log('Branding validation failed');
        // Show branding warning
    }
});

// Example feature gating
function premiumFeature() {
    if (!window.hasFeature('premium_features')) {
        showUpgradePrompt('premium_features');
        return;
    }
    
    // Premium feature code here
    console.log('Premium feature activated!');
}

// Example API call with license validation
async function makeApiCall() {
    const licenseInfo = window.appoLicense?.getLicenseInfo();
    if (!licenseInfo?.valid) {
        console.error('Cannot make API call: invalid license');
        return;
    }
    
    const dailyLimit = window.appoLicense.getDailyApiLimit();
    // Check against daily limit before making call
    
    // Make API call
    const response = await fetch('/api/data', {
        headers: {
            'X-License-Key': licenseInfo.license_key,
            'X-App-Identifier': 'com.appo.mywebapp'
        }
    });
    
    return response.json();
}
*/