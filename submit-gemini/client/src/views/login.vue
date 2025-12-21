<template>
  <div class="login-container">
    <canvas id="particle-canvas" class="particle-canvas"></canvas>

    <div class="login-body slide-in-up">
      <div class="login-title">
        <i class="fa fa-users" style="color: #009999; margin-right: 10px;"></i>
        校园社团管理系统
        <div class="login-subtitle">Campus Club Management System</div>
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
                type="primary" :loading="loading">
              立即登录 <i class="el-icon-right"></i>
            </el-button>
            <div class="login-link">
              <el-link @click="showAddWin()" :underline="false" style="color: #009999;">注册新账号</el-link>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <el-dialog title="用户注册" width="700px" :modal-append-to-body="false" :visible.sync="showAddFlag" custom-class="custom-dialog">
      <el-form label-width="90px" :model="usersForm">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户账号">
              <el-input v-model="usersForm.userName" placeholder="请输入用户账号..." autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用户密码">
              <el-input v-model="usersForm.passWord" type="password" placeholder="请输入用户密码..." autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户姓名">
              <el-input v-model="usersForm.name" placeholder="请输入用户姓名..." autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用户年龄">
              <el-input v-model="usersForm.age" placeholder="请输入用户年龄..." autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
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
              <el-input v-model="usersForm.phone" placeholder="请输入联系电话..." autocomplete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="联系地址">
          <el-input rows="3" type="textarea" v-model="usersForm.address" placeholder="请输入联系地址..." autocomplete="off"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showAddFlag = false">取 消</el-button>
        <el-button type="primary" @click="addInfo()">立即注册</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
/* 容器全屏，背景使用深色渐变，衬托粒子 */
.login-container {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  right: 0;
  background: radial-gradient(circle at center, #2b323c 0%, #1a1f25 100%);
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1;
}

/* 粒子画布层级 */
.particle-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
}

/* 登录框：毛玻璃效果 */
.login-body {
  width: 420px;
  padding: 50px 40px;
  background: rgba(255, 255, 255, 0.9); /* 如果喜欢深色模式，可改为 rgba(30,30,30,0.6) 并调整文字颜色 */
  backdrop-filter: blur(20px); /* 关键：背景模糊 */
  -webkit-backdrop-filter: blur(20px);
  border-radius: 16px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2), 0 5px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.5);
  transition: transform 0.3s ease;
}

.login-body:hover {
  transform: translateY(-5px); /* 悬浮微动 */
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.login-title {
  text-align: center;
  font-size: 26px;
  font-weight: bold;
  color: #333;
  margin-bottom: 40px;
  letter-spacing: 1px;
}

.login-subtitle {
  font-size: 14px;
  color: #888;
  margin-top: 8px;
  font-weight: normal;
  text-transform: uppercase;
  letter-spacing: 2px;
}

/* 按钮样式优化 */
.login-btn {
  width: 100%;
  margin-top: 20px;
  height: 48px;
  font-size: 16px;
  letter-spacing: 2px;
  border-radius: 24px; /* 圆角按钮 */
  background: linear-gradient(135deg, #009999 0%, #36d1d1 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(0, 153, 153, 0.3);
  transition: all 0.3s ease;
}

.login-btn:hover {
  background: linear-gradient(135deg, #008080 0%, #2bbaba 100%);
  transform: scale(1.02);
  box-shadow: 0 6px 20px rgba(0, 153, 153, 0.4);
}

.login-link {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
}

/* 入场动画 */
.slide-in-up {
  animation: slideInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 深度选择器修改 element-ui 输入框样式 */
.login-form >>> .el-input__inner {
  height: 48px;
  line-height: 48px;
  border-radius: 8px;
  background-color: #f7f9fc;
  border: 1px solid #dcdfe6;
  transition: all 0.3s;
}

.login-form >>> .el-input__inner:focus {
  background-color: #fff;
  border-color: #009999;
  box-shadow: 0 0 0 2px rgba(0, 153, 153, 0.1);
}

.login-form >>> .el-input__prefix {
  left: 10px;
  color: #909399;
}
</style>

<script>
import initMenu from "../utils/menus.js";
import { login, addUsers } from '../api/index.js'

export default {
  data(){
    return {
      loading: false,
      showAddFlag: false,
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
        userName: [{ required: true, message: '用户账号必须输入', trigger: 'blur' }],
        passWord: [{ required: true, message: '用户密码必须输入', trigger: 'blur' }],
      }
    }
  },
  mounted() {
    // 页面加载完成后初始化粒子效果
    this.initParticles();
    // 监听窗口大小改变
    window.addEventListener('resize', this.resizeCanvas);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeCanvas);
  },
  methods: {
    // ---------------- 粒子特效逻辑 ----------------
    initParticles() {
      const canvas = document.getElementById('particle-canvas');
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      let width = window.innerWidth;
      let height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;

      // 粒子配置
      const particles = [];
      const particleCount = 80; // 粒子数量
      const connectionDistance = 150; // 连线距离

      class Particle {
        constructor() {
          this.x = Math.random() * width;
          this.y = Math.random() * height;
          this.vx = (Math.random() - 0.5) * 1.5; // X轴速度
          this.vy = (Math.random() - 0.5) * 1.5; // Y轴速度
          this.size = Math.random() * 2 + 1;
          // 社团主题色：青色、蓝色
          const colors = ['rgba(0, 153, 153, 0.8)', 'rgba(64, 158, 255, 0.8)', 'rgba(255, 255, 255, 0.5)'];
          this.color = colors[Math.floor(Math.random() * colors.length)];
        }
        update() {
          this.x += this.vx;
          this.y += this.vy;
          // 边界反弹
          if (this.x < 0 || this.x > width) this.vx *= -1;
          if (this.y < 0 || this.y > height) this.vy *= -1;
        }
        draw() {
          ctx.beginPath();
          ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
          ctx.fillStyle = this.color;
          ctx.fill();
        }
      }

      // 初始化粒子
      for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
      }

      const animate = () => {
        ctx.clearRect(0, 0, width, height);

        // 绘制连线
        for (let i = 0; i < particles.length; i++) {
          for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < connectionDistance) {
              ctx.beginPath();
              // 线条透明度随距离变化
              const opacity = 1 - distance / connectionDistance;
              ctx.strokeStyle = `rgba(100, 200, 200, ${opacity * 0.3})`;
              ctx.lineWidth = 1;
              ctx.moveTo(particles[i].x, particles[i].y);
              ctx.lineTo(particles[j].x, particles[j].y);
              ctx.stroke();
            }
          }
        }

        // 绘制粒子
        particles.forEach(p => {
          p.update();
          p.draw();
        });

        requestAnimationFrame(animate);
      };

      animate();
    },
    resizeCanvas() {
      const canvas = document.getElementById('particle-canvas');
      if(canvas) {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      }
    },
    // ---------------- 原有业务逻辑 ----------------
    showAddWin(){
      this.showAddFlag = true;
    },
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          this.loading = true; // 开启加载状态
          login(this.loginForm).then(res => {
            this.loading = false;
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
    }
  }
}
</script>