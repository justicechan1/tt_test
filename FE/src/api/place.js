import api from './index';

export const searchPlaces = async (query) => {
  try {
    const res = await api.get('/api/places/search', {
      params: { name: query }
    });
    return res.data.search;
  } catch (error) {
    console.error('searchPlaces 실패:', error.response?.data || error);
    return [];
  }
};
