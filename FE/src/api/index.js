import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // 백엔드 주소에 맞게 수정
  withCredentials: false
});

export default api;
