import { apiClient } from './client';

export const authApi = {
  login: async (email, password) => {
    // Determine if using FormData or JSON based on backend implementation
    // Plan used JSON: {email, password} -> /auth/login
    // But router also supports /auth/token with FormData. 
    // Let's use JSON endpoint /auth/login for simplicity in React
    // apiClient.post returns the JSON data directly, not a response object wrapper
    const data = await apiClient.post('/api/auth/login', { email, password });
    return data;
  },

  signup: async (userData) => {
    // apiClient.post returns the JSON data directly
    const data = await apiClient.post('/api/auth/signup', userData);
    return data;
  },

  me: async () => {
    // apiClient.get returns the JSON data directly
    const data = await apiClient.get('/api/auth/me');
    return data;
  }
};
