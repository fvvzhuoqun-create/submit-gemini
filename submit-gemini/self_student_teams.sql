/*
 Navicat Premium Data Transfer

 Source Server         : root
 Source Server Type    : MySQL
 Source Server Version : 80040
 Source Host           : localhost:3306
 Source Schema         : self_student_teams

 Target Server Type    : MySQL
 Target Server Version : 80040
 File Encoding         : 65001

 Date: 22/12/2025 16:06:49
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for active_logs
-- ----------------------------
DROP TABLE IF EXISTS `active_logs`;
CREATE TABLE `active_logs`  (
  `id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '记录ID',
  `create_time` char(19) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '报名时间',
  `active_id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '活动编号',
  `user_id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '报名用户',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `active_id`(`active_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `active_logs_ibfk_1` FOREIGN KEY (`active_id`) REFERENCES `activities` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `active_logs_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci COMMENT = '报名记录' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of active_logs
-- ----------------------------
INSERT INTO `active_logs` VALUES ('1764591560890', '2025-12-01 20:19:20', '1764591560882', '1642422100001');
INSERT INTO `active_logs` VALUES ('1764591599573', '2025-12-01 20:19:59', '1764591560882', '1764591265109');
INSERT INTO `active_logs` VALUES ('1764591697842', '2025-12-01 20:21:37', '1764591697835', '1642422100001');

-- ----------------------------
-- Table structure for activities
-- ----------------------------
DROP TABLE IF EXISTS `activities`;
CREATE TABLE `activities`  (
  `id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '记录ID',
  `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '活动名称',
  `comm` varchar(60) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '活动概述',
  `detail` varchar(256) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '活动详情',
  `ask` varchar(125) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '活动要求',
  `total` int(0) NOT NULL COMMENT '报名人数',
  `active_time` char(19) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '活动时间',
  `team_id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '发布社团',
  `media_file` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL COMMENT '活动图片或视频',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `team_id`(`team_id`) USING BTREE,
  CONSTRAINT `activities_ibfk_1` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci COMMENT = '活动信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of activities
-- ----------------------------
INSERT INTO `activities` VALUES ('1764591560882', 'test', 'test', 'test', 'test', 3, '2025-12-03 00:00:00', '1672148926602', NULL);
INSERT INTO `activities` VALUES ('1764591697835', 'test', 'test', 'test', 'test', 1, '2025-12-03 00:00:00', '1672148926602', NULL);

-- ----------------------------
-- Table structure for apply_logs
-- ----------------------------
DROP TABLE IF EXISTS `apply_logs`;
CREATE TABLE `apply_logs`  (
  `id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '记录ID',
  `status` int(0) NOT NULL COMMENT '处理状态',
  `create_time` char(19) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '申请时间',
  `team_id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '申请社团',
  `user_id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '申请用户',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `team_id`(`team_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `apply_logs_ibfk_1` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `apply_logs_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci COMMENT = '申请记录' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of apply_logs
-- ----------------------------
INSERT INTO `apply_logs` VALUES ('1764591276499', 1, '2025-12-01 20:14:36', '1672148926602', '1764591265109');
INSERT INTO `apply_logs` VALUES ('1764591278790', 1, '2025-12-01 20:14:38', '1642422100000', '1764591265109');
INSERT INTO `apply_logs` VALUES ('1764591358730', 1, '2025-12-01 20:15:58', '1672148926602', '1764591265109');
INSERT INTO `apply_logs` VALUES ('1764591361210', 1, '2025-12-01 20:16:01', '1642422100000', '1764591265109');
INSERT INTO `apply_logs` VALUES ('1764592780017', 1, '2025-12-01 20:39:40', '1764591471519', '1764591308809');

-- ----------------------------
-- Table structure for members
-- ----------------------------
DROP TABLE IF EXISTS `members`;
CREATE TABLE `members`  (
  `id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '记录ID',
  `create_time` char(19) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '入团时间',
  `team_id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '加入社团',
  `user_id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '申请用户',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `team_id`(`team_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `members_ibfk_1` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `members_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci COMMENT = '成员信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of members
-- ----------------------------
INSERT INTO `members` VALUES ('1642422100000', '2022-01-17 20:00:00', '1642422100000', '1642422100001');
INSERT INTO `members` VALUES ('1764591298151', '2025-12-01 20:14:58', '1642422100000', '1764591265109');
INSERT INTO `members` VALUES ('1764591298687', '2025-12-01 20:14:58', '1672148926602', '1764591265109');
INSERT INTO `members` VALUES ('1764591374967', '2025-12-01 20:16:14', '1642422100000', '1764591265109');
INSERT INTO `members` VALUES ('1764591375407', '2025-12-01 20:16:15', '1672148926602', '1764591265109');
INSERT INTO `members` VALUES ('1764591471526', '2025-12-01 20:17:51', '1764591471519', '1764591265109');
INSERT INTO `members` VALUES ('1764592787623', '2025-12-01 20:39:47', '1764591471519', '1764591308809');

-- ----------------------------
-- Table structure for notices
-- ----------------------------
DROP TABLE IF EXISTS `notices`;
CREATE TABLE `notices`  (
  `id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '记录ID',
  `title` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '通知标题',
  `detail` varchar(125) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '通知详情',
  `create_time` char(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '发布时间',
  `team_id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL COMMENT '发布社团',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci COMMENT = '通知记录' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of notices
-- ----------------------------
INSERT INTO `notices` VALUES ('1672148823844', 'test', '测试', '2022-12-27', NULL);

-- ----------------------------
-- Table structure for pay_logs
-- ----------------------------
DROP TABLE IF EXISTS `pay_logs`;
CREATE TABLE `pay_logs`  (
  `id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '记录ID',
  `create_time` char(19) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '缴费时间',
  `total` double NOT NULL COMMENT '缴纳费用',
  `team_id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '收费社团',
  `user_id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '缴费用户',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `team_id`(`team_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `pay_logs_ibfk_1` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `pay_logs_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci COMMENT = '缴费记录' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for team_types
-- ----------------------------
DROP TABLE IF EXISTS `team_types`;
CREATE TABLE `team_types`  (
  `id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '记录ID',
  `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '类型名称',
  `create_time` char(19) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci COMMENT = '社团类型' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of team_types
-- ----------------------------
INSERT INTO `team_types` VALUES ('1642422100000', '科技创新', '2022-01-17 20:00:00');
INSERT INTO `team_types` VALUES ('1642422100001', '户外运动', '2022-01-17 20:00:00');
INSERT INTO `team_types` VALUES ('1642422100002', '语言文学', '2022-01-17 20:00:00');
INSERT INTO `team_types` VALUES ('1642422100003', '志愿服务', '2022-01-17 20:00:00');

-- ----------------------------
-- Table structure for teams
-- ----------------------------
DROP TABLE IF EXISTS `teams`;
CREATE TABLE `teams`  (
  `id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '记录ID',
  `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '社团名称',
  `create_time` char(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '建立时间',
  `total` int(0) NOT NULL COMMENT '社团人数',
  `manager` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '社团团长',
  `type_id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '社团编号',
  `cooldown` int(0) NULL DEFAULT 7 COMMENT '申请冷静期(天)',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `type_id`(`type_id`) USING BTREE,
  CONSTRAINT `teams_ibfk_1` FOREIGN KEY (`type_id`) REFERENCES `team_types` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci COMMENT = '社团信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of teams
-- ----------------------------
INSERT INTO `teams` VALUES ('1642422100000', '网络攻防', '2022-01-17', 3, '1642422100001', '1642422100000', 7);
INSERT INTO `teams` VALUES ('1672148926602', '星空漫画', '2022-12-27', 2, '1642422100001', '1642422100002', 7);
INSERT INTO `teams` VALUES ('1764591471519', '123', '2025-12-01', 2, '1764591265109', '1642422100000', 7);

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` char(13) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '记录ID',
  `user_name` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '用户账号',
  `pass_word` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '用户密码',
  `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL COMMENT '用户姓名',
  `gender` char(2) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL COMMENT '用户性别',
  `age` int(0) NULL DEFAULT NULL COMMENT '用户年龄',
  `phone` char(11) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL COMMENT '联系电话',
  `address` varchar(64) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL COMMENT '联系地址',
  `status` int(0) NOT NULL COMMENT '信息状态',
  `create_time` char(19) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '添加时间',
  `type` int(0) NOT NULL COMMENT '用户身份',
  `avatar` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL COMMENT '用户头像',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci COMMENT = '系统用户' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES ('1642422100000', 'admin', 'admin', '张三', '男', 45, '90989192', '武当十八号', 1, '2022-01-17 20:00:00', 0, 'd346735f-ad26-4bc1-b02a-dfd8413b9767.jpg');
INSERT INTO `users` VALUES ('1642422100001', '123', '123', '李华', '男', 28, '90989193', '武当十九号', 1, '2022-01-17 20:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1672148602348', '222', '123', '哈哈哈哈', '男', 12, '1111', 'dd', 1, '2022-12-27 21:43:22', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1703644000001', 'wangwei', '123456', '王伟', '男', 20, '13800138001', '南苑宿舍3栋201', 1, '2023-12-27 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1703644000002', 'lina', '123456', '李娜', '女', 19, '13900139002', '北苑宿舍5栋305', 1, '2023-12-27 10:05:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1703644000003', 'zhangmin', '123456', '张敏', '女', 21, '13700137003', '东苑宿舍1栋102', 1, '2023-12-27 11:30:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1703644000004', 'liuqiang', '123456', '刘强', '男', 22, '13600136004', '西苑宿舍4栋404', 1, '2023-12-28 09:15:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1703644000005', 'chenjing', '123456', '陈静', '女', 20, '13500135005', '南苑宿舍2栋606', 1, '2023-12-28 14:20:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1703644000006', 'yangyang', '123456', '杨洋', '男', 19, '13400134006', '北苑宿舍6栋502', 1, '2023-12-29 08:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1703644000007', 'zhaojun', '123456', '赵军', '男', 23, '13300133007', '校外公寓A座', 1, '2023-12-29 16:45:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1703644000008', 'huangting', '123456', '黄婷', '女', 18, '13200132008', '东苑宿舍3栋202', 1, '2023-12-30 11:10:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1703644000009', 'zhoujie', '123456', '周杰', '男', 21, '13100131009', '西苑宿舍1栋303', 1, '2023-12-30 13:20:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1703644000010', 'wulan', '123456', '吴兰', '女', 20, '13000130010', '南苑宿舍5栋101', 1, '2023-12-31 09:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1764591265109', '1234', '123', '李狗蛋', '男', 2, '1234', '1', 1, '2025-12-01 20:14:25', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1764591308809', '12345', '123', '', '', NULL, '', '', 1, '2025-12-01 20:15:08', 2, 'yonghu.jpg');

SET FOREIGN_KEY_CHECKS = 1;
