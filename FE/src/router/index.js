import { createRouter, createWebHistory } from 'vue-router'
import MainPage from '@/views/main.vue' // 지도
import HomePage from '@/views/homePage.vue' // 시작 페이지
import UserPage from '@/views/userPage.vue' // 사용자 정의 페이지

const routes = [
  {
    path: '/',
    component: HomePage
  },
  {
    path: '/main',
    component: MainPage
  },
  {
    path: '/user',
    component: UserPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router