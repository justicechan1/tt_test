<template>
  <div id="pop">
    <header>
      <h2 id="place_name">
        <a
          :href="'https://www.instagram.com/explore/search/keyword/?q=' + encodeURIComponent(place.name)"
          target="_blank"
          id="instagram_link"
        >
          <img src="@/assets/instagram.png" alt="Instagram" id="instagram_img" />
        </a>
        {{ placeData?.name || place.name }}
      </h2>

      <p id="place_category"> {{ placeData?.category || '카테고리 없음' }} </p>
      <p id="place_address"> {{ placeData?.address || '주소 정보 없음' }} </p>
      <p id="running_time"> {{ placeData?.open_time || '-' }} ~ {{ placeData?.close_time || '-' }} </p>
    </header>

    <article id="review">
      <div class="image-slider" v-if="placeData?.image_urls?.length">
        <div class="image-container">
          <img
            v-for="(image, index) in placeData.image_urls"
            :key="index"
            :src="image"
            :alt="'Image' + (index + 1)"
            class="slider-image"
          />
        </div>
      </div>
    </article>

    <footer>
      <button id="add_place" @click="addPlace"> 추가➕ </button>
      <button id="close_btn" @click="$emit('close')"> 닫기❌ </button>
    </footer>
  </div>
</template>

<script>
import { addPlaceToSchedule, getPlaceDetail } from '@/api/place';

export default {
  name: 'PlacePop',
  props: {
    place: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      placeData: null,
      userId: localStorage.getItem('userId') ?? ''
    };
  },
  methods: {
    async addPlace() {
      const userId = 1; // 테스트 고정
      const selectedDate = localStorage.getItem("selectedDate") || "2025-05-22";
      const placeName = this.place.name;

      const inputData = {
        places_by_day: {
          [selectedDate]: [{ name: placeName }]  // ✅ PlaceNameOnly 형태
        }
      };

      try {
        await addPlaceToSchedule(userId, inputData);
        alert("✅ 일정에 추가 완료!");
        this.$emit("place-added");
      } catch (error) {
        alert(`🚫 추가 실패: ${JSON.stringify(error.response?.data?.detail)}`);
      }
    }
  },
  async mounted() {
    const res = await getPlaceDetail(this.place.name);
    this.placeData = res;
  }
};
</script>

<style scoped>
#pop {
  width: 350px;
  height: 70%;
  padding: 20px;
  background-color: white;
  border: 3px solid skyblue;
  border-radius: 10px;
  position: absolute;
}
  
header {
  flex: 0 0 20%; /* 상단 20% */
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  justify-content: center;
} 

header p{
  margin: 0;       /* 모든 자식 요소의 기본 margin 제거 */
  padding: 0;      /* 혹시 패딩 있으면 제거 */
  line-height: 1;  /* 줄 간격 조절 (필요시) */
}

header h2 {
  margin: 0;
}

article {
  flex: 1 0 auto;
  max-height: 70%;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
} 

#instagram_link {
  display: inline-block;
  cursor: pointer;
}

#instagram_img {
  width: 40px;
  height: 40px;
  margin: 0;
}

.image-slider {
  width: 100%;
  height: 100%;
  overflow-x: auto;
  display: flex;
  align-items: center;
  gap: 10px;
  scroll-behavior: smooth;
}

.image-container {
  display: flex;
  gap: 10px;
}

.slider-image {
  width: 250px; /* 이미지 고정 너비 */
  height: 450px; /* 이미지 고정 높이 */
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0; /* 이미지가 작아지지 않도록 */
}

footer {
  flex: 0 0 10%;
  display: flex;
  justify-content: space-between; /* 양쪽 끝 정렬 */
  align-items: center;
  padding: 0 10px; /* 좌우 여백 조절 */
}

#add_place,
#close_btn {
  background-color: white; /* 버튼 배경색 */
  border: none; /* 테두리 제거 */
  padding: 8px 12px; /* 패딩 추가 */
  cursor: pointer; /* 커서 변경 */
}
</style>