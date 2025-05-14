<template>
  <div id="pop">
    <header> <!-- 팝업의 헤더 -->
      <h2 id="place_name"> {{ name }}</h2>
      <h4 id="place_address"> {{ address }} </h4>
      <h4 id="running time"> {{ day }} {{ time }}</h4>
    </header>
    <article id ="review">
      <!-- <iframe src="https://www.instagram.com/explore/search/keyword/?q=해지개" width="98%" height="100%"> </iframe> -->
    </article>
    <footer>
      <button id = "close_btn"> 닫기❌ </button>
    </footer>
  </div>
</template>

<script>
  export default {
    name: 'Place_',
    props: {
      name: String,
      address: String,
      day: String,
      time: String
    }
  }
</script>

<style scoped>
#pop {
  width: 330px;
  height: 85%;
  background-color: white;
  border: 3px solid skyblue;
  border-radius: 10px;
}
  
header {
  width: 90%;
  height: 20%;
} 
  
article {
  width: 100%;
  height: 70%;
} 
  
footer {
  display: flex;
  justify-content: flex-start; /* 좌측 정렬 */
  padding: 10px; /* 여백 추가 */
}
  
#close_btn {
  background-color: none; /* 버튼 배경색 */
  border: none; /* 테두리 제거 */
  padding: 8px 12px; /* 패딩 추가 */
  cursor: pointer; /* 커서 변경 */
}
</style>