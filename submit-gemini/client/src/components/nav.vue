<template>
  <div class="fater-header">
    <div class="fater-header-logo">
      <img src="../assets/school-logo.png" class="school-logo-img" alt="西北农林科技大学校徽">

      <div class="brand-text-group">
        <span class="brand-main-text">社团空间</span>
        <span class="brand-sub-text">NWAFU CLUBS</span>
      </div>
    </div>

    <div class="fater-header-user">
      <el-dropdown @command="handleCommand" trigger="click">
        <div class="user-profile-card">
          <img :src="userAvatarUrl || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'" class="user-avatar"/>
          <div class="user-info">
            <span class="name">{{ (this.$store.state.users && this.$store.state.users.name) || '管理员' }}</span>
            <span class="role">在线</span>
          </div>
          <i class="el-icon-arrow-down" style="margin-left: 10px; color: #a0aec0;"></i>
        </div>

        <el-dropdown-menu slot="dropdown" class="custom-dropdown">
          <el-dropdown-item command="profile" icon="el-icon-user">个人中心</el-dropdown-item>
          <el-dropdown-item command="logout" icon="el-icon-switch-button" divided style="color: #ff6b6b;">退出登录</el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
    </div>

    <el-dialog title="个人信息设置" :visible.sync="profileVisible" width="550px" :append-to-body="true" :close-on-click-modal="false" custom-class="profile-dialog">
      <el-form :model="currentUser" label-width="100px">
        <el-form-item label="用户头像">
          <el-upload
              class="avatar-uploader"
              :action="uploadActionUrl"
              :show-file-list="false"
              :on-success="handleAvatarSuccess"
              :before-upload="beforeAvatarUpload"
              name="file">
            <img v-if="currentUser.avatar" :src="getFileUrl(currentUser.avatar)" class="avatar">
            <i v-else class="el-icon-plus avatar-uploader-icon"></i>
          </el-upload>
        </el-form-item>
        <el-form-item label="用户账号">
          <el-input v-model="currentUser.userName" disabled></el-input>
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="currentUser.name" placeholder="请输入姓名"></el-input>
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="currentUser.phone" placeholder="请输入联系电话"></el-input>
        </el-form-item>
        <el-form-item label="联系地址">
          <el-input type="textarea" v-model="currentUser.address" placeholder="请输入地址"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="profileVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveProfile">保存修改</el-button>
      </div>
    </el-dialog>

  </div>
</template>

<style scoped>
/* Logo 区域优化 */
.logo-icon-bg {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  margin-right: 12px;
  font-size: 18px;
  box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
}

/* 用户信息卡片化 */
.user-profile-card {
  display: flex;
  align-items: center;
  background-color: transparent;
  padding: 6px 12px;
  border-radius: 30px;
  transition: background-color 0.3s;
  cursor: pointer;
}

.user-profile-card:hover {
  background-color: rgba(0,0,0,0.03);
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  margin-right: 12px;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  object-fit: cover;
}

.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.user-info .name {
  font-size: 14px;
  font-weight: 700;
  color: #2d3748;
}

.user-info .role {
  font-size: 12px;
  color: #10b981; /* 在线状态绿 */
}

/* 上传头像样式 */
.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 12px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}
.avatar-uploader .el-upload:hover {
  border-color: #667eea;
  background-color: rgba(102, 126, 234, 0.05);
}
.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
}
.avatar {
  width: 100px;
  height: 100px;
  display: block;
  border-radius: 12px;
}

/* client/src/components/nav.vue - <style scoped> */

/* Logo 区域整体布局优化 */
.fater-header-logo {
  display: flex;
  align-items: center;
  /* 移除之前的文字渐变，改用深色实色，显得更稳重官方 */
  /* background: var(--primary-gradient); */
  /* -webkit-background-clip: text; */
  /* -webkit-text-fill-color: transparent; */
  color: var(--text-main);
  text-shadow: none; /* 移除之前的阴影 */
}

/* --- 新增：校徽图片样式 --- */
.school-logo-img {
  /* 高度根据实际校徽形状微调，通常 40px-50px 比较合适 */
  height: 48px;
  width: auto; /* 保持原始比例 */
  margin-right: 15px; /* 图片和文字的间距 */
  /* 加一点微弱的投影让Logo更立体 */
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.08));
  transition: all 0.3s ease;
}
.school-logo-img:hover {
  transform: scale(1.05) rotate(-2deg); /* 鼠标悬停时微微动一下，增加趣味性 */
}

/* --- 新增：文字组样式 --- */
.brand-text-group {
  display: flex;
  flex-direction: column; /* 文字上下排列 */
  justify-content: center;
  line-height: 1.1; /* 紧凑一点 */
}

.brand-main-text {
  font-size: 20px;
  font-weight: 800;
  color: #2d3748; /* 深灰黑色 */
  letter-spacing: 1px;
}

.brand-sub-text {
  font-size: 11px;
  font-weight: 500;
  color: #a0aec0; /* 浅灰色 */
  text-transform: uppercase; /* 全大写英文 */
  letter-spacing: 1px;
  margin-top: 2px;
}

/* --- 原有样式删除提醒 --- */
/* 请确保删除了原来的 .logo-icon-bg 样式，否则可能会有冲突 */
/*
.logo-icon-bg {
   display: none;
}
*/
</style>

<script>
// JS 逻辑保持不变
import { updateUserInfo } from "../api/index.js";

const API_BASE_URL = "http://localhost:9999/teams";

export default {
  data() {
    return {
      profileVisible: false,
      currentUser: {},
      uploadActionUrl: API_BASE_URL + "/files/upload",
    };
  },
  computed: {
    userAvatarUrl() {
      const users = this.$store.state.users;
      if (users && users.avatar) {
        return API_BASE_URL + "/files/" + users.avatar;
      }
      return "";
    }
  },
  methods: {
    handleCommand(command) {
      if (command === 'logout') {
        this.exit();
      } else if (command === 'profile') {
        this.openProfile();
      }
    },
    exit() {
      this.$confirm('确定要退出登录吗?', '系统提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        sessionStorage.removeItem("token");
        this.$store.commit("setToken", null);
        this.$store.commit("setMenus", null);
        this.$store.commit("setUsers", {});
        this.$router.push("/");
      }).catch(() => {});
    },
    openProfile() {
      if (this.$store.state.users) {
        this.currentUser = JSON.parse(JSON.stringify(this.$store.state.users));
      } else {
        this.currentUser = {};
      }
      this.profileVisible = true;
    },
    beforeAvatarUpload(file) {
      const isJPG = file.type === 'image/jpeg' || file.type === 'image/png';
      const isLt2M = file.size / 1024 / 1024 < 2;
      if (!isJPG) this.$message.error('上传头像图片只能是 JPG/PNG 格式!');
      if (!isLt2M) this.$message.error('上传头像图片大小不能超过 2MB!');
      return isJPG && isLt2M;
    },
    handleAvatarSuccess(res) {
      if (res.code === 0) {
        this.$set(this.currentUser, 'avatar', res.data);
        this.$message.success('头像上传成功');
      } else {
        this.$message.error(res.msg || '上传失败');
      }
    },
    saveProfile() {
      updateUserInfo(this.currentUser).then(res => {
        if (res.code === 0) {
          this.$message.success("修改成功");
          const updatedUser = { ...this.$store.state.users, ...this.currentUser };
          this.$store.commit("setUsers", updatedUser);
          this.profileVisible = false;
        } else {
          this.$message.error(res.msg);
        }
      });
    },
    getFileUrl(fileName) {
      if (!fileName) return '';
      return API_BASE_URL + "/files/" + fileName;
    }
  }
};
</script>