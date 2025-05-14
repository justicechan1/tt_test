<template>
  <div id="pop">
    <header> <!-- 팝업의 헤더 -->
      <h2> 🍊{{ trip_area }}여행</h2>
      <p> {{ startDay }} ~ {{ endDay }} </p>
      <p> 총 {{ tripday }}일 </p>
    </header>
    <article id ="choose">
      <select>
        <option v-for="n in tripday" :key="n"> Day {{ n }} </option>
      </select>
    </article>
    <footer>
      <button id = "close_btn"> 닫기❌ </button>
    </footer>
  </div>
</template>

<script>
import { useDataStore } from '@/store/data'

export default {
  name: 'CalPop',
  props: {
    area: {
      type: String,
      required: false
    },
    days: {
      type: String,
      required: false
    },
    date: {
      type: String,
      required: false
    },
    tripDays: {
      type: Number,
      required: true
    }
  },
  setup() {
    const data = useDataStore();

    return {
      trip_area: data.area,
      startDay: data.startDate,
      endDay: data.endDate,
      tripday: data.TripDays
    }
  }
}
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
  height: 70%;
}

select {
  padding: 10px;
  border-radius: 8px;
  border: skyblue;
  font-size: 14px;
}

footer {
  height: 10%;
  width: 100%;
  display: flex;
  justify-content: flex-end; /* 👉 우측 정렬 */
  align-items: center; /* 수직 정렬 */
}

#close_btn {
  padding: 10px 10px 10px 10px;
  border-radius: 20px;
  background-color: #dce9f5;
  border: none;
  cursor: pointer;
}
</style>