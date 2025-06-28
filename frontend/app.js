// IG Shop Agent Frontend
const API_BASE = 'https://igshop-dev-functions-v2.azurewebsites.net';
const INSTAGRAM_APP_ID = 'YOUR_INSTAGRAM_APP_ID'; // Will be configured from backend
const REDIRECT_URI = `${window.location.origin}/oauth-callback.html`;

class IGShopAgent {
    constructor() {
        this.isConnected = false;
        this.accessToken = null;
        this.pageInfo = null;
        this.init();
    }

    async init() {
        // Check existing connection
        await this.checkConnection();
        
        // Load dashboard data
        await this.loadDashboard();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Start polling for new messages
        this.startMessagePolling();
    }

    setupEventListeners() {
        // Instagram connect button
        document.getElementById('connect-instagram-btn').addEventListener('click', () => {
            this.connectToInstagram();
        });

        // Disconnect button
        document.getElementById('disconnect-btn').addEventListener('click', () => {
            this.disconnect();
        });

        // Test message button
        document.getElementById('send-test-btn').addEventListener('click', () => {
            this.sendTestMessage();
        });

        // Test message input (Enter key)
        document.getElementById('test-message').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendTestMessage();
            }
        });
    }

    async connectToInstagram() {
        try {
            // First, get the Instagram app configuration from backend
            const config = await this.apiCall('/api/instagram/config');
            
            if (!config.app_id) {
                throw new Error('Instagram app not configured in backend');
            }

            // Build Instagram OAuth URL
            const oauthUrl = new URL('https://api.instagram.com/oauth/authorize');
            oauthUrl.searchParams.set('client_id', config.app_id);
            oauthUrl.searchParams.set('redirect_uri', REDIRECT_URI);
            oauthUrl.searchParams.set('scope', 'user_profile,user_media,instagram_basic,instagram_manage_messages');
            oauthUrl.searchParams.set('response_type', 'code');
            oauthUrl.searchParams.set('state', this.generateState());

            // Open OAuth popup
            const popup = window.open(
                oauthUrl.toString(),
                'instagram-oauth',
                'width=500,height=600,scrollbars=yes,resizable=yes'
            );

            // Listen for OAuth callback
            this.waitForOAuthCallback(popup);

        } catch (error) {
            console.error('Instagram connection error:', error);
            this.showError('Failed to connect to Instagram: ' + error.message);
        }
    }

    waitForOAuthCallback(popup) {
        const checkClosed = setInterval(() => {
            if (popup.closed) {
                clearInterval(checkClosed);
                this.checkConnection(); // Refresh connection status
            }
        }, 1000);

        // Listen for message from popup
        window.addEventListener('message', (event) => {
            if (event.origin !== window.location.origin) return;
            
            if (event.data.type === 'INSTAGRAM_OAUTH_SUCCESS') {
                clearInterval(checkClosed);
                popup.close();
                this.handleOAuthSuccess(event.data.code, event.data.state);
            } else if (event.data.type === 'INSTAGRAM_OAUTH_ERROR') {
                clearInterval(checkClosed);
                popup.close();
                this.showError('Instagram OAuth failed: ' + event.data.error);
            }
        }, { once: true });
    }

    async handleOAuthSuccess(code, state) {
        try {
            // Exchange code for token via backend
            const result = await this.apiCall('/api/instagram/oauth/callback', {
                method: 'POST',
                body: JSON.stringify({ code, state, redirect_uri: REDIRECT_URI })
            });

            if (result.success) {
                this.accessToken = result.access_token;
                this.pageInfo = result.page_info;
                await this.updateConnectionStatus(true);
                this.showSuccess('Instagram connected successfully!');
            } else {
                throw new Error(result.error || 'OAuth exchange failed');
            }
        } catch (error) {
            console.error('OAuth callback error:', error);
            this.showError('Failed to complete Instagram connection: ' + error.message);
        }
    }

    async checkConnection() {
        try {
            const status = await this.apiCall('/api/instagram/status');
            if (status.connected) {
                this.isConnected = true;
                this.accessToken = status.access_token;
                this.pageInfo = status.page_info;
                await this.updateConnectionStatus(true);
            } else {
                await this.updateConnectionStatus(false);
            }
        } catch (error) {
            console.error('Check connection error:', error);
            await this.updateConnectionStatus(false);
        }
    }

    async updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        const connectSection = document.getElementById('connect-section');
        const connectedSection = document.getElementById('connected-section');

        if (connected && this.pageInfo) {
            // Show connected state
            statusIndicator.className = 'w-3 h-3 bg-green-500 rounded-full';
            statusText.textContent = 'Connected';
            connectSection.classList.add('hidden');
            connectedSection.classList.remove('hidden');
            
            // Update page info
            document.getElementById('page-name').textContent = this.pageInfo.name || 'Instagram Page';
            document.getElementById('page-followers').textContent = 
                this.pageInfo.followers_count ? 
                this.formatNumber(this.pageInfo.followers_count) : 'N/A';
        } else {
            // Show disconnected state
            statusIndicator.className = 'w-3 h-3 bg-red-500 rounded-full';
            statusText.textContent = 'Not Connected';
            connectSection.classList.remove('hidden');
            connectedSection.classList.add('hidden');
        }
    }

    async disconnect() {
        try {
            await this.apiCall('/api/instagram/disconnect', { method: 'POST' });
            this.isConnected = false;
            this.accessToken = null;
            this.pageInfo = null;
            await this.updateConnectionStatus(false);
            this.showSuccess('Instagram disconnected successfully');
        } catch (error) {
            console.error('Disconnect error:', error);
            this.showError('Failed to disconnect: ' + error.message);
        }
    }

    async loadDashboard() {
        try {
            // Load product count
            const catalog = await this.apiCall('/api/catalog');
            document.getElementById('product-count').textContent = 
                `${catalog.products?.length || 0} products`;

            // Load products in management section
            this.loadProducts(catalog.products || []);

            // Load analytics
            await this.loadAnalytics();

        } catch (error) {
            console.error('Dashboard load error:', error);
        }
    }

    loadProducts(products) {
        const productList = document.getElementById('product-list');
        if (products.length === 0) {
            productList.innerHTML = '<p class="text-gray-500 text-sm">No products yet</p>';
            return;
        }

        productList.innerHTML = products.map(product => `
            <div class="flex justify-between items-center p-2 bg-gray-50 rounded">
                <div>
                    <div class="font-semibold text-sm">${product.name}</div>
                    <div class="text-gray-500 text-xs">${product.price} ${product.currency}</div>
                </div>
                <div class="text-xs ${product.in_stock ? 'text-green-600' : 'text-red-600'}">
                    ${product.in_stock ? 'In Stock' : 'Out of Stock'}
                </div>
            </div>
        `).join('');
    }

    async loadAnalytics() {
        try {
            const analytics = await this.apiCall('/api/analytics');
            
            document.getElementById('total-messages').textContent = analytics.total_messages || 0;
            document.getElementById('total-orders').textContent = analytics.total_orders || 0;
            document.getElementById('response-rate').textContent = 
                `${analytics.response_rate || 0}%`;
            document.getElementById('conversion-rate').textContent = 
                `${analytics.conversion_rate || 0}%`;
        } catch (error) {
            console.error('Analytics load error:', error);
        }
    }

    async sendTestMessage() {
        const messageInput = document.getElementById('test-message');
        const message = messageInput.value.trim();
        
        if (!message) {
            this.showError('Please enter a test message');
            return;
        }

        try {
            const response = await this.apiCall('/api/ai/test-response', {
                method: 'POST',
                body: JSON.stringify({ message })
            });

            // Show response
            const responseDiv = document.getElementById('test-response');
            const responseContent = document.getElementById('response-content');
            
            responseContent.innerHTML = `
                <div class="mb-2">
                    <strong>Customer:</strong> ${message}
                </div>
                <div>
                    <strong>AI Agent:</strong> ${response.ai_response}
                </div>
                ${response.detected_intent ? `
                    <div class="mt-2 text-sm text-gray-500">
                        Detected Intent: ${response.detected_intent}
                    </div>
                ` : ''}
            `;
            
            responseDiv.classList.remove('hidden');
            messageInput.value = '';

        } catch (error) {
            console.error('Test message error:', error);
            this.showError('Failed to get AI response: ' + error.message);
        }
    }

    async startMessagePolling() {
        // Poll for new messages every 10 seconds
        setInterval(async () => {
            if (this.isConnected) {
                await this.loadRecentMessages();
            }
        }, 10000);
    }

    async loadRecentMessages() {
        try {
            const messages = await this.apiCall('/api/messages/recent');
            this.updateRecentMessages(messages.messages || []);
        } catch (error) {
            console.error('Recent messages error:', error);
        }
    }

    updateRecentMessages(messages) {
        const messagesDiv = document.getElementById('recent-messages');
        
        if (messages.length === 0) {
            messagesDiv.innerHTML = `
                <div class="text-gray-500 text-center py-4">
                    <i class="fas fa-inbox text-3xl mb-2"></i>
                    <p>No messages yet</p>
                    <p class="text-sm">Messages will appear here when customers contact you</p>
                </div>
            `;
            return;
        }

        messagesDiv.innerHTML = messages.slice(0, 5).map(msg => `
            <div class="border-l-4 border-blue-500 pl-3 py-2">
                <div class="flex justify-between items-start">
                    <div class="font-semibold text-sm text-gray-700">
                        ${msg.customer_name || 'Customer'}
                    </div>
                    <div class="text-xs text-gray-400">
                        ${this.formatTime(msg.timestamp)}
                    </div>
                </div>
                <div class="text-sm text-gray-600 mt-1">
                    ${msg.message.substring(0, 100)}${msg.message.length > 100 ? '...' : ''}
                </div>
                ${msg.ai_response ? `
                    <div class="text-xs text-green-600 mt-1">
                        ✓ AI responded
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    // Utility methods
    async apiCall(endpoint, options = {}) {
        const url = API_BASE + endpoint;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (!response.ok) {
            throw new Error(`API call failed: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }

    generateState() {
        return Math.random().toString(36).substring(2, 15) + 
               Math.random().toString(36).substring(2, 15);
    }

    formatNumber(num) {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
        return date.toLocaleDateString();
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `
            fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-sm
            ${type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}
        `;
        notification.innerHTML = `
            <div class="flex items-center space-x-2">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new IGShopAgent();
}); 