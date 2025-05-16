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

export const getPlaceDetail = async (name) => {
  try {
    const res = await api.get('/api/places/data', {
      params: { name }
    });
    return res.data.places;
  } catch (error) {
    console.error('getPlaceDetail 실패:', error.response?.data || error);
    throw error;
  }
};
