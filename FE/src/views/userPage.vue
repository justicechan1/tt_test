<template>
  <div id="user_section">
    <main id="travel_section">
      <Transition name="fade" mode="out-in">
        <component :is="currentComponent" :key="step" v-on="{ next: nextPage, prev: prevPage }" />
      </Transition>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AreaPage from '@/components/areaSection.vue'
import DayPage from '@/components/daySection.vue'
import TimePage from '@/components/timeSection.vue'

const step = ref(0)

const components = [AreaPage, DayPage, TimePage]

const currentComponent = computed(() => components[step.value])

const nextPage = () => {
  if (step.value < components.length - 1) step.value++
}

const prevPage = () => {
  if (step.value > 0) step.value--
}
</script>

<style>

/* 전체 페이지 레이아웃 설정 */
#user_section {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  display: flex;
  justify-content: center;  /* 수평 중앙 정렬 */
  align-items: center;      /* 수직 중앙 정렬 */
}


/* 콘텐츠 카드 스타일 */
#travel_section {
  width: 70vh;
  height: 75vh;
  min-width: 60vh;
  min-height: 75vh;
  max-width: 80vh;
  max-height: 75vh;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 2px solid skyblue;
  box-shadow: 0 4px 20px rgba(150, 228, 232, 0.5);
  border-radius: 12px;
  background-color: white;
}

/* 컴포넌트 전환 효과 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>