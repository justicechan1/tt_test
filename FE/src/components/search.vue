<template>
  <div id="pop">
    <header>
      <p> 어떤 관광명소를 찾고 계시나요?</p>
      <h3>🔎장소를 검색해주세요</h3>
      <input
        v-model="searchQuery"
        type="text"
        placeholder="장소를 입력하세요"
        id="search_input"
      />
    </header>

    <article id="place_list" v-if="!selectedPlace">
      <p> ✅ 추천 장소</p>
      <ul>
        <li 
          v-for="(place, index) in filteredPlaces" 
          :key="index" 
          @click="selectPlace(place)">
          {{ place.places.name }}
        </li>
      </ul>
    </article>

    <footer>
      <button id="close_btn" @click="$emit('close')">닫기❌</button>
    </footer>
  </div>
</template>

<script>
import { searchPlaces } from '@/api/place';

export default {
  name: 'SearchPop',
  data() {
    return {
      searchQuery: '',
      places: [],
      selectedPlace: null,
      debounceTimeout: null,
    };
  },
  watch: {
    searchQuery(newQuery) {
      if (this.debounceTimeout) clearTimeout(this.debounceTimeout);
      this.debounceTimeout = setTimeout(() => {
        this.fetchPlaces(newQuery);
      }, 300);
    }
  },
  computed: {
    filteredPlaces() {
      return this.places;
    },
  },
  methods: {
    async fetchPlaces(query) {
      if (!query.trim()) {
        this.places = [];
        return;
      }
      try {
        const results = await searchPlaces(query);
        this.places = results.map(p => ({
          places: {
            name: p.name,
            address: p.address || '주소 없음',
            category: p.category || '',
            image_urls: p.image_urls || [],
          }
        }));
      } catch (error) {
        console.error('검색 API 실패:', error);
        this.places = [];
      }
    },
    selectPlace(place) {
      this.$emit('select-place', place.places);
    },
  },
};
</script>

<style scoped>
#pop {
  display: flex;
  flex-direction: column;
  margin: 10px;
  width: 300px;
  height: 90%;
  background-color: white;
  border: 3px solid skyblue;
  border-radius: 10px;
  position: absolute;
  overflow: hidden;
}

header {
  width: 100%;
  flex: 0 0 10%;
  padding: 10px;
  display: flex;
  flex-direction: column;
}

header input {
  width: 85%;
}

#search_input {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid skyblue;
  font-size: 16px;
}

#place_list {
  width: 100%;
  height: 70%;
  margin: 10px;
  overflow-y: auto;
}

#place_list ul {
  width: 85%;
  list-style: none;
  padding: 10px;
}

#place_list li {
  padding: 8px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

footer {
  flex: 0 0 10%;
  width: 100%;
  margin-right: 20px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

#close_btn {
  padding: 10px;
  background-color: white;
  border: none;
  cursor: pointer;
}
</style>
