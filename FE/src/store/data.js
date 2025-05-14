import { defineStore } from 'pinia'

export const useDataStore = defineStore('data', {
  // 상태 정의
  state: () => ({
    area: '',
    TripDays: 0,
    startDate: '',
    endDate: ''
  }),

  // getters (선택사항)
  getters: {},

  // actions (상태 변경 메서드)
  actions: {
    setArea(area) {
      this.area = area
    },
    setTripDay(days) {
      this.TripDays = days
    },
    setStartDay(date) {
      this.startDate = date
    },
    setEndDate(date) {
      this.endDate = date
    }
  }
});