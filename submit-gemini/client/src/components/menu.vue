<template>
  <el-aside class="fater-left">
    <div class="menu-container">
      <el-menu
          text-color="#718096"
          active-text-color="#ffffff"
          :default-active="this.$router.currentRoute.path"
          router
          unique-opened>
        <template v-for="(item, index) in menuList">
          <el-menu-item :key="index" :index="item.path">
            <i :class="item.icon"></i>
            <span slot="title">{{ item.name }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </div>
  </el-aside>
</template>

<style scoped>
/* 菜单容器调整，防止溢出 */
.menu-container {
  height: 100%;
  overflow-y: auto;
  /* 隐藏滚动条 */
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.menu-container::-webkit-scrollbar {
  display: none;
}

/* 覆盖 Element Menu 默认样式 */
.el-menu {
  border: none;
  background: transparent !important;
}

/* 菜单项基础样式 */
.el-menu-item {
  height: 50px;
  line-height: 50px;
  margin: 8px 10px; /* 上下间距，左右缩进形成悬浮感 */
  border-radius: 12px; /* 圆角矩形 */
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.el-menu-item i {
  color: #a0aec0;
  margin-right: 10px;
  transition: color 0.3s;
}

/* Hover 状态 - 微妙的上浮和变色 */
.el-menu-item:hover {
  background-color: #f7fafc !important;
  color: #667eea !important;
  transform: translateX(5px);
}
.el-menu-item:hover i {
  color: #667eea;
}

/* 选中状态 - 激进的渐变色和阴影 */
.el-menu-item.is-active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3); /* 紫色系投影 */
  transform: scale(1.02); /* 微微放大 */
}

.el-menu-item.is-active i {
  color: #ffffff !important;
}

/* 移除原有的右侧边框条 */
.el-menu-item.is-active::before {
  display: none;
}
</style>

<script>
export default{
  props: {
    menuList: []
  },
}
</script>