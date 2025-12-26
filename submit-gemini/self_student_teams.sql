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

 Date: 23/12/2025 20:50:00
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
INSERT INTO `teams` VALUES ('1767226600000', '极客社', '2026-01-01', 43, '1767225600020', '1642422100000', 7);
INSERT INTO `teams` VALUES ('1767226600100', '飞跃协会', '2026-01-01', 18, '1767225602590', '1642422100001', 7);
INSERT INTO `teams` VALUES ('1767226600200', '星火俱乐部', '2026-01-01', 50, '1767225602620', '1642422100002', 7);
INSERT INTO `teams` VALUES ('1767226600300', '蓝天小队', '2026-01-01', 28, '1767225600060', '1642422100003', 7);
INSERT INTO `teams` VALUES ('1767226600400', '绿野社', '2026-01-01', 40, '1767225601370', '1642422100000', 7);
INSERT INTO `teams` VALUES ('1767226600500', '晨曦协会', '2026-01-01', 31, '1767225601420', '1642422100001', 7);
INSERT INTO `teams` VALUES ('1767226600600', '追风俱乐部', '2026-01-01', 22, '1767225602720', '1642422100002', 7);
INSERT INTO `teams` VALUES ('1767226600700', '探索小队', '2026-01-01', 6, '1767225600200', '1642422100003', 7);
INSERT INTO `teams` VALUES ('1767226600800', '知行社', '2026-01-01', 19, '1767225602770', '1642422100000', 7);
INSERT INTO `teams` VALUES ('1767226600900', '墨香协会', '2026-01-01', 34, '1767225601700', '1642422100001', 7);
INSERT INTO `teams` VALUES ('1767226601000', '爱心俱乐部', '2026-01-01', 40, '1767225600460', '1642422100002', 7);
INSERT INTO `teams` VALUES ('1767226601100', '辩论小队', '2026-01-01', 15, '1767225601750', '1642422100003', 7);
INSERT INTO `teams` VALUES ('1767226601200', '摄影社', '2026-01-01', 30, '1767225601930', '1642422100000', 7);
INSERT INTO `teams` VALUES ('1767226601300', '动漫协会', '2026-01-01', 41, '1767225601980', '1642422100001', 7);
INSERT INTO `teams` VALUES ('1767226601400', '电竞俱乐部', '2026-01-01', 35, '1767225600770', '1642422100002', 7);
INSERT INTO `teams` VALUES ('1767226601500', '吉他小队', '2026-01-01', 5, '1767225600810', '1642422100003', 7);
INSERT INTO `teams` VALUES ('1767226601600', '街舞社', '2026-01-01', 41, '1767225600890', '1642422100000', 7);
INSERT INTO `teams` VALUES ('1767226601700', '轮滑协会', '2026-01-01', 34, '1767225600930', '1642422100001', 7);
INSERT INTO `teams` VALUES ('1767226601800', '书法俱乐部', '2026-01-01', 5, '1767225601220', '1642422100002', 7);
INSERT INTO `teams` VALUES ('1767226601900', '绘画小队', '2026-01-01', 16, '1767225601260', '1642422100003', 7);

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
INSERT INTO `users` VALUES ('1767225600000', 'user1', '123', '周军强', '男', 18, '13468283449', '宿舍9栋109', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600010', 'user2', '123', '冯俊', '女', 23, '13526846714', '宿舍14栋231', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600020', 'user3', '123', '吕福', '男', 18, '13124901325', '宿舍7栋400', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600030', 'user4', '123', '吕军兴', '男', 22, '13767952979', '宿舍14栋388', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600040', 'user5', '123', '赵文勇', '女', 24, '13828361524', '宿舍1栋130', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600050', 'user6', '123', '姜伟', '女', 24, '13393345318', '宿舍5栋220', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600060', 'user7', '123', '陶健元', '女', 19, '13521561102', '宿舍13栋219', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600070', 'user8', '123', '尤生波', '男', 18, '13197642075', '宿舍6栋308', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600080', 'user9', '123', '冯永刚', '男', 24, '13146180848', '宿舍15栋142', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600090', 'user10', '123', '褚波', '男', 22, '13888389631', '宿舍3栋193', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600100', 'user11', '123', '魏永', '女', 18, '13695028118', '宿舍5栋526', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600110', 'user12', '123', '冯俊', '男', 24, '13759169561', '宿舍6栋204', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600120', 'user13', '123', '杨龙永', '女', 25, '13538345758', '宿舍7栋533', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600130', 'user14', '123', '何刚明', '男', 24, '13532680760', '宿舍2栋402', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600140', 'user15', '123', '韩辉', '女', 19, '13580347909', '宿舍19栋133', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600150', 'user16', '123', '魏明生', '女', 22, '13222670866', '宿舍15栋204', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600160', 'user17', '123', '孙全', '男', 19, '13038755882', '宿舍18栋415', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600170', 'user18', '123', '孙强文', '男', 22, '13449833871', '宿舍14栋245', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600180', 'user19', '123', '华辉', '男', 22, '13193004603', '宿舍16栋535', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600190', 'user20', '123', '陈龙文', '女', 24, '13173863493', '宿舍5栋133', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600200', 'user21', '123', '杨良', '男', 20, '13928216032', '宿舍3栋312', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600210', 'user22', '123', '严福', '男', 18, '13749354297', '宿舍2栋414', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600220', 'user23', '123', '孔贵', '女', 25, '13390259909', '宿舍7栋602', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600230', 'user24', '123', '秦永', '男', 24, '13214171230', '宿舍11栋347', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600240', 'user25', '123', '严兴东', '男', 23, '13558358235', '宿舍7栋521', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600250', 'user26', '123', '施福峰', '男', 18, '13722274731', '宿舍20栋382', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600260', 'user27', '123', '杨保', '男', 18, '13777390579', '宿舍1栋249', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600270', 'user28', '123', '何龙', '男', 19, '13027969514', '宿舍17栋478', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600280', 'user29', '123', '姜海', '男', 22, '13290524222', '宿舍2栋505', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600290', 'user30', '123', '曹兴', '男', 18, '13056884547', '宿舍12栋458', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600300', 'user31', '123', '魏龙良', '女', 24, '13653466402', '宿舍8栋257', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600310', 'user32', '123', '张保世', '女', 18, '13052196749', '宿舍18栋386', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600320', 'user33', '123', '李毅生', '男', 21, '13024511355', '宿舍17栋246', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600330', 'user34', '123', '李军辉', '女', 18, '13177210668', '宿舍19栋191', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600340', 'user35', '123', '卫仁海', '男', 19, '13650561243', '宿舍6栋278', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600350', 'user36', '123', '金仁全', '男', 18, '13062419274', '宿舍17栋467', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600360', 'user37', '123', '褚文健', '男', 18, '13627094712', '宿舍15栋277', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600370', 'user38', '123', '魏志志', '男', 23, '13634040551', '宿舍12栋113', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600380', 'user39', '123', '李宁文', '女', 19, '13114182154', '宿舍9栋332', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600390', 'user40', '123', '赵永', '女', 24, '13979518409', '宿舍15栋113', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600400', 'user41', '123', '何伟勇', '女', 23, '13020533496', '宿舍13栋109', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600410', 'user42', '123', '曹义', '女', 18, '13323022461', '宿舍11栋275', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600420', 'user43', '123', '尤刚生', '女', 25, '13964987068', '宿舍19栋447', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600430', 'user44', '123', '朱志', '女', 25, '13493943362', '宿舍20栋105', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600440', 'user45', '123', '华俊东', '女', 25, '13181147162', '宿舍10栋128', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600450', 'user46', '123', '吴山仁', '女', 24, '13746210186', '宿舍5栋232', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600460', 'user47', '123', '沈俊', '女', 24, '13545593819', '宿舍13栋269', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600470', 'user48', '123', '钱海勇', '女', 23, '13195796214', '宿舍11栋381', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600480', 'user49', '123', '冯良', '男', 18, '13232748826', '宿舍14栋391', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600490', 'user50', '123', '华广', '男', 24, '13789358142', '宿舍7栋428', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600500', 'user51', '123', '王宁', '女', 19, '13313912306', '宿舍11栋562', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600510', 'user52', '123', '金勇文', '女', 24, '13515743482', '宿舍11栋424', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600520', 'user53', '123', '尤志', '男', 25, '13981592915', '宿舍14栋518', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600530', 'user54', '123', '金海', '女', 21, '13578815099', '宿舍10栋252', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600540', 'user55', '123', '赵志仁', '男', 19, '13638120379', '宿舍18栋410', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600550', 'user56', '123', '何强', '女', 19, '13191552786', '宿舍20栋149', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600560', 'user57', '123', '尤宁仁', '女', 19, '13197220728', '宿舍1栋526', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600570', 'user58', '123', '卫仁贵', '男', 20, '13878589674', '宿舍13栋490', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600580', 'user59', '123', '朱波', '女', 24, '13331918964', '宿舍12栋203', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600590', 'user60', '123', '郑全永', '女', 18, '13624571576', '宿舍4栋405', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600600', 'user61', '123', '张世', '男', 22, '13699448876', '宿舍20栋397', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600610', 'user62', '123', '曹仁', '男', 19, '13831138205', '宿舍13栋255', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600620', 'user63', '123', '杨明', '男', 23, '13110830055', '宿舍19栋541', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600630', 'user64', '123', '孔健波', '女', 19, '13466888831', '宿舍19栋563', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600640', 'user65', '123', '曹辉明', '女', 18, '13069649823', '宿舍14栋518', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600650', 'user66', '123', '金元龙', '男', 23, '13669048272', '宿舍13栋596', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600660', 'user67', '123', '赵广', '男', 24, '13276319955', '宿舍14栋444', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600670', 'user68', '123', '秦义俊', '女', 23, '13753954658', '宿舍20栋470', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600680', 'user69', '123', '吴世龙', '男', 25, '13683572955', '宿舍13栋181', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600690', 'user70', '123', '陶勇峰', '男', 23, '13194890372', '宿舍2栋418', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600700', 'user71', '123', '陶贵', '男', 25, '13286514599', '宿舍8栋310', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600710', 'user72', '123', '李元', '女', 20, '13457973712', '宿舍10栋162', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600720', 'user73', '123', '郑东', '女', 25, '13575592829', '宿舍11栋232', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600730', 'user74', '123', '严军', '男', 21, '13350731000', '宿舍12栋196', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600740', 'user75', '123', '赵良', '男', 21, '13937605528', '宿舍8栋219', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600750', 'user76', '123', '秦辉', '男', 19, '13837573266', '宿舍8栋115', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600760', 'user77', '123', '许全', '女', 23, '13469728558', '宿舍4栋544', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600770', 'user78', '123', '吴良军', '女', 21, '13667312727', '宿舍12栋490', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600780', 'user79', '123', '姜元强', '男', 19, '13283192205', '宿舍1栋149', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600790', 'user80', '123', '褚军', '女', 18, '13091488632', '宿舍19栋209', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600800', 'user81', '123', '赵永广', '女', 20, '13966635645', '宿舍7栋347', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600810', 'user82', '123', '郑平', '男', 24, '13639715900', '宿舍1栋529', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600820', 'user83', '123', '曹福', '男', 22, '13880326622', '宿舍12栋182', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600830', 'user84', '123', '魏永', '男', 23, '13085427822', '宿舍8栋497', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600840', 'user85', '123', '尤仁生', '女', 19, '13613604502', '宿舍2栋574', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600850', 'user86', '123', '张强仁', '男', 20, '13542181961', '宿舍8栋200', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600860', 'user87', '123', '李平', '女', 22, '13564445182', '宿舍8栋470', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600870', 'user88', '123', '曹永', '男', 20, '13860527391', '宿舍20栋417', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600880', 'user89', '123', '郑永俊', '男', 24, '13797962412', '宿舍9栋202', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600890', 'user90', '123', '吕辉东', '女', 18, '13957235614', '宿舍1栋526', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600900', 'user91', '123', '李志毅', '女', 18, '13264389637', '宿舍14栋587', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600910', 'user92', '123', '吴刚兴', '女', 19, '13060609253', '宿舍13栋489', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600920', 'user93', '123', '褚伟平', '男', 18, '13778607302', '宿舍18栋324', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600930', 'user94', '123', '赵志', '男', 21, '13797393744', '宿舍11栋368', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600940', 'user95', '123', '沈贵', '男', 19, '13869091250', '宿舍18栋168', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600950', 'user96', '123', '韩军东', '女', 19, '13569944977', '宿舍13栋215', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600960', 'user97', '123', '尤军', '女', 20, '13455544324', '宿舍14栋336', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600970', 'user98', '123', '赵东', '男', 25, '13199100859', '宿舍9栋343', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600980', 'user99', '123', '卫明', '男', 18, '13081002901', '宿舍17栋188', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225600990', 'user100', '123', '姜永', '男', 23, '13334289724', '宿舍8栋146', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601000', 'user101', '123', '张山宁', '女', 21, '13892496708', '宿舍15栋351', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601010', 'user102', '123', '魏文', '男', 20, '13891259279', '宿舍9栋404', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601020', 'user103', '123', '吴良健', '女', 24, '13910866716', '宿舍16栋477', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601030', 'user104', '123', '许力', '女', 23, '13114780216', '宿舍18栋546', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601040', 'user105', '123', '陈福', '女', 23, '13423131904', '宿舍4栋550', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601050', 'user106', '123', '蒋峰俊', '男', 21, '13165904358', '宿舍15栋271', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601060', 'user107', '123', '施宁', '女', 19, '13230641881', '宿舍14栋496', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601070', 'user108', '123', '尤贵', '男', 20, '13949514934', '宿舍7栋445', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601080', 'user109', '123', '魏平', '男', 22, '13774373312', '宿舍16栋421', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601090', 'user110', '123', '周永海', '女', 24, '13665879657', '宿舍18栋265', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601100', 'user111', '123', '陈全山', '女', 18, '13889071970', '宿舍2栋373', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601110', 'user112', '123', '褚义', '女', 22, '13627863510', '宿舍7栋411', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601120', 'user113', '123', '蒋义', '女', 18, '13786975818', '宿舍4栋448', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601130', 'user114', '123', '冯义', '男', 21, '13764687095', '宿舍3栋208', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601140', 'user115', '123', '曹波广', '女', 20, '13711383722', '宿舍15栋227', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601150', 'user116', '123', '华龙', '女', 23, '13788540379', '宿舍2栋360', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601160', 'user117', '123', '褚军永', '男', 18, '13878265533', '宿舍5栋396', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601170', 'user118', '123', '钱力', '女', 25, '13340780400', '宿舍13栋132', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601180', 'user119', '123', '蒋福', '男', 18, '13310324886', '宿舍4栋510', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601190', 'user120', '123', '吴军', '女', 23, '13023426234', '宿舍8栋366', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601200', 'user121', '123', '杨元', '女', 18, '13163747682', '宿舍6栋453', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601210', 'user122', '123', '曹峰', '女', 19, '13198295953', '宿舍15栋406', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601220', 'user123', '123', '孔保', '男', 24, '13427455506', '宿舍13栋574', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601230', 'user124', '123', '杨全保', '男', 23, '13293153014', '宿舍8栋349', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601240', 'user125', '123', '杨福宁', '男', 23, '13649229239', '宿舍9栋519', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601250', 'user126', '123', '曹山全', '女', 25, '13665444226', '宿舍19栋132', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601260', 'user127', '123', '赵波宁', '女', 22, '13683301352', '宿舍19栋242', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601270', 'user128', '123', '褚贵勇', '男', 25, '13845725158', '宿舍6栋459', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601280', 'user129', '123', '钱山福', '女', 22, '13928800044', '宿舍5栋584', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601290', 'user130', '123', '华辉', '男', 18, '13458960957', '宿舍2栋575', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601300', 'user131', '123', '孙永生', '男', 25, '13819243068', '宿舍8栋321', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601310', 'user132', '123', '卫文兴', '女', 25, '13968806321', '宿舍11栋270', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601320', 'user133', '123', '周全健', '男', 23, '13423711171', '宿舍8栋376', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601330', 'user134', '123', '姜波俊', '女', 23, '13495750987', '宿舍7栋492', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601340', 'user135', '123', '金波', '男', 19, '13017519391', '宿舍9栋464', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601350', 'user136', '123', '金山', '男', 20, '13865746741', '宿舍4栋385', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601360', 'user137', '123', '孙良', '男', 19, '13850557865', '宿舍13栋234', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601370', 'user138', '123', '张海生', '男', 25, '13188874461', '宿舍18栋370', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601380', 'user139', '123', '吕东俊', '女', 20, '13485451505', '宿舍14栋484', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601390', 'user140', '123', '金仁力', '男', 18, '13835682548', '宿舍10栋272', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601400', 'user141', '123', '杨伟仁', '男', 23, '13933661499', '宿舍2栋407', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601410', 'user142', '123', '郑广强', '女', 19, '13993055343', '宿舍19栋356', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601420', 'user143', '123', '王伟', '男', 18, '13670727753', '宿舍14栋580', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601430', 'user144', '123', '何贵文', '男', 19, '13289244380', '宿舍15栋120', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601440', 'user145', '123', '何波', '女', 20, '13735877963', '宿舍17栋379', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601450', 'user146', '123', '蒋宁义', '男', 18, '13538965991', '宿舍7栋368', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601460', 'user147', '123', '张俊毅', '男', 25, '13119921760', '宿舍1栋266', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601470', 'user148', '123', '许平宁', '男', 19, '13020269256', '宿舍7栋264', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601480', 'user149', '123', '尤军', '女', 21, '13642459594', '宿舍3栋351', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601490', 'user150', '123', '冯强平', '女', 22, '13851164571', '宿舍8栋286', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601500', 'user151', '123', '尤永宁', '男', 22, '13493716160', '宿舍15栋249', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601510', 'user152', '123', '尤义', '男', 18, '13530985687', '宿舍20栋202', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601520', 'user153', '123', '王健', '女', 19, '13468550418', '宿舍6栋339', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601530', 'user154', '123', '冯毅良', '男', 24, '13177369611', '宿舍16栋463', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601540', 'user155', '123', '魏生', '女', 18, '13854459957', '宿舍16栋327', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601550', 'user156', '123', '郑福龙', '男', 19, '13293760767', '宿舍2栋277', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601560', 'user157', '123', '吕良毅', '男', 22, '13186081083', '宿舍13栋323', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601570', 'user158', '123', '李毅', '女', 25, '13547241683', '宿舍9栋201', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601580', 'user159', '123', '尤峰保', '男', 19, '13315989559', '宿舍15栋155', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601590', 'user160', '123', '沈广', '女', 19, '13084318827', '宿舍19栋386', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601600', 'user161', '123', '蒋山俊', '男', 25, '13565572376', '宿舍13栋522', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601610', 'user162', '123', '沈文健', '女', 22, '13113602544', '宿舍14栋400', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601620', 'user163', '123', '金宁', '女', 24, '13256192711', '宿舍2栋454', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601630', 'user164', '123', '陶峰', '女', 19, '13480628856', '宿舍14栋429', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601640', 'user165', '123', '陈辉', '男', 24, '13638688479', '宿舍4栋592', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601650', 'user166', '123', '尤明伟', '女', 25, '13849029049', '宿舍13栋571', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601660', 'user167', '123', '许强', '男', 25, '13882602060', '宿舍10栋410', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601670', 'user168', '123', '吕兴', '男', 19, '13010576347', '宿舍14栋185', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601680', 'user169', '123', '孙永毅', '男', 23, '13862393596', '宿舍18栋395', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601690', 'user170', '123', '沈力强', '男', 22, '13643278032', '宿舍18栋275', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601700', 'user171', '123', '严志', '女', 18, '13676878123', '宿舍8栋489', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601710', 'user172', '123', '杨龙', '女', 20, '13631381589', '宿舍7栋167', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601720', 'user173', '123', '施力平', '女', 18, '13276299302', '宿舍8栋455', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601730', 'user174', '123', '冯伟', '男', 18, '13471831703', '宿舍17栋483', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601740', 'user175', '123', '曹伟', '男', 22, '13882248367', '宿舍19栋427', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601750', 'user176', '123', '周海世', '女', 22, '13190762618', '宿舍13栋355', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601760', 'user177', '123', '华贵刚', '男', 24, '13241237685', '宿舍15栋156', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601770', 'user178', '123', '郑志', '男', 22, '13741061748', '宿舍13栋458', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601780', 'user179', '123', '吕永', '女', 21, '13350840141', '宿舍1栋156', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601790', 'user180', '123', '朱良', '女', 19, '13884488059', '宿舍17栋393', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601800', 'user181', '123', '朱海龙', '男', 23, '13922461313', '宿舍10栋211', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601810', 'user182', '123', '卫刚海', '男', 21, '13687420613', '宿舍13栋586', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601820', 'user183', '123', '沈良保', '女', 23, '13746671749', '宿舍10栋444', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601830', 'user184', '123', '卫毅', '男', 23, '13081765788', '宿舍16栋278', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601840', 'user185', '123', '严福勇', '男', 21, '13620261563', '宿舍14栋313', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601850', 'user186', '123', '秦平伟', '女', 20, '13573073276', '宿舍7栋143', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601860', 'user187', '123', '李广元', '男', 23, '13255510047', '宿舍19栋597', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601870', 'user188', '123', '蒋海兴', '女', 22, '13353960385', '宿舍6栋188', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601880', 'user189', '123', '秦义龙', '女', 19, '13610167318', '宿舍14栋536', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601890', 'user190', '123', '褚东世', '女', 19, '13322745108', '宿舍1栋498', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601900', 'user191', '123', '姜贵', '男', 25, '13179448447', '宿舍13栋126', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601910', 'user192', '123', '曹良', '女', 25, '13657696440', '宿舍14栋548', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601920', 'user193', '123', '周力文', '男', 25, '13697954091', '宿舍9栋391', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601930', 'user194', '123', '卫文波', '男', 19, '13174287563', '宿舍10栋578', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601940', 'user195', '123', '何力', '男', 22, '13569414527', '宿舍3栋328', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601950', 'user196', '123', '韩宁波', '男', 21, '13597442920', '宿舍7栋174', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601960', 'user197', '123', '许军', '男', 24, '13221280507', '宿舍11栋394', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601970', 'user198', '123', '周山', '男', 22, '13467241959', '宿舍7栋470', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601980', 'user199', '123', '韩宁健', '女', 25, '13318045848', '宿舍1栋168', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225601990', 'user200', '123', '严福', '女', 23, '13344419490', '宿舍7栋147', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602000', 'user201', '123', '吕明', '男', 25, '13144420892', '宿舍13栋242', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602010', 'user202', '123', '孔永世', '男', 22, '13518615168', '宿舍1栋530', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602020', 'user203', '123', '张伟山', '女', 25, '13948889068', '宿舍2栋470', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602030', 'user204', '123', '魏辉强', '女', 19, '13512676796', '宿舍10栋352', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602040', 'user205', '123', '尤福勇', '女', 24, '13218829630', '宿舍3栋417', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602050', 'user206', '123', '褚峰', '女', 24, '13334412349', '宿舍3栋300', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602060', 'user207', '123', '吕军明', '女', 23, '13981023037', '宿舍13栋482', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602070', 'user208', '123', '姜波伟', '女', 18, '13416299219', '宿舍14栋360', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602080', 'user209', '123', '吴世', '女', 18, '13655827439', '宿舍17栋562', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602090', 'user210', '123', '蒋广保', '男', 24, '13755413843', '宿舍14栋326', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602100', 'user211', '123', '钱保', '女', 18, '13228669779', '宿舍13栋162', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602110', 'user212', '123', '李峰东', '女', 23, '13988242504', '宿舍20栋200', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602120', 'user213', '123', '孔辉毅', '女', 23, '13492185710', '宿舍5栋339', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602130', 'user214', '123', '曹义龙', '女', 21, '13612504027', '宿舍13栋387', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602140', 'user215', '123', '施兴', '男', 21, '13745736854', '宿舍15栋434', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602150', 'user216', '123', '杨贵福', '男', 22, '13359434766', '宿舍16栋295', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602160', 'user217', '123', '吕广', '女', 21, '13997113692', '宿舍3栋532', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602170', 'user218', '123', '陈力元', '女', 21, '13141213051', '宿舍14栋384', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602180', 'user219', '123', '华义', '男', 24, '13634359941', '宿舍7栋221', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602190', 'user220', '123', '冯世海', '女', 19, '13938829826', '宿舍4栋492', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602200', 'user221', '123', '孙文', '女', 25, '13032100425', '宿舍15栋206', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602210', 'user222', '123', '陈峰', '男', 22, '13810006015', '宿舍18栋141', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602220', 'user223', '123', '魏明', '男', 20, '13440320829', '宿舍17栋145', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602230', 'user224', '123', '郑伟', '男', 20, '13833504048', '宿舍5栋158', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602240', 'user225', '123', '金军', '男', 25, '13041564271', '宿舍17栋247', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602250', 'user226', '123', '韩龙文', '男', 19, '13259429769', '宿舍14栋262', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602260', 'user227', '123', '褚文广', '男', 23, '13372848546', '宿舍18栋346', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602270', 'user228', '123', '严生', '男', 19, '13914717468', '宿舍10栋262', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602280', 'user229', '123', '朱伟良', '男', 24, '13777117817', '宿舍15栋306', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602290', 'user230', '123', '曹明福', '女', 23, '13467448583', '宿舍7栋365', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602300', 'user231', '123', '杨龙宁', '女', 22, '13377276725', '宿舍15栋317', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602310', 'user232', '123', '冯明', '男', 19, '13874671601', '宿舍11栋118', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602320', 'user233', '123', '秦永良', '女', 21, '13690727196', '宿舍18栋348', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602330', 'user234', '123', '郑东', '女', 20, '13328871289', '宿舍9栋494', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602340', 'user235', '123', '秦宁刚', '女', 23, '13464714421', '宿舍1栋259', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602350', 'user236', '123', '赵健', '男', 18, '13749736616', '宿舍18栋291', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602360', 'user237', '123', '杨宁永', '女', 20, '13249888939', '宿舍10栋251', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602370', 'user238', '123', '严广', '女', 23, '13686293178', '宿舍10栋150', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602380', 'user239', '123', '孙勇毅', '女', 20, '13768871489', '宿舍18栋589', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602390', 'user240', '123', '李义辉', '女', 20, '13051006422', '宿舍12栋531', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602400', 'user241', '123', '韩东世', '男', 18, '13315843366', '宿舍11栋191', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602410', 'user242', '123', '朱海福', '女', 20, '13287629866', '宿舍4栋283', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602420', 'user243', '123', '冯龙强', '女', 25, '13378660216', '宿舍4栋512', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602430', 'user244', '123', '秦宁', '男', 19, '13856587729', '宿舍1栋147', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602440', 'user245', '123', '陶波明', '女', 22, '13610492913', '宿舍19栋322', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602450', 'user246', '123', '王毅', '男', 22, '13989935607', '宿舍4栋472', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602460', 'user247', '123', '吴健', '男', 22, '13697838995', '宿舍17栋324', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602470', 'user248', '123', '沈世刚', '女', 24, '13792687969', '宿舍7栋265', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602480', 'user249', '123', '吕军山', '男', 21, '13560668620', '宿舍12栋523', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602490', 'user250', '123', '孙峰', '女', 24, '13633280297', '宿舍14栋434', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602500', 'user251', '123', '陈全全', '女', 19, '13799810988', '宿舍15栋492', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602510', 'user252', '123', '韩广全', '男', 22, '13043026820', '宿舍9栋305', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602520', 'user253', '123', '施世强', '男', 23, '13524652157', '宿舍10栋427', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602530', 'user254', '123', '韩全海', '女', 22, '13564176222', '宿舍19栋126', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602540', 'user255', '123', '朱俊', '男', 21, '13511931966', '宿舍1栋566', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602550', 'user256', '123', '褚刚', '男', 21, '13146734985', '宿舍15栋273', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602560', 'user257', '123', '王军健', '女', 21, '13969644982', '宿舍14栋205', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602570', 'user258', '123', '严永兴', '男', 24, '13819616280', '宿舍16栋145', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602580', 'user259', '123', '严仁', '女', 24, '13074411948', '宿舍15栋208', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602590', 'user260', '123', '许力明', '男', 25, '13527700753', '宿舍1栋303', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602600', 'user261', '123', '朱强俊', '男', 23, '13496224205', '宿舍9栋368', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602610', 'user262', '123', '张山刚', '男', 23, '13488949593', '宿舍8栋221', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602620', 'user263', '123', '严刚兴', '女', 21, '13319964976', '宿舍5栋278', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602630', 'user264', '123', '孙辉永', '女', 24, '13798158180', '宿舍13栋496', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602640', 'user265', '123', '吕明勇', '女', 22, '13082487863', '宿舍6栋131', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602650', 'user266', '123', '韩波明', '男', 19, '13552421735', '宿舍1栋286', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602660', 'user267', '123', '张俊波', '男', 25, '13630405673', '宿舍16栋148', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602670', 'user268', '123', '朱强福', '男', 18, '13145108517', '宿舍6栋118', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602680', 'user269', '123', '吕元志', '男', 23, '13176174417', '宿舍2栋197', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602690', 'user270', '123', '吕伟义', '女', 23, '13311427903', '宿舍17栋102', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602700', 'user271', '123', '施宁', '女', 19, '13499742828', '宿舍4栋578', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602710', 'user272', '123', '冯俊', '女', 24, '13084035216', '宿舍8栋210', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602720', 'user273', '123', '孔东', '女', 23, '13796621825', '宿舍1栋348', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602730', 'user274', '123', '张俊', '女', 24, '13231403629', '宿舍15栋544', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602740', 'user275', '123', '杨福全', '女', 18, '13361741089', '宿舍12栋409', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602750', 'user276', '123', '韩福', '男', 20, '13772427524', '宿舍3栋426', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602760', 'user277', '123', '施海刚', '男', 23, '13378566530', '宿舍14栋515', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602770', 'user278', '123', '郑东', '男', 18, '13149437109', '宿舍8栋331', 1, '2026-01-01 10:00:00', 1, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602780', 'user279', '123', '冯健志', '男', 18, '13849102956', '宿舍17栋390', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602790', 'user280', '123', '何兴', '男', 20, '13330482554', '宿舍6栋145', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602800', 'user281', '123', '周勇贵', '女', 19, '13633034363', '宿舍3栋425', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602810', 'user282', '123', '钱力勇', '男', 21, '13536633639', '宿舍10栋250', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602820', 'user283', '123', '杨平力', '男', 18, '13683551730', '宿舍11栋313', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602830', 'user284', '123', '尤广', '女', 19, '13784093176', '宿舍2栋536', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602840', 'user285', '123', '钱强俊', '女', 24, '13490578444', '宿舍4栋170', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602850', 'user286', '123', '姜全', '男', 19, '13995072809', '宿舍3栋322', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602860', 'user287', '123', '严生', '女', 25, '13635816056', '宿舍6栋164', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602870', 'user288', '123', '卫良', '女', 23, '13438141910', '宿舍7栋240', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602880', 'user289', '123', '吕仁', '男', 25, '13989170094', '宿舍2栋540', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602890', 'user290', '123', '陶生', '男', 22, '13483028480', '宿舍20栋362', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602900', 'user291', '123', '吕伟', '女', 21, '13289908318', '宿舍17栋186', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602910', 'user292', '123', '冯永', '女', 22, '13250419477', '宿舍2栋303', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602920', 'user293', '123', '陶贵志', '男', 24, '13497639339', '宿舍7栋491', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602930', 'user294', '123', '严仁辉', '男', 18, '13727725536', '宿舍6栋320', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602940', 'user295', '123', '姜兴', '男', 25, '13597006942', '宿舍8栋562', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602950', 'user296', '123', '王贵文', '女', 25, '13331048433', '宿舍3栋597', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602960', 'user297', '123', '沈山仁', '女', 24, '13531826110', '宿舍8栋144', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602970', 'user298', '123', '施山', '男', 18, '13775523439', '宿舍6栋519', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602980', 'user299', '123', '吕强', '女', 18, '13365873392', '宿舍7栋112', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');
INSERT INTO `users` VALUES ('1767225602990', 'user300', '123', '曹辉平', '男', 19, '13267851082', '宿舍18栋395', 1, '2026-01-01 10:00:00', 2, 'yonghu.jpg');

SET FOREIGN_KEY_CHECKS = 1;
