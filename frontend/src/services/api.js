import axios from 'axios';

const API = axios.create({
  baseURL: '/api',
});

API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 422) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  signup: (data) => API.post('/auth/signup', data),
  login: (data) => API.post('/auth/login', data),
  getProfile: () => API.get('/auth/me'),
};

export const uploadAPI = {
  local: (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    return API.post('/upload/local', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 600000,
      onUploadProgress: onProgress,
    });
  },
  url: (url) => API.post('/upload/url', { url }, { timeout: 600000 }),
  drive: (url) => API.post('/upload/drive', { url }, { timeout: 600000 }),
  analyzeLink: (url) => API.post('/upload/analyze-link', { url }, { timeout: 60000 }),
};

export const reportAPI = {
  getHistory: () => API.get('/reports/'),
  getReport: (id) => API.get(`/reports/${id}`),
  deleteReport: (id) => API.delete(`/reports/${id}`),
  getStats: () => API.get('/reports/stats'),
};

export default API;
