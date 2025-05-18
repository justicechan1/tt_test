// ✅ 수정된 maps.js
import api from './index';

export const getRoute = async (user_id, date) => {
  const res = await api.post('/api/users/maps/route', { user_id, date });
  return res.data; 
};
