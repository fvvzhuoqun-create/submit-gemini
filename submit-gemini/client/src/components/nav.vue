<template>
  <div class="fater-header">
    <div class="fater-header-logo">
      <i class="fa fa-users" style="margin-right: 10px;"></i>
      校园社团管理系统
    </div>

    <div class="fater-header-user">
      <el-dropdown @command="handleCommand" trigger="click">
        <div class="el-dropdown-link user-info-inner">
          <el-avatar
              :size="36"
              :src="userAvatarUrl"
              icon="el-icon-user-solid"
              class="header-avatar"
              shape="square"
          ></el-avatar>
          <span class="username">{{ this.$store.state.users.name || '用户' }}</span>
          <i class="el-icon-arrow-down el-icon--right"></i>
        </div>
        <el-dropdown-menu slot="dropdown">
          <el-dropdown-item command="profile" icon="el-icon-user">个人中心</el-dropdown-item>
          <el-dropdown-item command="logout" icon="el-icon-switch-button" divided>退出登录</el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
    </div>

    <el-dialog title="个人信息设置" :visible.sync="profileVisible" width="550px" :append-to-body="true" :close-on-click-modal="false">
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
          <div style="font-size: 12px; color: #999; line-height: 1.5; margin-top: 5px;">
            点击上方框图上传新头像，支持 JPG/PNG 格式，大小不超过 2MB
          </div>
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

<script>
import { updateUserInfo } from "../api/index.js";

// 后端服务的基础地址，用于拼接图片路径和上传地址
// 请根据你的 SpringBoot 项目实际端口修改，通常是 8080 或 8888
const API_BASE_URL = "http://localhost:8080";

export default {
  data() {
    return {
      profileVisible: false,
      currentUser: {}, // 用于编辑的用户信息副本
      uploadActionUrl: API_BASE_URL + "/files/upload", // 上传接口地址
    };
  },
  computed: {
    // 计算属性：获取当前登录用户的头像URL
    userAvatarUrl() {
      const avatar = this.$store.state.users.avatar;
      if (avatar) {
        return API_BASE_URL + "/files/" + avatar;
      }
      return ""; // 返回空字符串将显示 el-avatar 的默认图标
    }
  },
  methods: {
    // 菜单指令处理
    handleCommand(command) {
      if (command === 'logout') {
        this.exit();
      } else if (command === 'profile') {
        this.openProfile();
      }
    },
    // 退出登录
    exit() {
      this.$confirm('确定要退出登录吗?', '系统提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        sessionStorage.removeItem("token");
        this.$store.commit("setToken", null);
        this.$router.push("/");
      }).catch(() => {});
    },
    // 打开个人中心，深拷贝用户信息防止直接修改 Vuex
    openProfile() {
      this.currentUser = JSON.parse(JSON.stringify(this.$store.state.users));
      this.profileVisible = true;
    },
    // 图片上传前的校验
    beforeAvatarUpload(file) {
      const isJPG = file.type === 'image/jpeg' || file.type === 'image/png';
      const isLt2M = file.size / 1024 / 1024 < 2;

      if (!isJPG) {
        this.$message.error('上传头像图片只能是 JPG/PNG 格式!');
      }
      if (!isLt2M) {
        this.$message.error('上传头像图片大小不能超过 2MB!');
      }
      return isJPG && isLt2M;
    },
    // 上传成功回调
    handleAvatarSuccess(res) {
      if (res.code === 0) {
        // res.data 应该是后端返回的文件名
        this.$set(this.currentUser, 'avatar', res.data);
        this.$message.success('头像上传成功');
      } else {
        this.$message.error(res.msg || '上传失败');
      }
    },
    // 保存个人信息修改
    saveProfile() {
      updateUserInfo(this.currentUser).then(res => {
        if (res.code === 0) {
          this.$message.success("修改成功");
          // 更新 Vuex 中的用户信息（注意：规范做法应在 store 中定义 mutation）
          // 这里为了简便直接修改 state，确保界面即时刷新
          Object.assign(this.$store.state.users, this.currentUser);
          this.profileVisible = false;
        } else {
          this.$message.error(res.msg);
        }
      });
    },
    // 获取图片完整访问路径
    getFileUrl(fileName) {
      if (!fileName) return '';
      return API_BASE_URL + "/files/" + fileName;
    }
  }
};
</script>

<style scoped>
/* 顶部导航栏整体布局 */
.fater-header {
  position: fixed;
  left: 0;
  right: 0;
  top: 0;
  height: 60px;
  line-height: 60px;
  background-color: #ffffff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 1000;
  padding: 0 24px;
  display: flex;
  justify-content: space-between; /* 左右两端对齐 */
  align-items: center;
}

.fater-header-logo {
  font-size: 20px;
  font-weight: 700;
  color: #009999;
  display: flex;
  align-items: center;
}

/* 顶部右侧用户信息区容器 */
.fater-header-user {
  display: flex;
  align-items: center;
}

/* 用户信息内部样式（鼠标悬停效果） */
.user-info-inner {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info-inner:hover {
  background-color: rgba(0, 0, 0, 0.025);
}

.header-avatar {
  margin-right: 8px;
  background-color: #009999; /* 默认头像背景色 */
}

.username {
  font-size: 14px;
  color: #606266;
  margin-right: 4px;
  font-weight: 500;
}

/* ------------------- 上传组件样式 ------------------- */
.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}

.avatar-uploader .el-upload:hover {
  border-color: #009999;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
  border: 1px dashed #c0ccda; /* 显式的虚线边框 */
  border-radius: 6px;
}

.avatar {
  width: 100px;
  height: 100px;
  display: block;
  border-radius: 6px;
  object-fit: cover;
}
</style>