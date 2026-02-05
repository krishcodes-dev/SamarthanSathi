import axios from 'axios';

// ===== AXIOS INSTANCE =====
const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
});

// ===== REQUEST INTERCEPTOR =====
apiClient.interceptors.request.use(
    (config) => {
        console.log(`🔵 ${config.method.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => {
        console.error('❌ Request error:', error);
        return Promise.reject(error);
    }
);

// ===== RESPONSE INTERCEPTOR =====
apiClient.interceptors.response.use(
    (response) => {
        console.log(`✅ ${response.config.method.toUpperCase()} ${response.config.url} → ${response.status}`);
        return response.data;  // Return only data, not full response
    },
    (error) => {
        // ===== UNIFIED ERROR HANDLING =====

        if (error.response) {
            // Server responded with error status
            const { status, data } = error.response;

            console.error(`❌ ${status} ${error.config.method.toUpperCase()} ${error.config.url}`);
            console.error('Error data:', data);

            // Format error message
            let message = data?.detail || data?.message || `Server error (${status})`;
            let details = null;

            // Handle structured error responses (e.g. validation errors)
            if (typeof message === 'object') {
                details = message;
                message = message.error || "Validation Error";
            }

            const err = new Error(message);
            err.details = details; // Attach structured details
            return Promise.reject(err);

        } else if (error.request) {
            // Request made but no response (network error, CORS, timeout)
            console.error('❌ Network error:', error.message);

            if (error.code === 'ECONNABORTED') {
                return Promise.reject(new Error('Request timeout - server is slow'));
            }

            return Promise.reject(new Error('Cannot reach server. Is the backend running?'));

        } else {
            // Something else went wrong
            console.error('❌ Unknown error:', error.message);
            return Promise.reject(new Error(error.message));
        }
    }
);

// ===== API METHODS =====

const api = {
    // Get request queue
    getQueue: async (limit = 50) => {
        return apiClient.get('/requests/queue', { params: { limit } });
    },

    // Submit new request
    submitRequest: async (raw_text) => {
        return apiClient.post('/requests/submit', { raw_text });
    },

    // Get single request with full details
    getRequest: async (id) => {
        return apiClient.get(`/requests/${id}`);
    },

    // Get resource matches for a request
    getResourceMatches: async (requestId) => {
        return apiClient.get(`/requests/${requestId}/matches`);
    },

    // Dispatch resource to request
    dispatchResource: async (requestId, resourceId, quantity) => {
        return apiClient.post(
            `/matches/${requestId}/dispatch/${resourceId}`,
            { quantity }
        );
    },

    // Health check
    healthCheck: async () => {
        // Health is at root level, not under /api/v1
        return axios.get('http://localhost:8000/health');
    }
};

export default api;
