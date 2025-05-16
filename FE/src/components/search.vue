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
      places: [], // ← 실제 검색 결과
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
        const results = await searchPlaces(query); // ex: [{ name, address, ... }]
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
      console.log('선택한 장소:', place.places);
      this.$emit('select-place', place.places);
    },
  },
};
</script>

<style scoped>
#pop {
  display: flex;
  flex-direction: column;
  padding: 10px;
  width: 300px;
  height: 90%;
  background-color: white;
  border: 3px solid skyblue;
  border-radius: 10px;
  position: absolute;
}

header {
  flex: 0 0 auto;
  width: 100%;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

#search_input {
  padding: 8px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 16px;
}

#place_list {
  width: 100%;
  height: 70%;
  overflow-y: auto;
}

#place_list ul {
  list-style: none;
  padding: 0;
}

#place_list li {
  padding: 8px;
  border-bottom: 1px solid #eee;
}

footer {
  flex: 0 0 auto;
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

#close_btn {
  padding: 10px;
  border-radius: 20px;
  background-color: #dce9f5;
  border: none;
  cursor: pointer;
}
</style>