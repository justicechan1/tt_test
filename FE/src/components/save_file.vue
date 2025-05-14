<template>
    <div id="pop">
      <header> <!-- 팝업의 헤더 -->
        <h2> 📜다운로드 </h2>
      </header>
      <article id ="save_list">
    
      </article>
      <footer>
        <button id = "close_btn"> 닫기❌ </button>
      </footer>
    </div>
  </template>
    
  <script>
    export default {
      name: 'Save_',
    }
  </script>
    
  <style scoped>
  #pop {
  display: flex;
  flex-direction: column;
  padding: 10px;
  width: 300px;
  height: 90%;
  background-color: white;
  border: 3px solid skyblue;
  border-radius: 10px;
  position: absolute;
}

header {
  flex: 0 0 20%;
  width: 100%;
  padding: 10px;
}
    
#save_list {
  width: 100%;
  height: 70%;
} 
    
footer {
  flex: 0 0 10%;
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