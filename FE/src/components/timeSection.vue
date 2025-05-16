<template>
  <div class="section">
    <div class="title">
      <p> 어디서부터 여행을 즐기실건가요? </p>
      <h3> 🏕️여행 장소를 입력해주세요 </h3>
    </div>
    <div class="article_section">
      <div id="start_info"> 
        <h4> ✈️ 출발 장소 및 시간 입력 </h4>
        <p> {{ startDay }} </p>
        <form id="start_input">
          <label>
            <input v-model="startPlace" type="radio" value="제주국제공항" /> 제주국제공항
          </label>
          <label>
            <input v-model="startPlace" type="radio" value="제주국제여객터미널" /> 제주국제여객터미널
          </label>
        </form> 
        <input v-model="startTime" type="time" id="start_time" />
      </div>

      <div id="end_info">
        <h4> ✈️ 마지막 장소 및 시간 입력 </h4>
        <p> {{ endDay }} </p>
        <form id="end_input">
          <label>
            <input v-model="endPlace" type="radio" value="제주국제공항" /> 제주국제공항
          </label>
          <label>
            <input v-model="endPlace" type="radio" value="제주국제여객터미널" /> 제주국제여객터미널
          </label>
        </form> 
        <input v-model="endTime" type="time" id="end_time" />
      </div>
    </div>

    <footer>
      <button id="before_btn" @click="$emit('prev')"> 이전 </button> 
      <button id="ok_btn" @click="saveData"> 확인 </button>  
    </footer>
  </div>
</template>

<script>
import { initSchedule } from '@/api/schedule'
import { useDataStore } from '@/store/data' 

export default {
  data() {
    return {
      startPlace: '',
      startTime: '',
      endPlace: '',
      endTime: '',
      previewPayload: null
    }
  },
  setup() {
    const data = useDataStore()
    return {
      startDay: data.startDate,
      endDay: data.endDate,
    };
  },
  methods: {
    async saveData() {
      if (!this.startPlace || !this.startTime || !this.endPlace || !this.endTime) {
        alert('출발/도착 장소와 시간을 모두 입력해주세요.');
        return;
      }

      const payload = {
        date: {
          user_id: '2',
          start_date: this.startDay,
        end_date: this.endDay
      },
      start_end: {
          arrival: this.startPlace,
          arrivaltime: this.startTime,
          departure: this.endPlace,
          departuretime: this.endTime
          },
        user: {
          start_time: "09:00",
          end_time: "18:00",
          travel_style: "편안한",
          meal_time_preferences: {
            breakfast: ["08:00"],
            lunch: ["12:30"],
            dinner: ["18:30"]
          }
        },
        places_by_day: {}
      };

      this.previewPayload = payload;
      console.log("보내는 payload ↓↓↓");
      console.log(JSON.stringify(payload, null, 2));

      try {
        await initSchedule(payload);
        this.$router.push('/main'); // 조건 통과 시에만 라우팅
      } catch (e) {
        console.error(e);
      }
    }
  }
}
</script>

<style scoped>
.section {
  padding: 20px;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.title {
  display: flex;
  padding: 20px;
  flex-direction: column;
}

.article_section {
  display: flex;
  flex-direction: column;
  max-height: 90%;
  padding: 30px;
  width: 100%;
  box-sizing: border-box;
}

.article_section p, h4 {
  margin: 0;
  padding: 0;
}

#start_input,
#start_time,
#end_input,
#end_time {
  width: 100%;
  padding: 10px;
  margin: 5px 0;
  border: 1px solid skyblue;
  border-radius: 5px;
  font-size: 16px;
}

.payload-preview {
  background-color: #f4f4f4;
  border: 1px solid #ccc;
  padding: 15px;
  margin: 20px;
  font-size: 14px;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
}

footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

#before_btn, #ok_btn {
  padding: 10px 20px;
  border-radius: 20px;
  background-color: #dce9f5;
  border: none;
  cursor: pointer;
}
</style>
