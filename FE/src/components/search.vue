<template>
  <div id="pop">
    <header>
      <h3>🔎 장소를 검색해주세요</h3>
      <input
        v-model="searchQuery"
        type="text"
        placeholder="장소를 입력하세요"
        id="search_input"
      />
    </header>

    <article id="place_list">
      <ul>
        <li v-for="place in places" :key="place">{{ place }}</li>
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
  name: 'Search_',
  props: {
    days: String,
    date: String,
  },
  data() {
    return {
      searchQuery: '',
      places: [],
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
  methods: {
    async fetchPlaces(query) {
      if (!query.trim()) {
        this.places = [];
        return;
      }
      const results = await searchPlaces(query);
      this.places = results.map(p => p.name);
    }
  }
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
