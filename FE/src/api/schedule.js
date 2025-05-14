import api from './index';

export const initSchedule = async (payload) => {
  try {
    const res = await api.post('/api/users/schedules/init', payload);
    return res.data;
  } catch (error) {
    console.error('initSchedule 실패:', error.response?.data || error);
    throw error;
  }
};
