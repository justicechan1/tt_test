<template>
  <div id="selectDayPlace"> 
    <h4> 어떤 일정을 삭제하실건가요? </h4>
    <select v-model="selectedDay" @change="updateVisits">
      <option v-for="(date, index) in dateList" :key="index" :value="index">
        Day {{ index + 1 }}
      </option>
    </select>

    <div class="radio-container" v-if="currentVisits.length">
      <div v-for="visit in currentVisits" :key="visit.order">
        <label>
          <input v-model="selectedPlace" type="radio" :value="visit.place" /> {{ visit.place }}
        </label>
      </div>
    </div>

    <div class="btn-container">
      <button id="close_btn" @click="$emit('close')">닫기❌</button>
      <button id="select_btn" @click="confirmSelection">확인</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import { useDataStore } from '@/store/data';
import { removePlace } from '@/api/maps';

export default {
  name: 'RemovePlacePop',
  props: {
    dateList: {
      type: Array,
      required: true
    },
    visitsByDate: {
      type: Object,
      required: true
    }
  },
  setup(props, { emit }) {
    const selectedDay = ref(0);
    const selectedPlace = ref(null);
    const currentVisits = ref([]);
    const dataStore = useDataStore();

    const updateVisits = () => {
      const selectedDate = props.dateList[selectedDay.value];
      currentVisits.value = props.visitsByDate?.[selectedDate] || [];
    };

    onMounted(updateVisits);
    watch(selectedDay, updateVisits);

    const confirmSelection = async () => {
      if (!selectedPlace.value) {
        alert("삭제할 장소를 선택하세요.");
        return;
      }
      try {
        const selectedDate = props.dateList[selectedDay.value];
        const payload = {
          places_by_day: {
            [selectedDate]: [{ name: selectedPlace.value }]
          }
        };
        await removePlace(dataStore.userId, payload);
        alert("장소가 삭제되었습니다.");
        emit("close");
        emit("refresh");
      } catch (err) {
        console.error("삭제 실패:", err);
        alert("장소 삭제에 실패했습니다.");
      }
    };

    return {
      selectedDay,
      selectedPlace,
      currentVisits,
      updateVisits,
      confirmSelection,
    };
  }
};
</script>

<style scoped>
#selectDayPlace {
  width: 250px;
  height: auto;
  padding: 20px;
  background-color: white;
  border: 3px solid skyblue;
  border-radius: 10px;
  position: absolute;
  top: 30px;
  left: 420px;
  z-index: 1000;
}

h4, h5 {
  margin: 0 0 10px 0;
}

.radio-container {
  margin: 10px 0;
}

.btn-container {
  flex: 0 0 10%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px;
}

#close_btn, #select_btn {
  background-color: white;
  border: none;
  cursor: pointer;
}
</style>
