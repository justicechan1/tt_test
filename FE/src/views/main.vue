<template>
  <div id="map_page">
    <nav id="side">
      <ul class="nav_list">
        <li style="background-color: skyblue; border-color: skyblue;">
          <h1> ✈️ </h1>
        </li>
        <li id="side_btn">
          <button id="search_btn" @click="search_Popup($event)">
            <p> 🔍 </p>
          </button>
        </li>
        <li id="side_btn">
          <button id="calender_btn" @click="calendar_Popup($event)">
            <span> 📆 </span>
          </button>
        </li>
        <li id="side_btn">
          <button id="save_btn" @click="save_Popup($event)">
            <span> 💾 </span>
          </button>
        </li>
        <li id="side_btn">
          <button id="test_btn" @click="place_Popup($event)">
            <span> ❓ </span>
          </button>
        </li>
      </ul>
    </nav>

    <div id="map" style="width: 100%; height: 100%;"></div>

    <!-- 팝업 슬라이딩 애니메이션 -->
    <transition name="slide-popup">
      <CalPop v-if="isCalendarPopupVisible" class="popup-panel" @close="calendar_Popup" />
    </transition>
    <transition name="slide-popup">
      <SearchPop v-if="isSearchPopupVisible" class="popup-panel" @close="search_Popup" @select-place="handleSelectPlace"/>
    </transition>
    <transition name="slide-popup">
      <SavePop v-if="isSavePopupVisible" class="popup-panel" @close="save_Popup" />
    </transition>

    <PlacePop 
      v-if="isPlacePopupVisible" 
      :key="selectedPlace?.name"
      :place="selectedPlace"
      :style="popupStyle"
      @close="handleClosePlace"
    />
    <div id="category_btn">
      <button class="category-button" @click="handleRoundButtonClick">관광명소</button>
      <button class="category-button" @click="handleRoundButtonClick">카페</button>
      <button class="category-button" @click="handleRoundButtonClick">음식점</button>
    </div>
  </div>
</template>

<script>
import CalPop from '@/components/calender.vue'  // 일정 표
import SearchPop from '@/components/search.vue'  // 장소 검색
import SavePop from '@/components/save_file.vue'  // 파일 저장장
import PlacePop from '@/components/place.vue'

export default {
  name: 'MainPage',
  components: {
    SearchPop,
    CalPop,
    SavePop,
    PlacePop
  },
  data() {
    return {
      selectedPlace: null,
      isCalendarPopupVisible: false, // 달력 팝업 상태 관리
      isSearchPopupVisible: false, // 검색 팝업 상태 관리
      isSavePopupVisible: false,
      isPlacePopupVisible: false,
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
      if (this.isCalendarPopupVisible) {
        this.closePopups(); // 이미 열려있으면 닫기
      } else {
        this.closePopups(); // 다른 팝업 닫기
        this.isCalendarPopupVisible = true; // 달력 팝업 열기
        this.popupStyle = {
          position: 'absolute',
          top: `20px`,
          left: `110px`,
          zIndex: 1000
        };
      }
    },
    search_Popup() {
      if (this.isSearchPopupVisible) {
        this.closePopups(); // 이미 열려있으면 닫기
      } else {
        this.closePopups(); // 다른 팝업 닫기
        this.isSearchPopupVisible = true; // 검색 팝업 열기
        this.popupStyle = {
          position: 'absolute',
          top: `20px`,
          left: `110px`,
          zIndex: 1000
        };
      }
    },
    save_Popup() {
      if (this.isSavePopupVisible) {
        this.closePopups(); // 이미 열려있으면 닫기
      } else {
        this.closePopups(); // 다른 팝업 닫기
        this.isSavePopupVisible = true; // 검색 팝업 열기
        this.popupStyle = {
          position: 'absolute',
          top: `20px`,
          left: `110px`,
          zIndex: 1000
        };
      }
    },
    handleSelectPlace(place) {
      this.selectedPlace = place;
      this.isPlacePopupVisible = true;
      this.popupStyle = {
          position: 'absolute',
          top: `30px`,
          left: `420px`, // 검색 팝업 오른쪽에 위치
          zIndex: 1000
        };
    },
    handleClosePlace() {
      this.selectedPlace = null; // 장소 팝업만 닫기
      this.isPlacePopupVisible = false;
    }
  },
  mounted() {
    // 네이버 지도 API 스크립트 로드
    const script = document.createElement("script");
    script.src = "https://openapi.map.naver.com/openapi/v3/maps.js?ncpKeyId=f0u1dydazz"; // 실제 NCP Client ID로 변경
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);

    script.onload = () => {
      // 네이버 지도 생성
      new window.naver.maps.Map("map", {
        center: new window.naver.maps.LatLng(33.4, 126.55), 
        zoom: 11,
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

</style>