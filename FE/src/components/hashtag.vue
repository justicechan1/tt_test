<template>
  <div class="hashtag-container">
    <button
      v-for="(tag, index) in hashtags"
      :key="index"
      :class="['hashtag-button', { selected: selectedHashtag === tag.hashtag_name }]"
      @click="handleClick(tag)">
      {{ tag.hashtag_name }}
    </button>
  </div>
</template>

<script>
import { getHashtags } from '@/api/maps';

export default {
  name: 'HashtagButtons',
  props: {
    category: { type: String, required: true },
    viewport: { type: Object, required: true }
  },
  data() {
    return {
      hashtags: [],
      selectedHashtag: null
    };
  },
  mounted() {
    this.fetchHashtags();
  },
  watch: {
    category: 'fetchHashtags',
    viewport: {
      handler: 'fetchHashtags',
      deep: true
    }
  },
  methods: {
    async fetchHashtags() {
      try {
        const result = await getHashtags(this.category, this.viewport);
        this.hashtags = result.tag;
      } catch (error) {
        console.error("해시태그 불러오기 실패:", error);
      }
    },
    handleClick(tag) {
      this.selectedHashtag = this.selectedHashtag === tag.hashtag_name ? null : tag.hashtag_name;
      this.$emit("hashtag-selected", this.selectedHashtag);
    }
  }
};
</script>


<style scoped>
.button-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
  justify-content: flex-end;
}

.hashtag-button {
  background-color: white;
  color: skyblue;
  border: 2px solid skyblue;
  border-radius: 15px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.hashtag-button:hover {
  background-color: deepskyblue;
  color: white;
}

/* 선택된 상태일 때 스타일 */
.hashtag-button.selected {
  background-color: deepskyblue;
  color: white;
  border-color: deepskyblue;
}
</style>