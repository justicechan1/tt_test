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
  }
});