<template>
  <div v-if="dateList.length > 0" id="selectDayPlace">
    <h4> 어떤 일정을 삭제하실건가요? </h4>

    <select v-model="selectedDay" @change="updateVisits">
      <option v-for="(date, index) in dateList" :key="index" :value="index">
        Day {{ index + 1 }} - {{ date }}
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
      <button id="select_btn" @click="confirmSelection">삭제</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { removePlace } from '@/api/maps';
import { useDataStore } from '@/store/data';

export default {
  name: 'RemovePlace',
  setup(props, { emit }) {
    const dataStore = useDataStore();

    // ✅ null 보호
    const dateList = dataStore.dateList || [];
    const tripDay = ref(dateList.length);
    const selectedDay = ref(0);
    const selectedPlace = ref(null);
    const currentVisits = ref([]);

    const updateVisits = () => {
      const selectedDate = dateList[selectedDay.value];
      currentVisits.value = dataStore.visits?.[selectedDate] || [];
    };

    onMounted(() => {
      if (dateList.length > 0) updateVisits();
    });

    const confirmSelection = async () => {
      if (!selectedPlace.value) {
        alert("삭제할 장소를 선택하세요.");
        return;
      }

      const date = dateList[selectedDay.value];
      const place_name = selectedPlace.value;

      try {
        await removePlace(dataStore.userId, date, place_name);
        alert("장소가 삭제되었습니다.");
        emit("close");
        emit("refresh"); // CalPop.vue 갱신
      } catch (err) {
        console.error("삭제 실패:", err);
        alert("장소 삭제에 실패했습니다.");
      }
    };

    return {
      tripDay,
      dateList,
      selectedDay,
      selectedPlace,
      currentVisits,
      updateVisits,
      confirmSelection
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
