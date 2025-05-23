<template>
  <div id="map_page">
    <nav id="side">
      <ul class="nav_list">
        <li style="background-color: skyblue; border-color: skyblue;"><h1> ✈️ </h1></li>
        <li id="side_btn"><button @click="search_Popup"><p> 🔍 </p></button></li>
        <li id="side_btn"><button @click="calendar_Popup"><span> 📆 </span></button></li>
        <li id="side_btn"><button @click="save_Popup"><span> 💾 </span></button></li>
        <li id="side_btn"><button @click="place_Popup"><span> ❓ </span></button></li>
      </ul>
    </nav>

    <div id="map" style="width: 100%; height: 100%;"></div>

    <transition name="slide-popup">
      <CalPop
        v-if="isCalendarPopupVisible"
        class="popup-panel"
        @close="calendar_Popup"
        @select-day="handleSelectDay"
        @loading="handleRouteLoading"
        @select-place="handleSelectPlace"
        @open-remove-place="handleOpenRemovePopup"
      />
    </transition>
    <transition name="slide-popup">
      <SearchPop v-if="isSearchPopupVisible" class="popup-panel" @close="search_Popup" @select-place="handleSelectPlace" />
    </transition>
    <transition name="slide-popup">
      <SavePop v-if="isSavePopupVisible" class="popup-panel" @close="save_Popup" />
    </transition>

    <PlacePop 
      ref="placePopup"
      v-if="isPlacePopupVisible" 
      :key="selectedPlace?.name"
      :place="selectedPlace"
      :style="popupStyle"
      @close="handleClosePlace"
      @place-added="refreshCalendar"
    />

    <RemovePlace
      v-if="isRemovePopupVisible"
      :date-list="removeDateList"
      :visits-by-date="removeVisitsByDate"
      class="remove-popup"
      @close="isRemovePopupVisible = false"
      @refresh="refreshCalendar"
    />

    <div id="category_btn">
      <button class="category-button" @click="() => openHashtag('관광명소')">관광명소</button>
      <button class="category-button" @click="() => openHashtag('카페')">카페</button>
      <button class="category-button" @click="() => openHashtag('음식점')">음식점</button>
      <button class="category-button" @click="() => openHashtag('숙소')">숙소</button>
    </div>

    <HashtagButton
      v-if="showHashtag"
      class="hashtag-container"
      :category="selectedCategory"
      :viewport="currentViewport"
      :key="selectedCategory + '-' + JSON.stringify(currentViewport)"
      @hashtag-selected="onHashtagSelected"
    />

    <div v-if="isLoadingRoute" class="loading-overlay">
      <div class="spinner"></div>
      <p>경로 최적화 중...</p>
    </div>
  </div>
</template>

<script>
import CalPop from '@/components/calender.vue';
import SearchPop from '@/components/search.vue';
import SavePop from '@/components/save_file.vue';
import PlacePop from '@/components/place.vue';
import HashtagButton from '@/components/hashtag.vue';
import RemovePlace from '@/components/removePlace.vue';

export default {
  name: 'MainPage',
  components: { CalPop, SearchPop, SavePop, PlacePop, HashtagButton, RemovePlace },
  data() {
    return {
      selectedPlace: null,
      selectedMarker: null,
      isCalendarPopupVisible: false,
      isSearchPopupVisible: false,
      isSavePopupVisible: false,
      isPlacePopupVisible: false,
      isLoadingRoute: false,
      isRemovePopupVisible: false,
      removeVisitsByDate: {},
      removeDateList: [],
      RemovePlaceStyle: {},
      popupStyle: {},
      markers: [],
      polyline: [],
      map: null,
      showHashtag: false,
      selectedCategory: null,
      currentViewport: null
    };
  },
  methods: {
    closePopups() {
      this.isCalendarPopupVisible = false;
      this.isSearchPopupVisible = false;
      this.isSavePopupVisible = false;
      this.isPlacePopupVisible = false;
      this.isRemovePopupVisible = false;
    },
    calendar_Popup() { this.togglePopup('isCalendarPopupVisible'); },
    search_Popup() { this.togglePopup('isSearchPopupVisible'); },
    save_Popup() { this.togglePopup('isSavePopupVisible'); },
    place_Popup() { this.togglePopup('isPlacePopupVisible'); },
    togglePopup(popupName) {
      if (this[popupName]) this.closePopups();
      else {
        this.closePopups();
        this[popupName] = true;
        this.popupStyle = { position: 'absolute', top: '20px', left: '110px', zIndex: 1000 };
      }
    },
    handleSelectPlace(place) {
      this.selectedPlace = place;
      this.isPlacePopupVisible = true;
      this.popupStyle = { position: 'absolute', top: '30px', left: '420px', zIndex: 1000 };
      if (this.selectedMarker) this.selectedMarker.setMap(null);

      setTimeout(() => {
        const placeData = this.$refs.placePopup?.placeData;
        if (placeData?.x_cord && placeData?.y_cord && this.map) {
          const latLng = new window.naver.maps.LatLng(placeData.y_cord, placeData.x_cord);
          this.selectedMarker = new window.naver.maps.Marker({
            position: latLng,
            map: this.map,
            icon: {
              content: '<div style="background:tomato;color:white;padding:5px 10px;border-radius:8px;">📍</div>',
              anchor: new window.naver.maps.Point(12, 35)
            }
          });
        }
      }, 300);
    },
    handleClosePlace() {
      this.selectedPlace = null;
      this.isPlacePopupVisible = false;
      if (this.selectedMarker) {
        this.selectedMarker.setMap(null);
        this.selectedMarker = null;
      }
    },
    refreshCalendar() {
      if (this.isCalendarPopupVisible && this.$refs.calendarRef) {
        this.$refs.calendarRef.SelectedDay();
      }
    },
    handleOpenRemovePopup(date, visits) {
      this.removeDateList = [date]; // 선택된 날짜만 전달
      this.removeVisitsByDate = { [date]: visits }; // 해당 날짜의 장소들만 전달
      this.isRemovePopupVisible = true;
    },
    createNumberMarkerIcon(number) {
      const svg = `
        <svg width="40" height="40" xmlns="http://www.w3.org/2000/svg">
          <circle cx="20" cy="20" r="18" fill="skyblue" />
          <text x="20" y="26" font-size="18" font-family="Arial" fill="white" font-weight="bold" text-anchor="middle">${number}</text>
        </svg>
      `;
      return 'data:image/svg+xml;base64,' + btoa(svg);
    },
    handleSelectDay({ coordinates, path }) {
      this.isLoadingRoute = true;
      this.markers.forEach(marker => marker.setMap(null));
      this.markers = [];

      if (this.polyline) this.polyline.forEach(line => line.setMap(null));
      this.polyline = [];

      coordinates.forEach(({ x, y }, index) => {
        const marker = new window.naver.maps.Marker({
          position: new window.naver.maps.LatLng(y, x),
          map: this.map,
          icon: {
            url: this.createNumberMarkerIcon(index + 1),
            size: new window.naver.maps.Size(40, 40),
            anchor: new window.naver.maps.Point(20, 20)
          }
        });
        this.markers.push(marker);
      });

      let filteredPath = path;
      if (path.length > 1) {
        const [x1, y1] = path[0][0];
        const [xLast, yLast] = path[path.length - 1][1];
        if (x1 === xLast && y1 === yLast) filteredPath = path.slice(0, -1);
      }

      filteredPath.forEach(segment => {
        const latLngs = segment.map(([x, y]) => new window.naver.maps.LatLng(y, x));
        const line = new window.naver.maps.Polyline({
          map: this.map,
          path: latLngs,
          strokeColor: 'skyblue',
          strokeOpacity: 0.8,
          strokeWeight: 2
        });
        this.polyline.push(line);
      });
    },
    handleRouteLoading(isLoading) {
      this.isLoadingRoute = isLoading;
    },
    openHashtag(label) {
      const categoryMap = {
        '관광명소': 'tourism',
        '카페': 'cafe',
        '음식점': 'restaurant',
        '숙소': 'hotel'
      };
      const selectedCategory = categoryMap[label];
      if (!this.map || !selectedCategory) return;

      const bounds = this.map.getBounds();
      this.selectedCategory = selectedCategory;
      this.currentViewport = {
        min_x: bounds.getSW().lng(),
        min_y: bounds.getSW().lat(),
        max_x: bounds.getNE().lng(),
        max_y: bounds.getNE().lat()
      };
      this.showHashtag = true;
    }
  },
  watch: {
    isPlacePopupVisible(newVal) {
      if (!newVal && this.selectedMarker) {
        this.selectedMarker.setMap(null);
        this.selectedMarker = null;
      }
    }
  },
  mounted() {
    const script = document.createElement("script");
    script.src = "https://openapi.map.naver.com/openapi/v3/maps.js?ncpKeyId=f0u1dydazz";
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
    script.onload = () => {
      this.map = new window.naver.maps.Map("map", {
        center: new window.naver.maps.LatLng(33.4, 126.55),
        zoom: 11
      });
    };
  }
};
</script>


<style>
body {
  display: flex;
  margin: 0;
  height: 100vh; /* 전체 높이 설정 */
  font-family: 'Pretendard SemiBold', sans-serif
}

#map_page {
  display: flex;
  width: 100%; /* 전체 너비 설정 */
  height: 100%;
}

#side {
  width: 80px;
  background-color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  border: 3px solid skyblue;
}

#side_btn:focus {
  background-color:rgb(10, 124, 173);
}

.nav_list {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.nav_list li {
  width: 80px;
  height: 80px;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  font-size: 30px;
}

.nav_list li button {
  width: 100%;
  height: 100%;
  border: none;
  background: none;
  font-size: inherit;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}

#category_btn {
  position: absolute; /* 절대 위치로 설정 */
  top: 20px; /* 상단에서의 위치 */
  right: 20px; /* 오른쪽에서의 위치 */
  display: flex; /* Flexbox 사용 */
  flex-direction: row; /* 수평 정렬 */
  gap: 10px; /* 버튼 간의 간격 */
}

.category-button {
  width: 80px; /* 너비 (원 크기) */
  height: 80px; /* 높이 (원 크기) */
  padding: 0; /* 패딩 제거 */
  background-color: rgba(73, 210, 255, 0.5); /* 배경색 */
  color: white; /* 글자색 */
  border: 2px solid white; /* 테두리 제거 */
  border-radius: 50%; /* 동그라미 모양 */
  cursor: pointer; /* 커서 변경 */
  display: flex; /* 내용 가운데 정렬 */
  align-items: center;
  justify-content: center;
  font-size: 16px; /* 글자 크기 */
  transition: background-color 0.2s ease;
}

.category-button:hover {
  background-color: deepskyblue; /* 호버 시 색상 변경 */
}

.hashtag-container {
  position: absolute;
  top: 120px;
  right: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  width: 250px;
  height: 250px;
  background-color: none;
  border-radius: 5px;
  overflow-y: auto;
  scrollbar-width: none;
  z-index: 300;
}

.popup-panel {
  position: absolute;
  top: 20px;
  left: 90px; /* 사이드바 바로 옆 */
  z-index: 1000;
  overflow: visible; 
}

/* transition 효과 */
.slide-popup-enter-active,
.slide-popup-leave-active {
  transition: all 0.3s ease;
}

.slide-popup-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}
.slide-popup-enter-to {
  opacity: 1;
  transform: translateX(0);
}

.slide-popup-leave-from {
  opacity: 1;
  transform: translateX(0);
}
.slide-popup-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/*로딩 부분*/
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(255, 255, 255, 0.6);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.spinner {
  border: 6px solid #eee;
  border-top: 6px solid skyblue;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

</style>