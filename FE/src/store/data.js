import { defineStore } from 'pinia'

export const useDataStore = defineStore('data', {
  // 상태 정의
  state: () => ({
    area: '',
    TripDays: 0,
    startDate: new Date().toISOString().substring(0, 10),
    endDate: new Date().toISOString().substring(0, 10),
    startPlace: '',
    endPlace: '',
    startTime:'',
    endTime: '',
    dayPlan: []
  }),
  
  // getters (선택사항)
  getters: {
    getDayPlan: (state) => (day) => {
      return state.dayPlans.find(plan => plan.day === day)?.places || []
    }
  },

  // actions (상태 변경 메서드)
  actions: {
    setArea(area) {
      this.area = area
    },
    setTripDay(days) {
      this.TripDays = days
    },
    setStartDay(date) {
      this.startDate = date || new Date().toISOString().substring(0, 10)
    },
    setEndDate(date) {
      this.endDate = date || new Date().toISOString().substring(0, 10)
    },
    setUserPlan(splace, stime, eplace, etime) {
      this.startPlace = splace,
      this.endPlace = eplace,
      this.startTime = stime,
      this.endTime = etime
    },
    addPlaceToDay(day, name, address, time) {
      const dayPlan = this.dayPlans.find(plan => plan.day === day);
      if (dayPlan) {
        dayPlan.places.push({ name, address, time });
      } else {
        // 만약 dayPlan이 없다면 생성
        this.dayPlans.push({
          day: day,
          places: [{ name, address, time }]
        });
      }
    },

    // 장소 삭제 메서드
    removePlaceFromDay(day, index) {
      const dayPlan = this.dayPlans.find(plan => plan.day === day);
      if (dayPlan) {
        dayPlan.places.splice(index, 1);
      }
    }
  }
});