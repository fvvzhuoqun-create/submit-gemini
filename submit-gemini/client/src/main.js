import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';

import 'font-awesome/css/font-awesome.min.css';

import "./assets/style.css";
// 1. 引入获取用户信息的接口
import { getLoginUser } from "./api";

Vue.use(ElementUI);

Vue.config.productionTip = false;

import initMenu from "./utils/menus";

router.beforeEach((to, from, next) => {
  if (to.path == '/') {
    next();
  } else {
    // 2. 检查是否有 Token 但没有用户信息（说明是刷新了页面）
    const token = sessionStorage.getItem("token");
    if (token && !store.state.users.id) {
      // 异步获取用户信息并存入 Vuex
      getLoginUser(token).then(res => {
        if (res.code === 0) {
          store.commit("setUsers", res.data);
        }
      });
    }

    if (store.state.menus == null) {
      initMenu(router, store);
      next();
    } else {
      next();
    }
  }
});

new Vue({
  router,
  store,
  render: function (h) { return h(App) }
}).$mount('#app')