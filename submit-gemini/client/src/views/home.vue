<template>
  <el-container class="home-wrapper">
    <Nav></Nav>
    <el-container>
      <Menu :menuList="this.$store.state.menus.children"></Menu>
      <el-main class="fater-body">
        <el-breadcrumb v-if="this.$router.currentRoute.path != '/index' " class="fater-body-breadcrumb">
          <el-breadcrumb-item>系统首页</el-breadcrumb-item>
          <el-breadcrumb-item>{{ this.$router.currentRoute.name }}</el-breadcrumb-item>
        </el-breadcrumb>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
/* 1. 核心容器：应用动态渐变背景 */
.home-wrapper {
  position: relative;
  width: 100%;
  height: 100vh;

  /* --- 移植自登录页的背景样式 START --- */
  background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
  background-size: 300% 300%;
  animation: gradientBG 15s ease infinite;
  /* --- END --- */

  z-index: 10;            /* 保持层级高于登录页 */
  overflow: hidden;       /* 防止滚动条溢出 */
}

/* 2. 背景动画定义 */
@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 3. 针对主内容区的微调 */
/* 为了让背景透出来，确保内容区背景透明（这在全局 style.css 已设置，这里加个保险） */
.fater-body {
  background-color: transparent !important;
}
</style>

<script>
import Nav from "../components/nav.vue";
import Menu from "../components/menu.vue";

export default{
  data(){
    return {

    }
  },
  methods: {

  },
  components: {
    Nav,
    Menu
  }
}
</script>