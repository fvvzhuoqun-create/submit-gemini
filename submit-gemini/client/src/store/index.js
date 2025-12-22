import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
	state:{
		token: null,
		menus: null,
		users: {}, // 【修复】补充 users 对象，防止 nav.vue 启动时报错
	},
	getters: {
		getToken: state => {
			return state.token
		},
		getMenus: state => {
			return state.menus
		},
		// 【建议】添加获取用户信息的 getter
		getUsers: state => {
			return state.users
		}
	},
	mutations: {
		setToken: (state, newToken) =>{
			state.token = newToken;
		},
		clearToken: (state) =>{
			state.token = null;
		},
		setMenus: (state, menus) =>{
			state.menus = menus;
		},
		clearMenus: (state) =>{
			state.menus = null;
		},
		// 【修复】添加设置用户信息的 mutation
		setUsers: (state, users) =>{
			state.users = users;
		}
	}
})