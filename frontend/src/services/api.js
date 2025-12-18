/**
 * Service API pour communiquer avec le backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Intercepteurs pour logging
apiClient.interceptors.request.use(
    (config) => {
        console.log('API Request:', config.method?.toUpperCase(), config.url);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

export const api = {
    // Upload
    uploadFile: async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await apiClient.post('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    // Evaluations
    getEvaluations: async (params = {}) => {
        const response = await apiClient.get('/evaluations', { params });
        return response.data;
    },

    getEvaluation: async (id) => {
        const response = await apiClient.get(`/evaluations/${id}`);
        return response.data;
    },

    // Dashboard
    getDashboardStats: async () => {
        const response = await apiClient.get('/dashboard/stats');
        return response.data;
    },

    // Themes
    getThemes: async (params = {}) => {
        const response = await apiClient.get('/themes', { params });
        return response.data;
    },

    // Clusters
    getClusters: async () => {
        const response = await apiClient.get('/clusters');
        return response.data;
    },

    // Insights
    getInsights: async (params = {}) => {
        const response = await apiClient.get('/insights', { params });
        return response.data;
    },

    generateInsights: async () => {
        const response = await apiClient.post('/analytics/generate-insights');
        return response.data;
    },

    // Analytics
    getTrends: async (params = {}) => {
        const response = await apiClient.get('/analytics/trends', { params });
        return response.data;
    },

    getCorrelations: async () => {
        const response = await apiClient.get('/analytics/correlations');
        return response.data;
    },

    compareFormations: async (formation1, formation2) => {
        const response = await apiClient.get('/analytics/compare', {
            params: { formation1, formation2 },
        });
        return response.data;
    },
};

export default api;
