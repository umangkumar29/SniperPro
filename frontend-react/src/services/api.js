import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_URL,
});

export const getProducts = () => api.get('/products/');
export const trackProduct = (url) => api.post('/products/track', { url });
export const refreshProduct = (id) => api.post(`/products/${id}/refresh`);
export const getPriceHistory = (id) => api.get(`/analytics/${id}/trend`);
export const getAnalysis = (id) => api.get(`/analytics/${id}/analysis`);
export const setAlert = (data) => api.post('/alerts/', data);
export const deleteProduct = (id) => api.delete(`/products/${id}`);
