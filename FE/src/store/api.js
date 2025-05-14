import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // 백엔드 주소에 맞게 변경
  withCredentials: false
});

export const initSchedule = async (payload) => {
  try {
    const res = await api.post('/api/users/schedules/init', payload);
    return res.data;
  } catch (error) {
    console.error('initSchedule 실패:', error.response?.data || error);
    throw error;
  }
};
