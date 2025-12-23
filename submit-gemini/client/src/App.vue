<template>
  <div id="app">
    <div class="app-background">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <transition name="fade-transform" mode="out-in">
      <router-view />
    </transition>
  </div>
</template>

<style>
/* 确保 App 占满全屏 */
#app {
  width: 100%;
  height: 100vh;
  position: relative;
}

/* --- 背景动效实现 --- */
.app-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1; /* 置于最底层 */
  background: #1e1e2f; /* 兜底背景色 */
  overflow: hidden;
}

/* 漂浮的光斑 */
.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px); /* 强力高斯模糊 */
  opacity: 0.6;
  animation: floatShape 20s infinite alternate;
}

.shape-1 {
  width: 500px;
  height: 500px;
  background: #e14eca; /* 霓虹紫 */
  top: -10%;
  left: -10%;
  animation-duration: 25s;
}

.shape-2 {
  width: 400px;
  height: 400px;
  background: #1d8cf8; /* 电光蓝 */
  bottom: 10%;
  right: -5%;
  animation-duration: 30s;
  animation-delay: -5s;
}

.shape-3 {
  width: 300px;
  height: 300px;
  background: #00f2c3; /* 荧光青 */
  top: 40%;
  left: 40%;
  opacity: 0.4;
  animation-duration: 35s;
  animation-delay: -10s;
}

@keyframes floatShape {
  0% { transform: translate(0, 0) rotate(0deg); }
  100% { transform: translate(100px, 50px) rotate(20deg); }
}
</style>