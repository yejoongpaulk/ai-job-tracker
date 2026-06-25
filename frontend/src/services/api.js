import axios from 'axios';

const api = axios.create({
  baseURL: '',             // LEAVE BLANK: Vite's local proxy router now handles path extensions
  withCredentials: true,   // Crucial: Forces browser cookie handshakes to process smoothly
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
