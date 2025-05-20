<template>
  <div id="selectDayPlace"> 
    <h4> 어떤 일차에 여행하실래요? </h4>
    <div class="radio-container">
      <div v-for="n in tripDay" :key="n">
        <label>
          <input v-model="trip_day" type="radio" :value="n" /> Day {{ n }} 
        </label>
      </div>
    </div>
    <div class="btn-container">
        <button id="close_btn" @click="$emit('close')"> 닫기❌ </button>
        <button id="select_btn" @click="confirmSelection"> 확인 </button>
    </div>
  </div>
</template>

<script>
import { useDataStore } from '@/store/data'
import { ref } from 'vue'

export default {
  name: 'AddPlace',
  setup(props, { emit }) {
    const data = useDataStore();
    const trip_day = ref(null); // 선택된 Day 저장

    const confirmSelection = () => {
      if (trip_day.value !== null) {
        emit("day-confirmed", trip_day.value); // ✅ 부모 컴포넌트(Place.vue)로 선택한 Day 전달
      } else {
        alert("Day를 선택하세요.");
      }
    };

    return {
      tripDay: data.TripDays, // 전체 여행일 수
      trip_day,
      confirmSelection
    }
  }
}
</script>

<style scoped>
#selectDayPlace {
    width: 200px;
    height: auto;
    padding: 20px;
    background-color: white;
    border: 3px solid skyblue;
    border-radius: 10px;
    position: absolute;
}

h4 {
  margin: 0;
}

.radio-container {
  margin: 10px;
}

.btn-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

#close_btn,
#select_btn {
  background-color: white;
  border: none;
  font-size: 14px;
  cursor: pointer;
}
</style>
