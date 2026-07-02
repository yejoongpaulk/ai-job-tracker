import axios from 'axios';

const api = axios.create({
  baseURL: '',             // Vite's local proxy router now handles path extensions
  withCredentials: true,   // Forces browser cookie handshakes to process smoothly
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
