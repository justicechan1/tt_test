import { createApp } from 'vue'
import { createPinia } from 'pinia'  // 데이터 저장

import App from './App.vue'
import router from './router'

import VCalendar from 'v-calendar';
import 'v-calendar/style.css';

createApp(App).use(router).use(VCalendar, {}).use(createPinia()).mount('#app')