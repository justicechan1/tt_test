<template>
  <div id="start_section">
    <main id="welcome_text">
      <h2> 사용자 맞춤 감성 여행 플랜 웹사이트 </h2>
      <h1> Trendy Trip✈️ </h1> 

      <p> 시작하려면 버튼을 눌러주세요</p>

      <RouterLink id="start_btn" to="/user"> 시작하기 </RouterLink>
    </main>
  </div>
</template>


<style>
#start_section {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

#welcome_text {
  width: 80vh;
  height: 75vh;
  max-width: 100vh;
  display: flex;
  flex-direction: column; /* 이 부분 추가 */
  justify-content: flex-start;
  align-items: flex-start;
  padding: 40px;
  box-sizing: border-box;
  border: 2px solid skyblue;
  box-shadow: 0 4px 20px rgba(150, 228, 232, 0.5);
  border-radius: 12px;
  background-color: white;
}

#welcome_text h1,
#welcome_text h2 {
  color: skyblue;           /* 폰트 색상 변경 */
  line-height: 1.2;         /* 행간 조정 (1.2는 약간 밀착된 느낌) */
  margin: 0;                /* 기본 마진 제거 (더 촘촘하게 붙이기 위함) */
}

#start_btn {
  padding: 16px 32px;         /* 내부 여백 확대 */
  font-size: 1.2rem;          /* 글자 크기 증가 */
  border-radius: 25px;
  background-color: #dce9f5;
  border: none;
  cursor: pointer;
  color:black;
  min-width: 160px;           /* 최소 너비 지정 (선택사항) */
  text-decoration: none;
}

</style>