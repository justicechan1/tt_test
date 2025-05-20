<template>
  <div id="pop">
    <header>
      <h2 id="place_name">
        <a
          :href="'https://www.instagram.com/explore/search/keyword/?q=' + encodeURIComponent(placeData?.name || place.name)"
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
      <button id="add_place" @click="isAddPlaceVisible = true">추가➕</button>
      <button id="close_btn" @click="$emit('close')">닫기❌</button>
    </footer>

    <!-- 중앙 팝업: AddPlace -->
    <AddPlace
      v-if="isAddPlaceVisible"
      class="add-place-popup"
      @close="isAddPlaceVisible = false"
      @day-confirmed="addPlace"
    />
  </div>
</template>

<script>
import { addPlaceToSchedule, getPlaceDetail } from '@/api/place';
import { useDataStore } from '@/store/data';
import AddPlace from './addPlace.vue';

export default {
  name: 'PlacePop',
  components: { AddPlace },
  props: {
    place: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      placeData: null,
      isAddPlaceVisible: false,
      userId: localStorage.getItem('userId') ?? '1'
    };
  },
  computed: {
    startDay() {
      const data = useDataStore();
      return data.startDate;
    }
  },
  methods: {
    async addPlace(day) {
      try {
        const startDate = new Date(this.startDay);
        startDate.setDate(startDate.getDate() + (day - 1));
        const formattedDate = startDate.toISOString().split('T')[0];

        const inputData = {
          places_by_day: {
            [formattedDate]: [{ name: this.place.name }]
          }
        };

        await addPlaceToSchedule(this.userId, inputData);
        alert("✅ 일정에 추가 완료!");
        this.isAddPlaceVisible = false;
        this.$emit("place-added");
      } catch (error) {
        alert(`🚫 추가 실패: ${JSON.stringify(error.response?.data?.detail || error)}`);
      }
    }
  },
  async mounted() {
    try {
      const res = await getPlaceDetail(this.place.name);
      this.placeData = res;
    } catch (e) {
      console.warn("장소 상세정보 불러오기 실패", e);
      this.placeData = { name: this.place.name };
    }
  }
};
</script>

<style scoped>
#pop {
  position: relative;
  width: 350px;
  height: 70%;
  padding: 20px;
  background-color: white;
  border: 3px solid skyblue;
  border-radius: 10px;
  z-index: 1000;
}

.add-place-popup {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1100;
}

header {
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

header h2 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

#place_category {
  font-size: 0.9rem;
  color: white;
  background-color: skyblue;
  padding: 2px 8px;
  border-radius: 6px;
  align-self: flex-start;
  margin-top: 4px;
}

header p {
  margin: 0;
  padding: 0;
  line-height: 1.3;
}

#instagram_link {
  display: inline-block;
  cursor: pointer;
}

#instagram_img {
  width: 24px;
  height: 24px;
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
  width: 250px;
  height: 450px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}

footer {
  flex: 0 0 10%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 10px;
}

#add_place,
#close_btn {
  background-color: white;
  border: none;
  padding: 8px 12px;
  cursor: pointer;
}
</style>
