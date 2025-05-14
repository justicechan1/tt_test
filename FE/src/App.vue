<template>
  <div id="app">
    <header id="web_title"> <!-- 타이틀 보여주기 -->
      <RouterLink class="home_link" to="/"> Trendy Trip✈️ </RouterLink>
    </header>

    <div id="view_section">
      <HomePage></HomePage> <!--초기 사용자 화면 -->

      <transition name="fade" mode="out-in">
        <router-view />
      </transition>
    </div>
  </div>
</template>

<style>
#app {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  font-family: 'Pretendard SemiBold', sans-serif;
}

#web_title {
  height: 10vh;
  width: 100%;
  padding-left: 30px;
  display: flex;
  align-items: center;
  font-size: 1.5em;
  font-family: 'Pretendard SemiBold', sans-serif;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 아래 전체 영역을 user_section이 채움 */
#view_section {
  width: 100%;
  height: 100%;
  flex: 1;
  display: flex;
  justify-content: center;  /* 수평 중앙 */
  align-items: center;      /* 수직 중앙 */
  background-color: rgb(238, 248, 250);
  overflow: hidden;
  position: relative;
}

.home_link {
  color: black;
  text-decoration: none;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>