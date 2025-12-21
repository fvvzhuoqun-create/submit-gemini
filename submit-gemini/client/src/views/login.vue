<template>
  <div class="login-container">
    <div class="login-mask"></div>

    <div class="login-body">
      <div class="login-title">
        校园社团管理系统
        <div style="font-size: 14px; color: #999; margin-top: 10px; font-weight: normal;">User Login</div>
      </div>
      <div class="login-form">
        <el-form :model="loginForm" :rules="rules" ref="loginForm">
          <el-form-item prop="userName">
            <el-input type="text"
                      v-model="loginForm.userName"
                      prefix-icon="el-icon-user"
                      placeholder="请输入账号"></el-input>
          </el-form-item>
          <el-form-item prop="passWord">
            <el-input type="password"
                      v-model="loginForm.passWord"
                      prefix-icon="el-icon-lock"
                      placeholder="请输入密码" show-password></el-input>
          </el-form-item>
          <el-form-item>
            <el-button
                class="login-btn"
                @click="submitForm('loginForm')"
                type="primary" :loading="loading">立即登录</el-button>
            <div class="login-link">
              <el-link @click="showAddWin()" :underline="false" type="primary">注册新账号</el-link>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <el-dialog title="用户注册" width="700px" :modal="false" :visible.sync="showAddFlag">
      <el-form label-width="90px" :model="usersForm">
        <el-row :gutter="15">
          <el-col :span="12">
            <el-form-item label="用户账号">
              <el-input v-model="usersForm.userName"
                        placeholder="请输入用户账号…" autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用户密码">
              <el-input v-model="usersForm.passWord" type="password"
                        placeholder="请输入用户密码…" autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="15">
          <el-col :span="12">
            <el-form-item label="用户姓名">
              <el-input v-model="usersForm.name"
                        placeholder="请输入用户姓名…" autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用户年龄">
              <el-input v-model="usersForm.age"
                        placeholder="请输入用户年龄…" autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="15">
          <el-col :span="12">
            <el-form-item label="用户性别">
              <el-radio-group v-model="usersForm.gender">
                <el-radio label="男"></el-radio>
                <el-radio label="女"></el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model="usersForm.phone"
                        placeholder="请输入联系电话…" autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="联系地址">
          <el-input rows="4" type="textarea" v-model="usersForm.address"
                    placeholder="请输入联系地址…" autocomplete="off"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showAddFlag = false">取 消</el-button>
        <el-button type="primary" @click="addInfo()">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.login-container {
  /* 使用深色遮罩或模糊背景 */
  background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url("../assets/bg.jpg");
  background-size: cover;
  background-position: center;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  right: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-body {
  width: 400px;
  padding: 40px;
  background-color: rgba(255, 255, 255, 0.95); /* 轻微透明 */
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  /* 移除原来的粗边框 */
  border: none;
}

.login-title {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 40px;
  letter-spacing: 2px;
}

/* 输入框样式微调 */
.el-input__inner {
  height: 45px;
  line-height: 45px;
  background-color: #f5f7fa;
  border: none;
}

.login-btn {
  width: 100%;
  margin-top: 20px;
  height: 45px;
  font-size: 16px;
  letter-spacing: 4px;
  border-radius: 4px;
  background: linear-gradient(to right, #009999, #36d1d1); /* 渐变按钮 */
  border: none;
}

.login-link {
  margin-top: 15px;
  text-align: center;
}
</style>

<script>
// JS 逻辑保持不变，为了展示方便省略...
import initMenu from "../utils/menus.js";
import { login, addUsers } from '../api/index.js'
export default {
  data(){
    return {
      loading: false, // 增加loading状态
      showAddFlag: false,
      // ... 其他数据保持不变
      usersForm: {
        id: "",
        userName: "",
        passWord: "",
        name: "",
        gender: "",
        age: "",
        phone: "",
        address: "",
        type: 2,
        status: 1
      },
      loginForm: {
        userName: '',
        passWord: ''
      },
      rules: {
        userName: [{
          required: true,
          message: '用户账号必须输入',
          trigger: 'blur'
        }],
        passWord: [{
          required: true,
          message: '用户密码必须输入',
          trigger: 'blur'
        }],
      }
    }
  },
  methods: {
    // ... 保持原有逻辑
    showAddWin(){

      this.showAddFlag = true;
    },
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {

          login(this.loginForm).then(res => {

            this.$store.commit('setToken', res.data);
            sessionStorage.setItem("token", res.data);
            initMenu(this.$router, this.$store);
            this.$router.push('/index');
          });

        } else {

          return false;
        }
      });
    },
    addInfo(){

      addUsers(this.usersForm).then(resp =>{

        if(resp.code == 0){

          this.$confirm('注册成功, 立即登陆?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {

            login({userName: this.usersForm.userName, passWord: this.usersForm.passWord}).then(res => {

              this.$store.commit('setToken', res.data);
              sessionStorage.setItem("token", res.data);
              initMenu(this.$router, this.$store);
              this.$router.push('/index');
            });
          });
        }else{

          this.$message({
            message: resp.msg,
            type: 'warning'
          });
        }
      });
    }
  }
}
</script>