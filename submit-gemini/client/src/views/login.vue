<template>
  <div class="login-container">
    <div class="login-content-wrapper slide-in-up">
      <div class="login-intro">
        <div class="school-branding-container">
          <h1 class="school-name">西北农林科技大学</h1>
          <div class="school-slogan-wrapper">
            <span class="slogan-deco-line"></span>
            <span class="school-slogan">共同创造</span>
            <span class="slogan-deco-line"></span>
          </div>
        </div>
        <h2 class="welcome-title">Welcome Back</h2>
        <p>开启您的智慧校园社团之旅</p>
        <div class="intro-decoration"></div>
      </div>

      <div class="login-body">
        <div class="login-title">
          <div class="title-main">社团管理系统</div>
          <div class="title-sub">Campus Club System</div>
        </div>

        <div class="login-form">
          <el-form :model="loginForm" :rules="rules" ref="loginForm">
            <el-form-item prop="userName">
              <el-input type="text"
                        v-model="loginForm.userName"
                        placeholder="用户名 / Email"></el-input>
            </el-form-item>
            <el-form-item prop="passWord">
              <el-input type="password"
                        v-model="loginForm.passWord"
                        placeholder="密码" show-password></el-input>
            </el-form-item>
            <el-form-item>
              <el-button
                  class="login-btn"
                  @click="submitForm('loginForm')"
                  type="primary" :loading="loading">
                登 录
              </el-button>

              <div class="login-options">
                <span @click="showAddWin()">注册账号</span>
                <span @click="showResetWin()">忘记密码?</span>
              </div>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>

    <el-dialog title="用户注册" width="700px" :modal-append-to-body="false" :visible.sync="showAddFlag" custom-class="custom-dialog">
      <el-form label-width="90px" :model="usersForm" :rules="registerRules" ref="registerForm">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户账号" prop="userName">
              <el-input v-model="usersForm.userName" placeholder="请输入用户账号..." autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用户密码" prop="passWord">
              <el-input v-model="usersForm.passWord" type="password" placeholder="请输入用户密码..." autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户姓名" prop="name">
              <el-input v-model="usersForm.name" placeholder="请输入用户姓名..." autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用户年龄" prop="age">
              <el-input v-model="usersForm.age" placeholder="请输入用户年龄..." autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户性别" prop="gender">
              <el-radio-group v-model="usersForm.gender">
                <el-radio label="男"></el-radio>
                <el-radio label="女"></el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="usersForm.phone" placeholder="请输入联系电话..." autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="联系地址" prop="address">
          <el-input rows="3" type="textarea" v-model="usersForm.address" placeholder="请输入联系地址..." autocomplete="off"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showAddFlag = false">取 消</el-button>
        <el-button type="primary" @click="addInfo()">立即注册</el-button>
      </div>
    </el-dialog>

    <el-dialog title="找回密码" width="500px" :modal-append-to-body="false" :visible.sync="showResetFlag" custom-class="custom-dialog">
      <el-form label-width="90px" :model="resetForm" :rules="resetRules" ref="resetForm">
        <el-form-item label="用户账号" prop="userName">
          <el-input v-model="resetForm.userName" placeholder="请输入您的账号" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="预留手机" prop="phone">
          <el-input v-model="resetForm.phone" placeholder="请输入注册时的手机号" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="新密码" prop="newPassWord">
          <el-input v-model="resetForm.newPassWord" type="password" placeholder="请输入新密码" autocomplete="off"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showResetFlag = false">取 消</el-button>
        <el-button type="primary" @click="submitReset()">确认重置</el-button>
      </div>
    </el-dialog>

  </div>
</template>

<style scoped>
/* 1. 动态流动背景 - 性能优化版 */
.login-container {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  right: 0;
  /* 极光渐变背景 */
  background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
  background-size: 300% 300%; /* 减小尺寸以提升性能 */
  animation: gradientBG 15s ease infinite;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1;
  /* 开启 GPU 硬件加速 */
  transform: translate3d(0, 0, 0);
}

@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 2. 主容器 */
.login-content-wrapper {
  display: flex;
  width: 900px;
  height: 550px;
  background: rgba(255, 255, 255, 0.95); /* 稍微增加不透明度减少混合计算 */
  backdrop-filter: blur(10px); /* 降低模糊半径 */
  -webkit-backdrop-filter: blur(10px);
  border-radius: 24px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.15); /* 阴影更轻 */
  overflow: hidden;
  position: relative;
  /* 开启硬件加速 */
  will-change: transform, opacity;
}

/* 左侧装饰区 */
.login-intro {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  /* 修改对齐方式，改为从顶部开始布局，方便放置学校名称 */
  justify-content: flex-start;
  padding-top: 60px; /* 顶部留白 */
  align-items: center;
  color: white;
  position: relative;
  overflow: hidden;
}

/* --- 新增：学校品牌艺术字样式 --- */
.school-branding-container {
  text-align: center;
  z-index: 5; /* 确保在装饰圆圈上面 */
  margin-bottom: auto; /* 将下方内容推到底部中央 */
}

.school-name {
  font-size: 26px;
  font-weight: 700;
  /* 优先使用衬线体营造学术和艺术感，如果没有则后退到黑体 */
  font-family: "Songti SC", "STSong", "SimSun", "Times New Roman", serif;
  letter-spacing: 3px;
  margin-bottom: 12px;
  text-shadow: 0 2px 10px rgba(0,0,0,0.2); /* 增加立体感 */
  background: linear-gradient(to bottom, #ffffff, #e0e0e0); /* 微妙的金属渐变感 */
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.school-slogan-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.85;
}

.school-slogan {
  font-size: 14px;
  font-weight: 300;
  letter-spacing: 6px; /* 大字间距营造高级感 */
  margin: 0 15px;
  text-transform: uppercase;
}

/* 艺术装饰短线 */
.slogan-deco-line {
  display: inline-block;
  width: 30px;
  height: 1px;
  background: rgba(255,255,255,0.5);
}
/* --- 新增结束 --- */


/* 修改原有的 h2 样式，增加顶部间距，避免离学校名字太近 */
.login-intro h2.welcome-title {
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 20px;
  z-index: 2;
  margin-top: 40px; /* 新增：与上方学校名字拉开距离 */
}

.login-intro p {
  font-size: 16px;
  opacity: 0.9;
  z-index: 2;
  letter-spacing: 2px;
  /* 确保下方留白 */
  margin-bottom: 80px;
}

/* 左侧装饰圆圈 */
.intro-decoration {
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
  bottom: -50px;
  left: -50px;
}
.intro-decoration::before {
  content: '';
  position: absolute;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
  top: -100px;
  right: -50px;
}

/* 3. 右侧登录表单区 */
.login-body {
  flex: 1;
  padding: 60px 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background-color: #fff;
}

.login-title {
  text-align: center;
  margin-bottom: 40px;
}
.title-main {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}
.title-sub {
  font-size: 14px;
  color: #999;
  margin-top: 5px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* 按钮重写 */
.login-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
  margin-top: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 10px 20px rgba(118, 75, 162, 0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.login-btn:hover {
  background: linear-gradient(135deg, #5a6fd6 0%, #684291 100%);
  transform: translateY(-2px);
  box-shadow: 0 15px 25px rgba(118, 75, 162, 0.4);
}

.login-options {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #666;
}
.login-options span {
  cursor: pointer;
  transition: color 0.3s;
}
.login-options span:hover {
  color: #667eea;
  text-decoration: underline;
}

/* 输入框样式覆盖 */
.login-form >>> .el-input__inner {
  background-color: #f7f9fc;
  border: none;
  border-radius: 8px;
  height: 50px;
  padding-left: 20px;
  transition: background-color 0.3s ease;
}
.login-form >>> .el-input__inner:focus {
  background-color: #fff;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

/* 动画 - 确保硬件加速 */
.slide-in-up {
  animation: slideInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
}
@keyframes slideInUp {
  from { opacity: 0; transform: translate3d(0, 50px, 0); }
  to { opacity: 1; transform: translate3d(0, 0, 0); }
}
</style>

<script>
// 移除了复杂的粒子动画逻辑，只保留纯业务逻辑
import initMenu from "../utils/menus.js";
import { login, addUsers, resetUserPwd } from '../api/index.js'

export default {
  data(){
    return {
      loading: false,
      showAddFlag: false,
      showResetFlag: false,
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
      resetForm: {
        userName: "",
        phone: "",
        newPassWord: ""
      },
      loginForm: {
        userName: '',
        passWord: ''
      },
      rules: {
        userName: [{ required: true, message: '用户账号必须输入', trigger: 'blur' }],
        passWord: [{ required: true, message: '用户密码必须输入', trigger: 'blur' }],
      },
      registerRules: {
        userName: [{ required: true, message: '请输入用户账号', trigger: 'blur' }],
        passWord: [{ required: true, message: '请输入用户密码', trigger: 'blur' }],
        name: [{ required: true, message: '请输入用户姓名', trigger: 'blur' }],
        age: [{ required: true, message: '请输入用户年龄', trigger: 'blur' }],
        gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
        phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
      },
      resetRules: {
        userName: [{ required: true, message: '请输入账号', trigger: 'blur' }],
        phone: [{ required: true, message: '请输入预留手机号', trigger: 'blur' }],
        newPassWord: [{ required: true, message: '请输入新密码', trigger: 'blur' }]
      }
    }
  },
  // 删除了 mounted 和 beforeDestroy 中关于粒子的代码
  methods: {
    showAddWin(){
      this.showAddFlag = true;
      this.$nextTick(() => {
        if(this.$refs['registerForm']) {
          this.$refs['registerForm'].resetFields();
        }
      });
    },
    showResetWin() {
      this.showResetFlag = true;
      this.$nextTick(() => {
        if(this.$refs['resetForm']) {
          this.$refs['resetForm'].resetFields();
        }
      });
    },
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          this.loading = true; // 开启加载状态
          login(this.loginForm).then(res => {
            this.loading = false;
            // 登录成功后直接跳转
            this.$store.commit('setToken', res.data);
            sessionStorage.setItem("token", res.data);
            initMenu(this.$router, this.$store);
            this.$router.push('/index');
          }).catch(() => {
            this.loading = false;
          });
        } else {
          return false;
        }
      });
    },
    addInfo(){
      this.$refs['registerForm'].validate((valid) => {
        if (valid) {
          addUsers(this.usersForm).then(resp =>{
            if(resp.code == 0){
              this.$confirm('注册成功, 立即登陆?', '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'success'
              }).then(() => {
                login({userName: this.usersForm.userName, passWord: this.usersForm.passWord}).then(res => {
                  this.$store.commit('setToken', res.data);
                  sessionStorage.setItem("token", res.data);
                  initMenu(this.$router, this.$store);
                  this.$router.push('/index');
                });
              });
              this.showAddFlag = false;
            }else{
              this.$message({
                message: resp.msg,
                type: 'warning'
              });
            }
          });
        } else {
          this.$message.warning("请填写除联系地址外的所有必填项");
          return false;
        }
      });
    },
    submitReset() {
      this.$refs['resetForm'].validate((valid) => {
        if (valid) {
          resetUserPwd({
            userName: this.resetForm.userName,
            phone: this.resetForm.phone,
            passWord: this.resetForm.newPassWord
          }).then(resp => {
            if (resp.code == 0) {
              this.$message.success("密码重置成功，请使用新密码登录");
              this.showResetFlag = false;
            } else {
              this.$message.warning(resp.msg);
            }
          });
        } else {
          return false;
        }
      });
    }
  }
}
</script>