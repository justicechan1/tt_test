// ✅ 수정된 maps.js
import api from './index';

export const getRoute = async (user_id, date) => {
  const res = await api.post('/api/users/maps/route', { user_id, date });
  return res.data; 
};

export const getHashtags = async (category, viewport) => {
  try {
    const res = await api.post('/api/users/maps/hashtage', {
      category,
      viewport
    });
    return res.data;
  } catch (error) {
    console.error('❌ 해시태그 불러오기 실패:', error.response?.data || error);
    throw error;
  }
};
