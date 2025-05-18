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

    <!-- 팝업들 -->
    <transition name="slide-popup">
      <CalPop v-if="isCalendarPopupVisible" class="popup-panel" @close="calendar_Popup" @select-day="handleSelectDay" @loading="handleRouteLoading"/>
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

    <div id="category_btn">
      <button class="category-button" @click="handleRoundButtonClick">관광명소</button>
      <button class="category-button" @click="handleRoundButtonClick">카페</button>
      <button class="category-button" @click="handleRoundButtonClick">음식점</button>
    </div>

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

export default {
  name: 'MainPage',
  components: { CalPop, SearchPop, SavePop, PlacePop },
  data() {
    return {
      selectedPlace: null,
      selectedMarker: null,
      isCalendarPopupVisible: false,
      isSearchPopupVisible: false,
      isSavePopupVisible: false,
      isPlacePopupVisible: false,
      isLoadingRoute: false, //로딩
      popupStyle: {},
      markers: [],
      polyline: [],
      map: null
    };
  },
  methods: {
    closePopups() {
      this.isCalendarPopupVisible = false;
      this.isSearchPopupVisible = false;
      this.isSavePopupVisible = false;
      this.isPlacePopupVisible = false;
    },
    calendar_Popup() {
      this.togglePopup('isCalendarPopupVisible');
    },
    search_Popup() {
      this.togglePopup('isSearchPopupVisible');
    },
    save_Popup() {
      this.togglePopup('isSavePopupVisible');
    },
    place_Popup() {
      this.togglePopup('isPlacePopupVisible');
    },
    togglePopup(popupName) {
      if (this[popupName]) {
        this.closePopups();
      } else {
        this.closePopups();
        this[popupName] = true;
        this.popupStyle = {
          position: 'absolute',
          top: '20px',
          left: '110px',
          zIndex: 1000
        };
      }
    },
    handleSelectPlace(place) {
      console.log('🔥 선택된 장소:', place);
      this.selectedPlace = place;
      this.isPlacePopupVisible = true;
      this.popupStyle = {
        position: 'absolute',
        top: '30px',
        left: '420px',
        zIndex: 1000
      };
      if (this.selectedMarker) {
        this.selectedMarker.setMap(null);
      }

      setTimeout(() => {
        const placeData = this.$refs.placePopup?.placeData;

        if (placeData?.x_cord && placeData?.y_cord && this.map) {
          const latLng = new window.naver.maps.LatLng(placeData.y_cord, placeData.x_cord);
          this.selectedMarker = new window.naver.maps.Marker({
            position: latLng,
            map: this.map,
            icon: { //마커 부분 수정 해줘잉
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

      if (this.polyline) {
        this.polyline.forEach(line => line.setMap(null));
      }
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

      //경로 그리기
      let filteredPath = path;
      if (path.length > 1) {
        const [x1, y1] = path[0][0];
        const [xLast, yLast] = path[path.length - 1][1];
        if (x1 === xLast && y1 === yLast) {
          filteredPath = path.slice(0, -1);  
        }
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
        zoom: 11,
      });
    };
    
  },
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
  padding: 10px 15px; /* 패딩 */
  background-color: skyblue; /* 배경색 */
  color: white; /* 글자색 */
  border: none; /* 테두리 제거 */
  border-radius: 5px; /* 모서리 둥글게 */
  cursor: pointer; /* 커서 변경 */
}

.category-button:hover {
  background-color: deepskyblue; /* 호버 시 색상 변경 */
}

.popup-panel {
  position: absolute;
  top: 20px;
  left: 90px; /* 사이드바 바로 옆 */
  z-index: 1000;
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