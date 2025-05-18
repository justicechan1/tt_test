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

export const getUserSchedule = async (userId) => {
  try {
    const res = await api.get('/api/users/schedules/init_show', {
      params: { user_id: userId }
    });
    return res.data;
  } catch (error) {
    console.error('getUserSchedule 실패:', error.response?.data || error);
    throw error;
  }
};