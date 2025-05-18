<template>
  <div id="pop">
    <header>
      <h2> 🍊{{ trip_area }}여행 </h2>
      <p> {{ startDay }} ~ {{ endDay }} </p>
      <p> 총 {{ tripday }}일 </p>
      <select v-model="selectedDay" @change="SelectedDay">
        <option v-for="n in tripday" :key="n" :value="n - 1"> Day {{ n }} </option>
      </select>
    </header>

    <article id="choose">
      <hr style="border: 1px solid skyblue; width: 80%; margin: 20px auto;" />

      <ul v-if="currentVisits.length > 0">
        <li v-for="visit in currentVisits" :key="visit.order">
          <strong class="visit_num">{{ visit.order }}</strong>
          <span>{{ visit.place }}</span>
          <p>이동시간: {{ visit.arrival_str }} ~ {{ visit.departure_str }}</p>
          <p>체류시간: {{ visit.stay_duration }}</p>
          <hr style="border: 1px solid skyblue; width: 90%; margin-right: 30px;" />
        </li>
      </ul>
      <p v-else>선택된 일차에 방문지가 없습니다.</p>
    </article>

    <footer>
      <button id="close_btn" @click="$emit('close')"> 닫기❌ </button>
    </footer>
  </div>
</template>

<script>
import { useDataStore } from '@/store/data';
import { getRoute } from '@/api/maps';

export default {
  name: 'CalPop',
  data() {
    return {
      selectedDay: 0,
      routeData: [],
      userId: localStorage.getItem('userId') ?? '1'
    };
  },
  setup() {
    const data = useDataStore();
    return {
      trip_area: data.area,
      startDay: data.startDate,
      endDay: data.endDate,
      tripday: data.TripDays
    };
  },
  computed: {
    currentVisits() {
      return [...(this.routeData || [])].sort((a, b) => a.order - b.order);
    },
    currentDate() {
      const date = new Date(this.startDay);
      date.setDate(date.getDate() + this.selectedDay);
      return date.toISOString().split('T')[0];
    }
  },
  methods: {
    async SelectedDay() {
      this.$emit("loading", true);
      try {
        const res = await getRoute(this.userId, this.currentDate);
        this.routeData = [...(res.visits || [])].sort((a, b) => a.order - b.order);

        this.$emit("select-day", {
          coordinates: this.routeData.map(v => ({ x: v.x_cord, y: v.y_cord })),
          path: res.path || [],
        });
      } catch (error) {
        console.warn("🚫 해당 날짜의 경로 없음:", error.response?.data || error);
        this.routeData = [];
      } finally {
        this.$emit("loading", false); 
        }
    }
  },
  mounted() {
    this.SelectedDay();
  },
  watch: {
    selectedDay() {
      this.SelectedDay();
    }
  }
};
</script>

<style scoped>
#pop {
  display: flex;
  flex-direction: column;
  margin: 10px;
  width: 300px;
  height: 90%;
  background-color: white;
  border: 3px solid skyblue;
  border-radius: 10px;
  position: absolute;
}

header {
  height: 30%;
  width: 100%;
  padding-left: 20px;
}

#choose {
  width: 100%;
  height: 80%;
  margin-top: 10px;
  overflow-y: auto;
}

select {
  padding: 10px;
  border-radius: 8px;
  border-color: skyblue;
  font-size: 14px;
}

.visit_num {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  width: 24px;
  height: 24px;
  background-color: skyblue;
  color: white;
  border-radius: 50%;
  font-size: 14px;
  margin-right: 8px;
}

ul {
  margin: 0;
  padding-left: 20px;
}

li {
  list-style-type: none;
  margin-bottom: 8px;
}

li p {
  margin: 0;
  color: gray;
}

footer {
  height: 10%;
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

#close_btn {
  padding: 10px;
  background-color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}
</style>
