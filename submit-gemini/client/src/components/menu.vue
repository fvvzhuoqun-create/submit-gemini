<template>
  <el-aside class="fater-left">
    <el-menu
        active-text-color="#009999"
        text-color="#606266"
        :default-active="this.$router.currentRoute.path"
        router
        unique-opened>
      <template v-for="(item, index) in menuList">
        <el-menu-item :key="index" :index="item.path" class="menu-item-custom">
          <i :class="item.icon"></i>
          <span slot="title" style="margin-left: 8px;">{{ item.name }}</span>
        </el-menu-item>
      </template>
    </el-menu>
  </el-aside>
</template>

<style scoped>
/* 选中项增加左侧色条和背景色 */
.el-menu-item.is-active {
  background-color: #e6fafa !important; /* 极浅的主色背景 */
  border-right: 3px solid #009999;
}

.el-menu-item {
  height: 50px;
  line-height: 50px;
  margin: 4px 0; /* 增加项间距 */
}
.el-menu-item:hover {
  background-color: #f5f7fa !important;
  color: #009999 !important;
}
</style>

<script>
export default{
  props: {
    menuList: []
  },
}
</script>